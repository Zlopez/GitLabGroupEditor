# This is a script that updates projects properties in specific
# group on GitLab.

import argparse
import os
import requests
import yaml

import gitlab


CONFIG_FILE = "python-gitlab.cfg"
DISTROBAKER_URL = "https://gitlab.cee.redhat.com/osci/distrobaker_centos_stream_config/-/raw/rhel9/distrobaker.yaml"
DEFAULT_MR_TEMPLATE = "Merge Request Template.md"

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
        "--only_allow_merge_if_pipeline_succeeds",
        help="Merge requests may not be merged until the pipeline passes",
        choices=["True", "False"]
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

    parser.add_argument(
        "--ci_config_path",
        help="The path to the Gitlab CI configuration."
    )

    parser.add_argument(
        "--shared_runners_enabled",
        help="Enable/disable shared CI runners for the projects in group",
        choices=["True", "False"]
    )

    parser.add_argument(
        "--merge-request-template",
        help="A markdown file to use as a template for merge requests.",
        type=argparse.FileType('r'),
        nargs="?",
        const=open(DEFAULT_MR_TEMPLATE, 'r'),
        default=None,
    )

    parser.add_argument(
        "--c9s_setup",
        help="Configure the selected projects with all of the standard CentOS Stream 9 settings. "
             "Does not set visibility. Idempotent.",
        action=argparse.BooleanOptionalAction
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
    ci_config_path = None
    only_allow_merge_if_pipeline_succeeds = None
    shared_runners_enabled = None
    mr_template = None

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

    if args.ci_config_path:
        ci_config_path = args.ci_config_path

    if args.only_allow_merge_if_pipeline_succeeds:
        only_allow_merge_if_pipeline_succeeds = args.only_allow_merge_if_pipeline_succeeds

    if args.shared_runners_enabled:
        shared_runners_enabled = args.shared_runners_enabled == "True"

    if args.merge_request_template:
        mr_template = args.merge_request_template.read()
        args.merge_request_template.close()

    if args.c9s_setup:
        merge_requests_enabled = True
        merge_method = "ff"
        issues_enabled = False
        emails_disabled = False
        protect_branch = "c9s"
        ci_config_path = "global-tasks.yml@redhat/centos-stream/ci-cd/dist-git-gating-tests"
        only_allow_merge_if_pipeline_succeeds = True
        shared_runners_enabled = False
        with open(DEFAULT_MR_TEMPLATE, "r") as f:
            mr_template = f.read()


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

        if ci_config_path is not None:
            print("* ci_config_path: {old} -> {new}".format(
                old=savable_project.ci_config_path, new=ci_config_path)
            )
            savable_project.ci_config_path = ci_config_path

        if only_allow_merge_if_pipeline_succeeds is not None:
            print("* only_allow_merge_if_pipeline_succeeds: {old} -> {new}".format(
                old=savable_project.only_allow_merge_if_pipeline_succeeds,
                new=only_allow_merge_if_pipeline_succeeds)
            )
            savable_project.only_allow_merge_if_pipeline_succeeds = only_allow_merge_if_pipeline_succeeds

        if shared_runners_enabled is not None:
            print("* shared_runners_enabled: {old} -> {new}".format(
                old=savable_project.shared_runners_enabled, new=shared_runners_enabled)
            )
            savable_project.shared_runners_enabled = shared_runners_enabled

        if mr_template is not None:
            print("* merge_request_template: {old} -> {new}".format(
                old=savable_project.merge_requests_template, new=mr_template)
            )

        if protect_branch is not None:
            try:
                branch_to_protect = savable_project.branches.get(protect_branch)
                print("* protected_branches: {old.name} -> {new.name}".format(
                    old=branch_to_protect, new=branch_to_protect
                ))

                if not args.dry_run:
                    branch_to_protect.protect(developers_can_push=False, developers_can_merge=True)
            except gitlab.exceptions.GitlabGetError as e:
                print("WARNING: {group_name}/{project_name} has no '{branch_name}' branch".format(
                      group_name=group.name, project_name=project.name, branch_name=protect_branch)
                )


        if not args.dry_run:
            while True:
                try:
                    savable_project.save()
                    break
                except requests.exceptions.ReadTimeout:
                    pass
