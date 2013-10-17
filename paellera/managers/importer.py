import os
from datetime import datetime, timedelta
from zipfile import ZipFile
from StringIO import StringIO
import csv
from io import BytesIO

import transaction
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc
from sqlalchemy import func

from paellera.models.sitecontent import SiteText

from paellera.models.pmodels import ArchiveKey
from paellera.models.pmodels import Suite, AptSource, SuiteAptSource
from paellera.models.pmodels import DefaultVariable

from paellera.models.pmodels import BaseTrait, Trait, TraitParent
from paellera.models.pmodels import TraitPackage, TraitVariable
from paellera.models.pmodels import TraitTemplate, TraitScript

from paellera.models.pmodels import Family, FamilyParent, FamilyVariable

from paellera.models.pmodels import Profile, ProfileTrait
from paellera.models.pmodels import ProfileFamily, ProfileVariable

from paellera.models.pmodels import DiskConfig, Kernel, Machine
from paellera.models.pmodels import MachineParent, MachineFamily
from paellera.models.pmodels import MachineVariable, MachineScript

from .util import Gpg

class NoParentError(Exception):
    pass


class TraitImporter(object):
    def __init__(self, session):
        self.session = session
        self.parsed = None

    def import_trait(self, suite_id, trait):
        name = trait['name']
        btraits = self.session.query(BaseTrait).filter_by(name=name).all()
        if not btraits:
            with transaction.manager:
                bt = BaseTrait()
                bt.name = name
                self.session.add(bt)
            bt = self.session.merge(bt)
        else:
            bt = btraits.pop()
            if btraits:
                raise RuntimeError, "bad database"
        q = self.session.query(Trait)
        q = q.filter_by(suite_id=suite_id)
        basequery = q.filter(BaseTrait.id == Trait.trait_id)
        parents_exist = True
        for parent in trait['parents']:
            pq = basequery.filter(BaseTrait.name == parent)
            try:
                pq.one()
            except NoResultFound:
                raise NoParentError, "%s doesn't exist" % parent
        with transaction.manager:
            dbobjs = list()
            t = Trait()
            t.name = name
            t.suite_id = suite_id
            t.trait_id = bt.id
            t.description = trait['description']
            self.session.add(t)
            t = self.session.merge(t)
            for parent in trait['parents']:
                tp = TraitParent()
                tp.trait_id = t.id
                p = basequery.filter(BaseTrait.name == parent).one()
                tp.parent_id = p.id
                self.session.add(tp)
            for pkg, action in trait['packages']:
                tp = TraitPackage()
                tp.trait_id = t.id
                tp.package = pkg
                tp.action = action
                self.session.add(tp)
            for trt, name, value in trait['variables']:
                if trt != t.name:
                    import pdb ; pdb.set_trace()
                    raise RuntimeError, 'bad data'
                tv = TraitVariable()
                tv.trait_id = t.id
                tv.name = name
                tv.value = value
                self.session.add(tv)
            for tdata in trait['templates']:
                tt = TraitTemplate()
                tt.trait_id = t.id
                tt.name = tdata['template']
                for f in ['owner', 'group', 'mode', 'content']:
                    setattr(tt, f, tdata[f])
                self.session.add(tt)
            for name, content in trait['scripts']:
                ts = TraitScript()
                ts.trait_id = t.id
                ts.name = name
                ts.content = content
                self.session.add(ts)
                
                
                
    
class SuiteImporter(object):
    def __init__(self, session):
        self.session = session
        self.parsed = None
        self.traits = TraitImporter(self.session)
        
    def import_suite(self, suite):
        name = suite['name']
        os = suite['os']
        with transaction.manager:
            dbobjs = list()
            s = Suite()
            s.name = name
            s.os = os
            self.session.add(s)
            dbobjs.append(s)
        s = self.session.merge(s)
        with transaction.manager:
            for aptsource in suite['apt_sources']:
                if aptsource['suite'] != name:
                    raise RuntimeError, "bad data"
                sas = SuiteAptSource()
                sas.suite_id = s.id
                q = self.session.query(AptSource)
                q = q.filter_by(name=aptsource['apt_id'])
                sas.apt_id = q.one().id
                sas.position = aptsource['order']
                self.session.add(sas)
        tlist = list(suite['traits'])
        while tlist:
            trait = tlist.pop(0)
            try:
                self.traits.import_trait(s.id, trait)
            except NoParentError, e:
                tlist.append(trait)
                print "trait %s -> %s" % (trait['name'], e)
                print [x['name'] for x in tlist], len(tlist)
        return s
    

