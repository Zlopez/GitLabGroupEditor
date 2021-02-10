# This is a script that updates projects properties in specific
# group on GitLab.

import os

import gitlab

# Let's add API key to header, otherwise only read access to API
group = "10910066"
visibility = "private"
merge_requests_enabled = False
config_file = "python-gitlab.cfg"

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
    print(
        "Updating project {group_name}/{project_name}".format(
            group_name=group.name, project_name=project.name)
    )
    savable_project = gl.projects.get(project.id)
    savable_project.visibility = visibility
    savable_project.merge_requests_enabled = merge_requests_enabled
    savable_project.save()
