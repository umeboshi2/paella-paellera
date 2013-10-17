from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode, UnicodeText
from sqlalchemy import ForeignKey
from sqlalchemy import Enum
from sqlalchemy import PickleType, Numeric, Boolean
from sqlalchemy import Binary

from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.declarative import declarative_base

#Base = declarative_base()
from .base import Base

name_col = Unicode(100)

##############################################################
# These scripts are only here to fill the scriptnames
# table with the default values.
MOUNT_SCRIPTS = ['proc', 'sys', 'devpts']
MOUNT_SCRIPTS = ['mount_target_%s' % script for script in MOUNT_SCRIPTS]
MOUNT_SCRIPTS += ['u%s' % script for script in MOUNT_SCRIPTS]

TRAIT_SCRIPTS = ['pre', 'preseed', 'remove', 'install',
                 'templates', 'config', 'chroot', 'reconfig', 'post']

MACHINE_SCRIPTS = ['pre', 'setup_disks', 'mount_target',
                   'bootstrap', 'make_device_entries',
                   'apt_sources_installer',
                   'ready_base_for_install',
                   'pre_install', 'install', 'post_install',
                   'install_modules', 'install_kernel',
                   'prepare_bootloader', 'apt_sources_final',
                   'install_fstab', 'post'
                   ] + MOUNT_SCRIPTS


##############################################################


TRAIT_SCRIPT_TYPE = Enum(*TRAIT_SCRIPTS,
                          name='trait_script_type_enum')
MACHINE_SCRIPT_TYPE = Enum(*MACHINE_SCRIPTS,
                            name='machine_script_type_enum')
##############################################################


##############################################################
# base tables
##############################################################

class ArchiveKey(Base):
    __tablename__ = 'archive_keys'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    keyid = Column(Unicode, unique=True)
    content = Column(UnicodeText)

class Suite(Base):
    __tablename__ = 'suites'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    os = Column(Unicode)
    description = Column(UnicodeText)

class AptSource(Base):
    __tablename__ = 'apt_sources'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    uri = Column(Unicode)
    dist = Column(Unicode)
    sections = Column(Unicode)
    local_path = Column(Unicode)

class SuiteAptSource(Base):
    __tablename__ = 'suite_apt_sources'
    suite_id = Column(Integer,
                      ForeignKey('suites.id'), primary_key=True,
                      nullable=False)
    apt_id = Column(Integer,
                    ForeignKey('apt_sources.id'), primary_key=True,
                    nullable=False)
    position = Column(Integer)


##############################################################
# trait tables
##############################################################

class BaseTrait(Base):
    __tablename__ = 'base_traits'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    
class Trait(Base):
    __tablename__ = 'traits'
    id = Column(Integer, primary_key=True)
    suite_id = Column(Integer,
                      ForeignKey('suites.id'),
                      nullable=False)
    trait_id = Column(Integer,
                      ForeignKey('base_traits.id'),
                      nullable=False)
    description = Column(UnicodeText)

class TraitParent(Base):
    __tablename__ = 'trait_parent'
    trait_id = Column(Integer,
                      ForeignKey('traits.id'), primary_key=True,
                      nullable=False)
    parent_id = Column(Integer,
                      ForeignKey('traits.id'), primary_key=True,
                      nullable=False)
    
class TraitPackage(Base):
    __tablename__ = 'trait_package'
    trait_id = Column(Integer,
                      ForeignKey('traits.id'), primary_key=True,
                      nullable=False)
    package = Column(Unicode, primary_key=True,
                     nullable=False)
    action = Column(Unicode, primary_key=True,
                    default=u'install')
    
class TraitVariable(Base):
    __tablename__ = 'trait_variables'
    trait_id = Column(Integer,
                      ForeignKey('traits.id'), primary_key=True,
                      nullable=False)
    name = Column(Unicode, primary_key=True, nullable=False)
    #name = Column(Unicode, primary_key=True)
    value = Column(UnicodeText)
    
class TraitTemplate(Base):
    __tablename__ = 'trait_templates'
    trait_id = Column(Integer,
                      ForeignKey('traits.id'), primary_key=True,
                      nullable=False)
    name = Column(Unicode, primary_key=True)
    owner = Column(Unicode)
    group = Column(Unicode)
    mode = Column(Unicode)
    content = Column(Binary)

class TraitScript(Base):
    __tablename__ = 'trait_scripts'
    trait_id = Column(Integer,
                      ForeignKey('traits.id'), primary_key=True,
                      nullable=False)
    name = Column(TRAIT_SCRIPT_TYPE, primary_key=True)
    content = Column(UnicodeText)

    
##############################################################
# family tables
##############################################################
    
class Family(Base):
    __tablename__ = 'families'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)


class FamilyParent(Base):
    __tablename__ = 'family_parent'
    family_id = Column(Integer, ForeignKey('families.id'), primary_key=True,
                       nullable=False)
    parent_id = Column(Integer, ForeignKey('families.id'), primary_key=True,
                       nullable=False)
    
class FamilyVariable(Base):
    __tablename__ = 'family_variables'
    family_id = Column(Integer, ForeignKey('families.id'), primary_key=True,
                       nullable=False)
    trait_id = Column(Integer,
                      ForeignKey('base_traits.id'), primary_key=True,
                      nullable=False)
    name = Column(Unicode, primary_key=True, nullable=False)
    #name = Column(Unicode, primary_key=True)
    value = Column(UnicodeText)

