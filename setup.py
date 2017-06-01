from setuptools import setup, find_packages

version = '1.4'

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
          'Programming Language :: Python :: 2.4',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.0',
          'Programming Language :: Python :: 3.1',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
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
