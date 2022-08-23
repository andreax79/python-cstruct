from setuptools import setup, find_packages
from cstruct import __version__


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='cstruct',
    version=__version__,
    description="C-style structs for Python",
    long_description="""\
Convert C struct definitions into Python classes with methods for serializing/deserializing.""",
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='struct',
    author='Andrea Bonomi',
    author_email='andrea.bonomi@gmail.com',
    url='http://github.com/andreax79/python-cstruct',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points="""
      # -*- Entry points: -*-
      """,
    test_suite='tests',
    tests_require=['pytest'],
)