##############################################################
# profile tables
##############################################################

class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    suite_id = Column(Integer,
                      ForeignKey('suites.id'),
                      nullable=False)
    description = Column(UnicodeText)

class ProfileTrait(Base):
    __tablename__ = 'profile_trait'
    profile_id = Column(Integer,
                        ForeignKey('profiles.id'), primary_key=True,
                        nullable=False)
    trait_id = Column(Integer,
                      ForeignKey('base_traits.id'), primary_key=True,
                      nullable=False)
    position = Column(Integer)
    
    
class ProfileFamily(Base):
    __tablename__ = 'profile_family'
    profile_id = Column(Integer,
                        ForeignKey('profiles.id'), primary_key=True,
                        nullable=False)
    family_id = Column(Integer, ForeignKey('families.id'), primary_key=True,
                       nullable=False)


class ProfileVariable(Base):
    __tablename__ = 'profile_variables'
    profile_id = Column(Integer,
                        ForeignKey('profiles.id'), primary_key=True,
                        nullable=False)
    trait_id = Column(Integer,
                      ForeignKey('base_traits.id'), primary_key=True,
                      nullable=False)
    name = Column(Unicode, primary_key=True, nullable=False)
    #name = Column(Unicode, primary_key=True)
    value = Column(UnicodeText)
    
    

##############################################################
# machine tables
##############################################################

class DiskConfig(Base):
    __tablename__ = 'diskconfigs'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    disklist = Column(UnicodeText)
    content = Column(UnicodeText)

class Kernel(Base):
    __tablename__ = 'kernels'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)


class Machine(Base):
    __tablename__ = 'machines'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    profile_id = Column(Integer,
                        ForeignKey('profiles.id'),
                        nullable=True)
    diskconfig_id = Column(Integer,
                           ForeignKey('diskconfigs.id'),
                           nullable=True)
    kernel_id = Column(Integer,
                       ForeignKey('kernels.id'),
                       nullable=True)

class MachineParent(Base):
    __tablename__ = 'machine_parent'
    machine_id = Column(Integer,
                        ForeignKey('machines.id'),
                        primary_key=True,
                        nullable=False)
    parent_id = Column(Integer,
                        ForeignKey('machines.id'),
                        nullable=False)
    

class MachineFamily(Base):
    __tablename__ = 'machine_family'
    machine_id = Column(Integer,
                        ForeignKey('machines.id'),
                        primary_key=True,
                        nullable=False)
    family_id = Column(Integer,
                       ForeignKey('families.id'),
                       primary_key=True,
                       nullable=False)


class MachineVariable(Base):
    __tablename__ = 'machine_variables'
    machine_id = Column(Integer,
                        ForeignKey('machines.id'),
                        primary_key=True,
                        nullable=False)
    trait_id = Column(Integer,
                      ForeignKey('base_traits.id'), primary_key=True,
                      nullable=False)
    name = Column(Unicode, primary_key=True, nullable=False)
    value = Column(UnicodeText)
    
class MachineScript(Base):
    __tablename__ = 'machine_scripts'
    machine_id = Column(Integer,
                        ForeignKey('machines.id'),
                        primary_key=True,
                        nullable=False)
    name = Column(MACHINE_SCRIPT_TYPE, primary_key=True)
    content = Column(UnicodeText)
    
    

class DefaultVariable(Base):
    __tablename__ = 'default_environment'
    section = Column(Unicode, primary_key=True, nullable=False)
    name = Column(Unicode, primary_key=True, nullable=False)
    value = Column(UnicodeText)

class CurrentVariable(Base):
    __tablename__ = 'current_environment'
    section = Column(Unicode, primary_key=True, nullable=False)
    name = Column(Unicode, primary_key=True, nullable=False)
    value = Column(UnicodeText)
    

Suite.aptsources = relationship(SuiteAptSource,
                                order_by=SuiteAptSource.position)
Suite.traits = relationship(Trait)


Trait.base = relationship(BaseTrait)
#Trait.parents = relationship(TraitParent)
Trait.packages = relationship(TraitPackage)
Trait.variables = relationship(TraitVariable)
Trait.scripts = relationship(TraitScript)
Trait.templates = relationship(TraitTemplate)

Family.variables = relationship(FamilyVariable)

Profile.traits = relationship(ProfileTrait)
Profile.variables = relationship(ProfileVariable)
Profile.suite = relationship(Suite)

Machine.kernel = relationship(Kernel)
Machine.profile = relationship(Profile)
Machine.diskconfig = relationship(DiskConfig)


if __name__ == '__main__':
    import os
    from sqlalchemy import engine_from_config
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.orm import scoped_session
    from zope.sqlalchemy import ZopeTransactionExtension
    cwd = os.getcwd()
    dburl = 'sqlite:///%s/paella.sqlite' % cwd
    settings = {'sqlalchemy.url' : dburl}
    engine = engine_from_config(settings)
    Base.metadata.create_all(engine)
    DBSession = \
        sessionmaker(
            extension=ZopeTransactionExtension())
    DBSession.configure(bind=engine)
    import transaction
    s = DBSession()
    
