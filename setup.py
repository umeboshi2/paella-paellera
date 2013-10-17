import os

from setuptools import setup, find_packages

#here = os.path.abspath(os.path.dirname(__file__))
#README = open(os.path.join(here, 'README.txt')).read()
#CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'trumpet>=0.1.1dev', # pull from github
    ]

setup(name='paellera',
      version='0.0',
      description='paellera',
      long_description="long description",
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Joseph Rawson',
      author_email='joseph.rawson.works@littledebian.org',
      url='https://github/umeboshi2/paellera',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='paellera',
      install_requires=requires,
      dependency_links=[
        'https://github.com/umeboshi2/trumpet/archive/master.tar.gz#egg=trumpet-0.1.1dev',
        'https://github.com/umeboshi2/hubby/archive/master.tar.gz#egg=hubby-0.0dev',
        ],
      entry_points="""\
      [paste.app_factory]
      main = paellera:main
      [console_scripts]
      initialize_paellera_db = paellera.scripts.initializedb:main
      [fanstatic.libraries]
      paellera_lib = paellera.resources:library
      paellera_css = paellera.resources:css
      paellera_js = paellera.resources:js
      """,
      )
