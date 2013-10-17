import os

import bs4

from .base import BaseParser

class FamilyParser(BaseParser):
    def _family_filename(self, name):
        basename = '%s.xml' % name
        return os.path.join(self._family_directory(), basename)

    def _get_family_names(self):
        dirname = self._family_directory()
        files = os.listdir(dirname)
        files = [f for f in files if f.endswith('.xml')]
        names = [x[:-4] for x in files]
        return names

    def _get_parents(self, element):
        pelements = element.find_all('parent')
        return [p.text.strip() for p in pelements]
    
    def _get_variables(self, element):
        velements = element.find_all('family_variable')
        variables = list()
        for e in velements:
            value = e.text.strip()
            name = e.attrs['name']
            trait = e.attrs['trait']
            variables.append((trait, name, value))
        return variables
    
    def _parse_family(self, name):
        filename = self._family_filename(name)
        soup = bs4.BeautifulSoup(file(filename))
        f = soup.family
        name = f.attrs['name']
        parents = self._get_parents(f)
        variables = self._get_variables(f)
        return dict(name=name, parents=parents, variables=variables)

    def parse(self):
        families = dict()
        for name in self._get_family_names():
            parsed = self._parse_family(name)
            families[name] = parsed
        return families

    
