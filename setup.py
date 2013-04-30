from setuptools import setup

setup(
    # Metadata
    name = 'slrm',
    version = '0.0.1',
    description = 'Utility for keeping track of all local repositories',
    author = 'Bing Xia',
    author_email = "aix.bing@gmail.com",
    packages = ['slrm'],

    entry_points = {
        'console_scripts' : ['slrm = slrm.slrm:main']
    },
    install_requires=['pygit2'],
    
    # Testing
    test_suite='nose.collector',
    tests_require=['nose'],
)
