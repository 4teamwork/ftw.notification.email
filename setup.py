from setuptools import setup, find_packages
import os

version = '2.2.0'
maintainer = 'Jonas Baumann'

tests_require = [
    'ftw.builder',
    'ftw.notification.email [activity]',
    'ftw.testbrowser',
    'ftw.testing',
    'plone.app.testing',
    'plone.testing',
]

extras_require = {
    'tests': tests_require,
    'activity': ['ftw.activity >= 2'],
}

setup(name='ftw.notification.email',
      version=version,
      description='Send edit-notifications by email.',
      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw notification email plone',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.notification.email',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', 'ftw.notification'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'Plone',
        'setuptools',
        'StoneageHTML',
        'BeautifulSoup',  # StoneageHTML requires BeautifulSoup (undeclared)
        'ftw.journal',
        'ftw.notification.base',
        ],

      tests_require=tests_require,
      extras_require=extras_require,
      entry_points='''
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      ''',
      )
