# This is a script that updates projects properties in specific
# group on GitLab.

import argparse
import os

import gitlab


CONFIG_FILE = "python-gitlab.cfg"


def parse_args():
    """
    Parse arguments.

    Return:
      Argument object.
    """
    parser = argparse.ArgumentParser(
        description="This app uses GitLab API to edit projects in specific group.")
    parser.add_argument("group", type=int, help="Id of the group to edit")
    parser.add_argument(
        "--visibility",
        help="Set visibility of the projects to specific value",
        choices=["private", "public"]
    )
    parser.add_argument(
        "--merge_requests_enabled",
        help="Enable/disable merge requests for the projects in group",
        choices=["True", "False"]
    )
    parser.add_argument(
        "--issues_enabled",
        help="Enable/disable issues for the projects in group",
        choices=["True", "False"]
    )

    return parser.parse_args()


if __name__ == "__main__":
    # Main
    args = parse_args()
    group = args.group
    visibility = args.visibility
    merge_requests_enabled = None
    issues_enabled = None

    if args.merge_requests_enabled:
        merge_requests_enabled = args.merge_requests_enabled == "True"

    if args.issues_enabled:
        issues_enabled = args.issues_enabled == "True"
    config_file = CONFIG_FILE

    # Read environment variable with config
    try:
        config_file = os.environ["PYTHON_GITLAB_CFG"]
    except KeyError:
        pass

    # Create Gitlab object
    gl = gitlab.Gitlab.from_config(config_files=[config_file])

    # Get the projects in group
    group = gl.groups.get(group)

    # Update each project in the group
    for project in group.projects.list():
        print("Project {group_name}/{project_name}".format(
                group_name=group.name, project_name=project.name)
        )
        savable_project = gl.projects.get(project.id)
        if visibility:
            print("* visibility: {old} -> {new}".format(
                old=savable_project.visibility, new=visibility)
            )
            savable_project.visibility = visibility
        if merge_requests_enabled is not None:
            print("* merge_requests_enabled: {old} -> {new}".format(
                old=savable_project.merge_requests_enabled, new=merge_requests_enabled)
            )
            savable_project.merge_requests_enabled = merge_requests_enabled

        if issues_enabled is not None:
            print("* issues_enabled: {old} -> {new}".format(
                old=savable_project.issues_enabled, new=issues_enabled)
            )
            savable_project.issues_enabled = issues_enabled
        savable_project.save()
