import os

import bs4

from .base import BaseParser

class TraitParser(BaseParser):
    def __init__(self, basedir):
        super(TraitParser, self).__init__(basedir)
        self.suite = None
        self.trait = None
        
    def set_trait(self, suite, trait):
        self.suite = suite
        self.trait = trait

    def _template_filename(self, template):
        template = template.replace('/', '-slash-')
        dirname = self._trait_directory(self.suite, self.trait)
        filename = 'template-%s' % template
        return os.path.join(dirname, filename)

    def _script_filename(self, name):
        dirname = self._trait_directory(self.suite, self.trait)
        basename = 'script-%s' % name
        return os.path.join(dirname, basename)

    def _desc_filename(self):
        dirname = self._trait_directory(self.suite, self.trait)
        return os.path.join(dirname, 'description.txt')
    
    
    def _get_parents(self, element):
        return [e.text.strip() for e in element.find_all('parent')]

    def _get_packages(self, element):
        pelements = element.find_all('package')
        packages = list()
        for e in pelements:
            package = e.text.strip()
            action = e.attrs['action']
            packages.append((package, action))
        return packages

    def _get_variables(self, element):
        velements = element.find_all('trait_variable')
        variables = list()
        for e in velements:
            value = e.text.strip()
            name = e.attrs['name']
            trait = e.attrs['trait']
            variables.append((trait, name, value))
        return variables

    def _get_template_data(self, element):
        telements = element.find_all('template')
        templates = list()
        for e in telements:
            template = e.text.strip()
            group = e.attrs['grp_owner']
            owner = e.attrs['owner']
            mode = e.attrs['mode']
            filename = self._template_filename(template)
            content = file(filename).read()
            data = dict(template=template, group=group,
                        owner=owner, mode=mode, content=content)
            templates.append(data)
        return templates

    def _get_script_data(self, element):
        selements = element.find_all('script')
        scripts = list()
        for e in selements:
            name = e.attrs['name']
            filename = self._script_filename(name)
            content = file(filename).read()
            scripts.append((name, content))
        return scripts
    
    
    def _parse_trait_xmlfile(self):
        dirname = self._trait_directory(self.suite, self.trait)
        filename = os.path.join(dirname, 'trait.xml')
        soup = bs4.BeautifulSoup(file(filename))
        telement = soup.trait
        # stuff
        name = telement.attrs['name']
        description = ''
        filename = self._desc_filename()
        if os.path.isfile(filename):
            description = file(filename).read()
        parents = self._get_parents(telement)
        packages = self._get_packages(telement)
        variables = self._get_variables(telement)
        templates = self._get_template_data(telement)
        scripts = self._get_script_data(telement)
        data = dict(name=name,
                    description=description,
                    parents=parents, packages=packages,
                    variables=variables, templates=templates,
                    scripts=scripts)
        return data
    
    def parse(self):
        return self._parse_trait_xmlfile()
    
