from setuptools import setup, find_packages
import os

version = '1.1.7'

entry_points = {
    'openprocurement.auctions.core.plugins': [
        'auctions.dgf.other = openprocurement.auctions.dgf.includeme:includeme_other',
        'auctions.dgf.financial = openprocurement.auctions.dgf.includeme:includeme_financial'
    ],
    'openprocurement.api.migrations': [
        'auctions = openprocurement.auctions.dgf.migration:migrate_data'
    ],
    'openprocurement.tests': [
        'auctions.dgf = openprocurement.auctions.dgf.tests.main:suite'
    ]
}

requires = [
    'setuptools',
    'openprocurement.auctions.core',
    'openprocurement.auctions.flash',
    'openprocurement.schemas.dgf',
    'schematics-flexible'
]

docs_requires = requires + [
    'sphinxcontrib-httpdomain',
]

setup(name='openprocurement.auctions.dgf',
      version=version,
      description="",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      license='Apache License 2.0',
      url='https://github.com/openprocurement/openprocurement.auctions.dgf',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.auctions'],
      include_package_data=True,
      zip_safe=False,
      extras_require={'docs': docs_requires},
      install_requires=requires,
      entry_points=entry_points,
      )
