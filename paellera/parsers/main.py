import os

import bs4

from .base import parse_database_element
from .base import BaseParser
from .trait import TraitParser
from .family import FamilyParser
from .profile import ProfileParser
from .machine import MachineParser

class MainParser(BaseParser):
    def __init__(self, basedir):
        super(MainParser, self).__init__(basedir)
        self.traitparser = TraitParser(self.basedir)
        self.familyparser = FamilyParser(self.basedir)
        self.profileparser = ProfileParser(self.basedir)
        self.machparser = MachineParser(self.basedir)
        
        self.dbelement = None

    def _get_apt_keys(self):
        dirname = self._aptkey_directory()
        filenames = os.listdir(dirname)
        keys = dict()
        for basename in filenames:
            filename = os.path.join(dirname, basename)
            if basename[-4:] != '.gpg':
                raise RuntimeError, "bad gpg file, %s" % basename
            name = basename[:-4]
            content = file(filename).read()
            keys[name] = content
        return keys
            
    def _get_suite_traits(self, suitedata):
        suite = suitedata['name']
        traits = list()
        for tname in suitedata['traits']:
            self.traitparser.set_trait(suite, tname)
            tdata = self.traitparser.parse()
            traits.append(tdata)
        suitedata['traits'] = traits
    
            
    def _get_top_machine_db(self):
        basename = 'machine_database.xml'
        filename = os.path.join(self.basedir, basename)
        soup = bs4.BeautifulSoup(file(filename), 'lxml')
        return soup.machine_database

    def get_machine_names(self):
        md = self._get_top_machine_db()
        return [x.attrs['name'] for x in md.find_all('machine')]

    def get_kernels(self):
        md = self._get_top_machine_db()
        return [x.text.strip() for x in md.find_all('kernel')]

    def get_diskconfigs(self):
        dirname = self._diskconfig_directory()
        names = os.listdir(dirname)
        dc = dict()
        for name in names:
            filename = os.path.join(dirname, name)
            dc[name] = file(filename).read()
        return dc

    def parse_db_element(self):
        filename = os.path.join(self.basedir, 'database.xml')
        soup = bs4.BeautifulSoup(file(filename).read(), 'lxml')
        self.dbelement = soup.paelladatabase
        self.dbparsed = parse_database_element(self.dbelement)
        self.dbparsed['aptkeys'] = self._get_apt_keys()
        for suite in self.dbparsed['suites']:
            sdata = self.dbparsed['suites'][suite]
            self._get_suite_traits(sdata)
        families = self.familyparser.parse()
        self.dbparsed['families'] = families
        profiles = self.profileparser.parse()
        self.dbparsed['profiles'] = profiles
        diskconfigs = self.get_diskconfigs()
        self.dbparsed['diskconfigs'] = diskconfigs
        kernels = self.get_kernels()
        self.dbparsed['kernels'] = kernels
        machines = self.get_machine_names()
        pm = self.machparser.parse(machines)
        self.dbparsed['machines'] = pm
        
    def parse(self):
        self.parse_db_element()
        
        
        
    
        
    
