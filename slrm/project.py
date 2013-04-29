import os as _os
import pygit2 as _pygit2
import pysvn as _pysvn

def get_project(p):
    ptype = p["type"]
    if ptype == "git":
        return GitProject(p["name"], p["directory"])
    elif ptype == "svn":
        return SvnProject(p["name"], p["directory"])
    else:
        raise("unknown project type")

class Project(object):
    def __init__(self):
        self.name = ""
        self.directory = None

    def __init__(self, name, directory):
        self.name = name

        try:
            d = _pygit2.discover_repository(_os.path.expanduser(directory))
            self.directory = d
            self.type = Project.GIT
        except Exception:
            pass

    def check(self):
        return True

    def num_changed(self):
        return 0

class GitProject(Project):
    UNCHANGED_STATUSES =  [_pygit2.GIT_STATUS_IGNORED, _pygit2.GIT_STATUS_CURRENT]

    def __init__(self, name, directory):
        self.dir = directory
        self.name = name
        self.repo = _pygit2.Repository(directory)

    def num_changed(self):
        status = self.repo.status()
        return sum(1 for (k,v) in status.items() if not v in GitProject.UNCHANGED_STATUSES)

    def status(self):
        return self.repo.status()

class SvnProject(Project):
    client = _pysvn.Client()

    def __init__(self, name, directory):
        self.dir = directory
        self.name = name
