# GitLab migration tool
## Migration tool which makes the issue migration from Gitlab To Jira possible

The tool is based on Python.

### Settings
- [Get Jira access token](https://id.atlassian.com/manage-profile/security/api-tokens) and add it as a value of the `JIRA_PASSWORD` variable
- [Get GitLab access token](https://gitlab.com/-/profile/personal_access_tokens) and add it as a value of the `GITHUB_TOKEN` variable
- Fill the email you are registered in Jira with in the `JIRA_USER` variable
- Fill in the target Jira Project in `JIRA_PROJECT`
- Replace `project-group-name/repository-name` with the source GitLab project. If you want to assign specific component, replace `Jira component name` with the component name.
- ✨Magic ✨

### Advanced settings:
- To match the correct Jira Swimlane you need to verify the `gl_progress_tickets` dictionary, which is a map of GitLab labels, used as swimlanes and Jira Swimlane names (a.k.a *Transitions* in Jira).
- Since the script needs the Transition IDs there is a Transitions dictionary map to the corresponding Transition IDs. These IDs are specific for each workflow (usually there is a separate workflow for each board). Check your IDs from [here](https://anvilo.atlassian.net/secure/admin/workflows/ListWorkflows.jspa), choosing the workflow of your board and correct them in the `transitions_dict`. 
- If you are using Jira Epics, you could check the `gl_label_epics` dictionary. This is a map of GitLab Labels, used as epics and Jira Epic IDs

## Features

- Migrating issue title and body
- Migrating issue assignee
- Matching ticket progress with the Jira swimlane
- Matching epic labels to Jira epics
- Project components
- Issue types

## Installation

GitLab Migration tool requires the following libraries to run:
- [python-gitlab](https://github.com/python-gitlab/python-gitlab)
- [Python Jira](https://github.com/pycontribs/jira)
- [miyuchina/mistletoe](https://github.com/miyuchina/mistletoe)

Install the dependencies.

```python
pip install python-gitlab
pip install jira
pip3 install mistletoe
```

And run the script...

```python
python gitlab_to_jira.py
```