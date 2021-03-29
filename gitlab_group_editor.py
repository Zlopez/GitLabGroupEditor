# This is a script that updates projects properties in specific
# group on GitLab.

import argparse
import os
import requests
import yaml

import gitlab


CONFIG_FILE = "python-gitlab.cfg"
DISTROBAKER_URL = "https://gitlab.cee.redhat.com/osci/distrobaker_centos_stream_config/-/raw/rhel9/distrobaker.yaml"


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
        "--merge_method",
        help="Choose the merge method for MRs. See https://docs.gitlab.com/ee/api/projects.html#project-merge-method",
        choices=["merge", "rebase_merge", "ff"]
    )

    parser.add_argument(
        "--issues_enabled",
        help="Enable/disable issues for the projects in group",
        choices=["True", "False"]
    )

    parser.add_argument(
        "--emails_enabled",
        help="Enable/disable email notifications for the projects in group",
        choices=["True", "False"]
    )

    parser.add_argument(
        "--filter",
        help="Whether to apply actions only to packages included in the DistroBaker sync",
        choices=["synced", "non_synced", "all"],
        default="all"
    )

    parser.add_argument(
        "--dry-run",
        help="Print the changes that would occur, but do not actually save them",
        action=argparse.BooleanOptionalAction
    )

    parser.add_argument(
        "--protect-branch",
        help="Branch to protect. Developers can merge, only maintainers and above can push"
    )

    return parser.parse_args()


if __name__ == "__main__":
    # Main
    args = parse_args()
    group = args.group
    visibility = args.visibility
    merge_requests_enabled = None
    merge_method = None
    issues_enabled = None
    emails_disabled = None
    protect_branch = None

    if args.merge_requests_enabled:
        merge_requests_enabled = args.merge_requests_enabled == "True"

    if args.merge_method:
        merge_method = args.merge_method

    if args.issues_enabled:
        issues_enabled = args.issues_enabled == "True"

    if args.emails_enabled:
        emails_disabled = args.emails_enabled != "True"

    if args.protect_branch:
        protect_branch = args.protect_branch

    config_file = CONFIG_FILE

    # Read environment variable with config
    try:
        config_file = os.environ["PYTHON_GITLAB_CFG"]
    except KeyError:
        pass

    if args.filter != "all":
        r = requests.get(DISTROBAKER_URL, timeout=10)
        r.raise_for_status()

        dbcfg = yaml.load(r.text, Loader=yaml.SafeLoader)
        package_filter = dbcfg["configuration"]["control"]["exclude"]["rpms"]

    # Create Gitlab object
    gl = gitlab.Gitlab.from_config(config_files=[config_file])

    # Get the projects in group
    group = gl.groups.get(group)

    # Update each project in the group
    for project in group.projects.list(as_list=False):
        if (args.filter == "synced" and project.name in package_filter) or \
                (args.filter == "non_synced" and project.name not in package_filter):
            continue

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

        if merge_method is not None:
            print("* merge_method: {old} -> {new}".format(
                old=savable_project.merge_method, new=merge_method)
            )
            savable_project.merge_method = merge_method

        if issues_enabled is not None:
            print("* issues_enabled: {old} -> {new}".format(
                old=savable_project.issues_enabled, new=issues_enabled)
            )
            savable_project.issues_enabled = issues_enabled

        if emails_disabled is not None:
            print("* emails_disabled: {old} -> {new}".format(
                old=savable_project.emails_disabled, new=emails_disabled)
            )
            savable_project.emails_disabled = emails_disabled

        if protect_branch is not None:
            branch_to_protect = savable_project.branches.get(protect_branch)
            print("* protected_branches: {old.name} -> {new.name}".format(
                old=branch_to_protect, new=branch_to_protect
            ))

            if not args.dry_run:
                branch_to_protect.protect(developers_can_push=False, developers_can_merge=True)


        if not args.dry_run:
            while True:
                try:
                    savable_project.save()
                    break
                except requests.exceptions.ReadTimeout:
                    pass
