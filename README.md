Simple Local Repository Manager
===============================

Just a tool to help me keep track of all the repositories I've checked out and
which ones have changes, etc.

Requires pygit2 and pysvn.

Usage
-----

slrm [-h] [-p PROJECTS] {status,list,add} ...

Manage local repositories

positional arguments:
  {status,list,add}     subparser help
    status              Get status of all repositories
    list                List all the repositories
    add                 Add a repository

optional arguments:
  -h, --help            show this help message and exit
  -p PROJECTS, --projects PROJECTS
                        use alternate project file (defaults to $HOME/.slrm)
