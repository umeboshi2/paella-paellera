import os

import bs4

from .base import BaseParser

class MachineParser(BaseParser):
    def _machine_dirname(self, name):
        return os.path.join(self.basedir, 'machines', name)

    def _machine_xml(self, name):
        dirname = self._machine_dirname(name)
        return os.path.join(dirname, 'machine.xml')

    def _get_script_content(self, machine, name):
        dirname = self._machine_dirname(machine)
        basename = 'script-%s' % name
        filename = os.path.join(dirname, basename)
        return file(filename).read()
    
    def _get_script_names(self, element):
        selements = element.find_all('script')
        return [x.attrs['name'] for x in selements]

    def _get_scripts(self, machine, element):
        names = self._get_script_names(element)
        sdata = dict()
        for name in names:
            sdata[name] = self._get_script_content(machine, name)
        return sdata
        
    def _get_families(self, element):
        felements = element.find_all('family')
        families = list()
        for e in felements:
            f = e.text.strip()
            families.append(f)
        return families

    def _get_variables(self, element):
        velements = element.find_all('machine_variable')
        variables = list()
        for e in velements:
            value = e.text.strip()
            name = e.attrs['name']
            trait = e.attrs['trait']
            variables.append((trait, name, value))
        return variables

    def _parse_machine(self, machine):
        dirname = self._machine_dirname(machine)
        xmlfile = self._machine_xml(machine)
        soup = bs4.BeautifulSoup(file(xmlfile))
        m = soup.machine
        name = m.attrs['name']
        parent = m.attrs.get('parent', None)
        profile = m.attrs.get('profile', None)
        kernel = m.attrs.get('kernel', None)
        diskconfig = m.attrs.get('diskconfig', None)
        
        families = self._get_families(m)
        variables = self._get_variables(m)
        scripts = self._get_scripts(name, m)
        data = dict(name=name, parent=parent, profile=profile,
                    kernel=kernel, diskconfig=diskconfig,
                    families=families, variables=variables,
                    scripts=scripts)
        return data
    
    def parse(self, names):
        machines = dict()
        for name in names:
            parsed = self._parse_machine(name)
            machines[name] = parsed
        return machines
    

    
