from setuptools import setup, find_packages
import sys, os

version = '1.0'

def readme():
    try:
        f = open('README.md')
        return f.read()
    finally:
        f.close()

setup(name='cstruct',
      version=version,
      description="C-style structs for Python",
      long_description="""\
Convert C struct definitions into Python classes with methods for serializing/deserializing.""",
      classifiers=[
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='struct',
      author='Andrea Bonomi',
      author_email='andrea.bonomi@gmail.com',
      url='http://github.com/andreax79/python-cstruct',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
