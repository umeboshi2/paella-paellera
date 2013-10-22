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

class SuiteNotSetError(Exception):
    pass


class TraitManager(object):
    def __init__(self, session):
        self.session = session
        self.suite_id = None
        self.trait_id = None
        self.current_suite = None
        self.current_trait = None
        
    def set_suite_id(self, suite_id):
        self.suite_id = suite_id
        self.current_suite = self.get_suite()

    def query(self):
        return self.session.query(Trait)

    def get_suite(self):
        try:
            return self.session.query(Suite).get(self.suite_id)
        except TypeError, e:
            if "'NoneType'" in e.args[0]:
                raise SuiteNotSetError, "Suite not set."
            else:
                raise e

    def set_trait(self, name):
        btid = self.session.query(BaseTrait).filter_by(name=name).one().id
        q = self.query().filter_by(suite_id=self.suite_id)
        q = q.filter_by(trait_id=btid)
        trait = q.one()
        self.trait_id = trait.id
        self.current_trait = trait

    def get_packages(self):
        q = self.session.query(TraitPackage)
        q = q.filter_by(trait_id=self.trait_id)
        return q.all()

    def add_package(self, name, action='install'):
        with transaction.manager:
            tp = TraitPackage()
            tp.trait_id = self.trait_id
            tp.package = name
            tp.action = action
            self.session.add(tp)
        return self.session.merge(tp)

    def delete_package(self, name):
        pass

    def update_package(self, name, newaction):
        pass

    def add_parent(self, trait_id):
        pass

    def delete_parent(self, trait_id):
        pass

    def add_template(self, template_dict):
        pass

    def update_template(self, template_id, data):
        pass

    def delete_template(self, template_id):
        pass

    def insert_script(self, name, content):
        pass

    def delete_script(self, script_id):
        pass


    def create_trait(self, name):
        pass

    
