import os

def parse_apt_source(element):
    apt_id = element.attrs['apt_id']
    dist = element.attrs['dist']
    local_path = element.attrs['local_path']
    uri = element.attrs['uri']
    sections = element.attrs['sections']
    return dict(apt_id=apt_id, dist=dist,
                local_path=local_path, uri=uri,
                sections=sections)


def parse_suite(element):
    name = element.attrs['name']
    os = element.attrs['os']
    apt_sources = list()
    for apt in element.find_all('suiteapt'):
        apt_id = apt.attrs['apt_id']
        order = apt.attrs['order']
        suite = apt.attrs['suite']
        if suite != name:
            raise RuntimeError, "bad xml"
        data = dict(apt_id=apt_id, order=order,
                    suite=suite)
        apt_sources.append(data)
    parsed = dict(name=name, os=os, apt_sources=apt_sources)
    return parsed


def get_suite_traits(dbelement, suite):
    tlist = dbelement.find_all('traits')
    traits = [t for t in tlist if t.attrs['suite'] == suite][0]
    return (t.attrs['name'] for t in traits.find_all('trait'))

def parse_database_element(dbelement):
    aptsources = dbelement.aptsources.find_all('aptsource')
    aptsources = (parse_apt_source(e) for e in aptsources)
    suites = dict()
    for s in dbelement.suites.find_all('suite'):
        parsed = parse_suite(s)
        name = parsed['name']
        traits = get_suite_traits(dbelement, name)
        parsed['traits'] = traits
        suites[name] = parsed
    db = dict(aptsources=aptsources, suites=suites)
    return db



class BaseParser(object):
    def __init__(self, basedir):
        if not os.path.isdir(basedir):
            raise RuntimeError, "No directory %s" % basedir
        self.basedir = basedir

    def _suite_directory(self, suite):
        return os.path.join(self.basedir, suite)

    def _trait_directory(self, suite, trait):
        return os.path.join(self.basedir, suite, trait)

    def _aptkey_directory(self):
        return os.path.join(self.basedir, 'aptkeys')
    
    def _family_directory(self):
        return os.path.join(self.basedir, 'families')

    def _profile_directory(self):
        return os.path.join(self.basedir, 'profiles')

    def _machine_directory(self):
        return os.path.join(self.basedir, 'machines')

    def _diskconfig_directory(self):
        return os.path.join(self.basedir, 'diskconfig')
        
parsedb = parse_database_element

if __name__ == '__main__':
    import bs4
    filename = 'database.xml'
    s = bs4.BeautifulSoup(file(filename).read(), 'lxml')
    p = s.paelladatabase
    db = parsedb(p)
    suites = db['suites']
    aptsources = db['aptsources']
