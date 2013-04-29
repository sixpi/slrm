#!/usr/bin/env python

import project as _p
import json as _json
import os as _os
import pygit2 as _pygit2
import pysvn as _pysvn

def slrm_get_projects(args):
    with open(args.projects, "r") as f:
        project_json = _json.load(f)
    return project_json

def slrm_status(args):
    project_json = slrm_get_projects(args)

    projects = project_json["projects"]

    header_format = "{0!s:<20} {1!s:<8}"
    print(header_format.format("Name", "Changes"))

    row_format = "{0:<20} {1:>8d}"
    for p in projects:
        proj = _p.get_project(p)

        name = proj.name
        changes = proj.num_changed()

        if not args.only_changed or changes != 0:
            print(row_format.format(name, changes))

def slrm_list(args):
    project_json = slrm_get_projects(args)

    for name in map(lambda x: x["name"], project_json["projects"]):
        print(name)

def slrm_add(args):
    project_json = slrm_get_projects(args)

    project_type = None
    directory = _os.path.realpath(args.directory)
    if project_type is None:
        try:
            git_dir = _pygit2.discover_repository(directory)
            r = _pygit2.Repository(git_dir)
            directory = r.workdir
            project_type = "git"
        except KeyError:
            pass
    if project_type is None:
        try:
            _pysvn.Client().info(directory)
            project_type = "svn"
        except ClientError:
            pass

    if project_type is None:
        print("Error: unknown repository type")
        exit(1)
    existing_directories = map(lambda x: x["directory"], project_json["projects"])
    if directory in existing_directories:
        print("Error: repository %s already exists" % directory)
        exit(1)

    project_name = args.name
    if not project_name:
        _, project_name = _os.path.split(directory.rstrip("/"))

    existing_names = map(lambda x: x["name"], project_json["projects"])
    if project_name in existing_names:
        print("Error: project %s already exists" % project_name)
        exit(1)

    project_dict = {
        "name": project_name,
        "directory": directory,
        "type": project_type}
    project_json["projects"].append(project_dict)

    with open(args.projects, "w") as f:
        _json.dump(project_json, f, indent=2, separators=(',',':'))

    print("Successfully added repository %s" % project_name)

def main():
    import argparse
    import sys

    home_dir = _os.path.expanduser("~")

    parser = argparse.ArgumentParser(description='Manage local repositories')
    parser.add_argument("-p", "--projects", default=("%s/.slrm" % home_dir),
                        help="use alternate project file (defaults to $HOME/.slrm)")
    subparsers = parser.add_subparsers(help="subparser help")

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

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
