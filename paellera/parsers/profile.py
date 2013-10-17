import os

import bs4

from .base import BaseParser

class ProfileParser(BaseParser):
    def _profile_filename(self, name):
        basename = '%s.xml' % name
        return os.path.join(self._profile_directory(), basename)

    def _get_profile_names(self):
        dirname = self._profile_directory()
        files = os.listdir(dirname)
        files = [f for f in files if f.endswith('.xml')]
        names = [x[:-4] for x in files]
        return names

    def _get_traits(self, element):
        telements = element.find_all('trait')
        traits = list()
        for e in telements:
            trait = e.text.strip()
            position = int(e.attrs['ord'])
            traits.append((position, trait))
        return traits

    def _get_families(self, element):
        felements = element.find_all('family')
        families = list()
        for e in felements:
            f = e.text.strip()
            families.append(f)
        return families

    def _get_variables(self, element):
        velements = element.find_all('profile_variable')
        variables = list()
        for e in velements:
            value = e.text.strip()
            name = e.attrs['name']
            trait = e.attrs['trait']
            variables.append((trait, name, value))
        return variables
    
    def _parse_profile(self, name):
        filename = self._profile_filename(name)
        soup = bs4.BeautifulSoup(file(filename))
        p = soup.profile
        name = p.attrs['name']
        suite = p.attrs['suite']
        traits = self._get_traits(p)
        families = self._get_families(p)
        variables = self._get_variables(p)
        data = dict(name=name, suite=suite,
                    traits=traits, families=families,
                    variables=variables)
        return data

    def parse(self):
        profiles = dict()
        for name in self._get_profile_names():
            parsed = self._parse_profile(name)
            profiles[name] = parsed
        return profiles
    

    
