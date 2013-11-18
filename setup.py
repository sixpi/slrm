from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

setup(
    # Metadata
    name='slrm',
    version='0.2.0',
    description='Utility for keeping track of all local repositories',
    author='Bing Xia',
    author_email="aix.bing@gmail.com",
    packages=['slrm'],

    entry_points={
        'console_scripts': ['slrm = slrm.slrm:main']
    }
)
