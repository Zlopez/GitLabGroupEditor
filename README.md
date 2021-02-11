# GitLabGroupEditor
Small script for changing properties of projects in group on GitLab

## Features
Here is the list of features the GitLabGroupEditor currently supports:
* edit all projects in specific group at once
* change visibility of projects
* disable/enable merge requests on projects
* list projects in group

## Quick start guide

1. Install requirements

`pip install -r requirements`
   
2. Create a copy of configuration file

`cp python-gitlab.cfg.example python-gitlab.cfg`

3. Update the configuration file with your authentication method

4. Run the script

`python gitlab_group_editor.py <group id>`

This will show you all the projects within specific group.

If you don't know how to find the group id, see [How to find group id in GitLab](#how-to-find-group-id-in-gitlab)

5. Profit!

## Configuration
The GitLabGroupEditor is looking for the configuration file in multiple places.
Default location is `python-gitlab.cfg` file in same folder as script.

Because the GitLabGroupEditor is using [python-gitlab](https://python-gitlab.readthedocs.io/)
library it supports `PYTHON_GITLAB_CFG` environment variable or looks for the configuration in
`/etc/python-gitlab.cfg` and `~/.python-gitlab.cfg`.

For more info about the configuration file structure see [example configuration file](https://github.com/Zlopez/GitLabGroupEditor/blob/main/python-gitlab.cfg.example).

## Usage
Here are some basic examples of GitLabGroupEditor usage.
```
# This will list all projects in group with id 123 
python gitlab_group_editor.py 123

# This will list all projects in group with id 123 using custom configuration 
PYTHON_GITLAB_CFG="example.cfg" python gitlab_group_editor.py 123

# This will change visibility to public for every project in group with id 123 
python gitlab_group_editor.py 123 --visibility public

# This will enable merge requests for every project in group with id 123 
python gitlab_group_editor.py 123 --merge_requests_enabled True

# This will print the help
python gitlab_group_editor.py --help
```

## How to find group id in GitLab
To find the group id for specific group just follow these steps:
* Go to GitLab groups dashboard, the link will be `<gitlab server>/dashboard/groups`

  For example, here is the link for [gitlab.com](https://gitlab.com/dashboard/groups)

  This will show you only your groups, to see all public group, just switch to `Explore public groups` tab
  
* Click on the group you want to see id for

  The id is located right bellow the name of the group