class ImportManager(object):
    def __init__(self, session):
        self.session = session
        self.suites = SuiteImporter(self.session)
        self.parsed = None
        
    def set_parsed_db(self, parsed):
        self.parsed = parsed

    def _import(self):
        self._import_aptkeys()
        self._import_aptsources()
        self._import_default_environment()
        self._import_kernels()
        self._import_diskconfigs()
        self._import_suites()
        self._import_families()
        self._import_profiles()
        
    def _import_aptkeys(self):
        aptkeys = self.parsed['aptkeys']
        with transaction.manager:
            dbobjs = list()
            for k in aptkeys:
                gpg = Gpg()
                content = aptkeys[k]
                keyid = gpg.importkey(content)
                ak = ArchiveKey()
                ak.name = k
                ak.content = content
                ak.keyid = keyid
                self.session.add(ak)
                dbobjs.append(ak)
        return [self.session.merge(o) for o in dbobjs]
                

    def _import_diskconfigs(self):
        dcs = self.parsed['diskconfigs']
        with transaction.manager:
            dbobjs = list()
            for dc in dcs:
                content = dcs[dc]
                dbdc = DiskConfig()
                dbdc.name = dc
                dbdc.content = content
                self.session.add(dbdc)
                dbobjs.append(dbdc)
        return [self.session.merge(o) for o in dbobjs]

    def _import_kernels(self):
        klist = self.parsed['kernels']
        with transaction.manager:
            dbobjs = list()
            for kernel in klist:
                dbkernel = Kernel()
                dbkernel.name = kernel
                self.session.add(dbkernel)
                dbobjs.append(dbkernel)
        return [self.session.merge(o) for o in dbobjs]

    def _import_default_environment(self):
        cfg = self.parsed['default_environment']
        with transaction.manager:
            dbobjs = list()
            for section in cfg.sections():
                for name, value in cfg.items(section):
                    var = DefaultVariable()
                    var.section = section
                    var.name = name
                    var.value = value
                    self.session.add(var)
                    dbobjs.append(var)
        return [self.session.merge(o) for o in dbobjs]

    def _import_aptsources(self):
        aptsources = self.parsed['aptsources']
        with transaction.manager:
            dbobjs = list()
            for a in aptsources:
                aptsource = AptSource()
                aptsource.name = a['apt_id']
                for f in ['uri', 'dist', 'sections', 'local_path']:
                    setattr(aptsource, f, a[f])
                self.session.add(aptsource)
                dbobjs.append(aptsource)
        return [self.session.merge(o) for o in dbobjs]
        

    def _import_suites(self):
        suites = self.parsed['suites']
        for suite in suites:
            self.suites.import_suite(suites[suite])
            
    def _get_base_trait(self, name):
        return self.session.query(BaseTrait).filter_by(name=name).one()
    
    def _import_family(self, family):
        name = family['name']
        basequery = self.session.query(Family)
        parents_exist = True
        for parent in family['parents']:
            fq = basequery.filter_by(name=parent)
            try:
                fq.one()
            except NoResultFound:
                raise NoParentError, "%s doesn't exist" % parent
        with transaction.manager:
            f = Family()
            f.name = name
            self.session.add(f)
            f = self.session.merge(f)
            for parent in family['parents']:
                fp = FamilyParent()
                fp.family_id = f.id
                p = basequery.filter_by(name=parent).one()
                fp.parent_id = p.id
                self.session.add(fp)
            for trt, name, value in family['variables']:
                fv = FamilyVariable()
                fv.family_id = f.id
                bt = self._get_base_trait(trt)
                fv.trait_id = bt.id
                fv.name = name
                fv.value = value
                self.session.add(fv)
                

        
    
    def _import_families(self):
        families = self.parsed['families']
        flist = families.keys()
        while flist:
            family = flist.pop(0)
            fdata = families[family]
            try:
                self._import_family(fdata)
            except NoParentError, e:
                flist.append(family)
                print "Family %s -> %s" % (family, e)
                print len(flist)

    def _import_profiles(self):
        profiles = self.parsed['profiles']
        with transaction.manager:
            for profile in profiles:
                pdata = profiles[profile]
                p = Profile()
                q = self.session.query(Suite).filter_by(name=pdata['suite'])
                suite = q.one()
                p.name = profile
                p.suite_id = suite.id
                self.session.add(p)
                p = self.session.merge(p)
                for pos, name in pdata['traits']:
                    pt = ProfileTrait()
                    pt.profile_id = p.id
                    bt = self._get_base_trait(name)
                    pt.trait_id = bt.id
                    pt.position = pos
                    self.session.add(pt)
                for fam in pdata['families']:
                    pf = ProfileFamily()
                    f = self.session.query(Family).filter_by(name=fam).one()
                    pf.profile_id = p.id
                    pf.family_id = f.id
                    self.session.add(pf)
                for trt, name, value in pdata['variables']:
                    pv = ProfileVariable()
                    pv.profile_id = p.id
                    bt = self._get_base_trait(trt)
                    pv.trait_id = bt.id
                    pv.name = name
                    pv.value = value
                    self.session.add(pv)
                    

    def _import_machines(self):
        pass
    
