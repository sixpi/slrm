import subprocess
from subprocess import DEVNULL, CalledProcessError
import os
import sys

from path import path
import colorama
from colorama import Fore, Style


class Project(object):
    def __init__(self, name, directory):
        pass

    def num_changed(self):
        return 0


class GitProject(Project):

    def __init__(self, name, directory):
        self.name = name
        self.directory = path(directory)

    def num_changed(self):
        changes = subprocess.check_output(
            ["git", "status", "--porcelain"]).decode('utf-8')
        return len([x for x in changes.strip().split("\n") if x])

    def unpushed(self):
        return 0

    def remotes(self):
        self.directory.chdir()
        remotes = subprocess.check_output(
            ["git", "remote"]).decode('utf-8').split()
        return remotes

    def cur_branch(self):
        self.directory.chdir()
        branch = subprocess.check_output(
            ["git", "rev-parse",
             "--abbrev-ref", "HEAD"]).decode('utf-8').strip()
        return branch


def slrm_get_projects():
    slrm_dir = path("~/.slrm.d").expanduser()
    slrm_dir.mkdir_p()

    projects = []

    for d in slrm_dir.dirs("*"):
        name = d.basename()

        d.chdir()
        ret = subprocess.check_call(["git", "status"],
                                    stdout=DEVNULL,
                                    stderr=subprocess.STDOUT)

        if ret != 0:
            continue
        projects.append(GitProject(name, d))

    return projects


def slrm_status(args):
    header_format = (Style.BRIGHT + Fore.GREEN +
                     "{0!s:<20} {1!s:>8} {2!s:>16} {3!s:>16}" +
                     Style.NORMAL + Fore.RESET)
    print(header_format.format("Name", "Changes", "Origin", "Upstream"))

    row_format = "{0:<20} {1:>8d} {2!s:>16} {3!s:>16}"
    for project in slrm_get_projects():
        name = project.name

        local_branch = project.cur_branch()

        origin_stat = "-/-"
        upstream_stat = "-/-"

        if "origin" in project.remotes():
            try:
                subprocess.call(["git", "fetch", "origin"],
                                stdout=DEVNULL, stderr=subprocess.STDOUT)

                origin_unpulled, origin_unpushed = [
                    int(x) for x in subprocess.check_output(
                        ["git", "rev-list", "--count", "--left-right","HEAD",
                         "origin/{0}...HEAD".format(local_branch)],
                        stderr=DEVNULL).split()]
                origin_stat = "{0}/{1}".format(origin_unpushed,
                                               origin_unpulled)
            except CalledProcessError:
                pass

        if "upstream" in project.remotes():
            try:
                subprocess.call(["git", "fetch", "upstream"])

                upstream_unpulled, upstream_unpushed = [
                    int(x) for x in subprocess.check_output(
                        ["git", "rev-list", "--count", "--left-right","HEAD",
                         "upstream/{0}...HEAD".format(local_branch)],
                        stderr=DEVNULL).split()]
                upstream_stat = "{0}/{1}".format(upstream_unpushed,
                                                 upstream_unpulled)
            except CalledProcessError:
                pass

        print(row_format.format(name, project.num_changed(),
                                origin_stat, upstream_stat))


def slrm_list(args):
    projects = slrm_get_projects()

    for project in projects:
        print(project.name)


def slrm_add(args):
    directory = path(args.directory).realpath()

    project_name = args.name
    if not project_name:
        project_name = directory.basename()

    existing_names = [project.name for project in slrm_get_projects()]
    if project_name in existing_names:
        print("Error: project %s already exists" % project_name)
        exit(1)

    slrm_dir = path("~/.slrm.d").expanduser()
    slrm_dir.mkdir_p()

    directory.chdir()
    directory.symlink(slrm_dir/project_name)

    print("Successfully added repository %s" % project_name)


def slrm_dir(args):
    projects = slrm_get_projects()
    project = args.project.strip()

    exact_matches = [p for p in projects if p.name == project]
    prefix_matches = [p for p in projects if p.name.startswith(project)]

    if len(exact_matches) == 1:
        p = exact_matches[0]
    elif len(prefix_matches) == 1:
        p = prefix_matches[0]
    elif len(prefix_matches) > 1:
        print("'{0}' is ambiguous".format(project))
        if len(prefix_matches) < 5: # arbitrary cutoff for printing suggestions
            print("Did you mean one of:")
            for p in prefix_matches:
                print("\t{0}".format(p["name"]))
        exit(1)
    else:
        print("No matches for {0}".format(project))
        exit(1)

    print(p.directory.realpath())


def make_parser():
    import argparse

    home_dir = os.path.expanduser("~")

    parser = argparse.ArgumentParser(description='Manage local repositories')
    parser.add_argument("-p", "--projects", default=("%s/.slrm" % home_dir),
                        help="use alternate project file (defaults"
                        " to $HOME/.slrm)")
    subparsers = parser.add_subparsers()

    status_command = subparsers.add_parser("status",
                                           help="Get status of all repositories")
    status_command.add_argument("-c", "--only-changed", action='store_true')
    status_command.set_defaults(func=slrm_status)

    list_command = subparsers.add_parser("list",
                                         help="List all the repositories")
    list_command.set_defaults(func=slrm_list)

    add_command = subparsers.add_parser("add",
                                        help="Add a repository")
    add_command.add_argument("-n", "--name",
                             help="Name of the new repository")
    add_command.add_argument("-d", "--directory",
                             help="Directory to add", default=".")
    add_command.set_defaults(func=slrm_add)

    dir_command = subparsers.add_parser("dir",
                                        help="Print a project directory")
    dir_command.add_argument("project", help="Name of project")
    dir_command.set_defaults(func=slrm_dir)

    return parser


def main():
    colorama.init()
    parser = make_parser()

    if len(sys.argv) == 1:
        args = parser.parse_args(args=['status'])
    else:
        args = parser.parse_args()

    args.func(args)
    colorama.deinit()


if __name__ == "__main__":
    main()
