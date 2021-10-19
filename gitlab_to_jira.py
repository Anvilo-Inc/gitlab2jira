#!/usr/bin/env python

import gitlab
from jira import JIRA
import urllib3
import html
import mistletoe
from jira_renderer import JIRARenderer

## Disable urllib3 ssl checks warnings
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )

## JIRA config
JIRA_URL = 'https://anvilo.atlassian.net'
JIRA_PROJECT = '' #Project initials - e.g. TR
JIRA_USER = '' #Jira user email
JIRA_PASSWORD = '' #Jira API token
JIRA_LABELS = [] #Labels that are going to be added for each new Jira ticket

## GitLab config
GITLAB_TOKEN = '' #GitLab Access token
GITLAB_URL = 'https://gitlab.com'

#Projects that are going to be migrated and their corresponding Jira components
projects = {
    'anvilo/project-group-name/repository-name': "Jira component name",
}


## Connect onto GitLab
gitlab = gitlab.Gitlab( GITLAB_URL, GITLAB_TOKEN, api_version=4 )

## Connect onto JIRA
jira = JIRA( JIRA_URL, basic_auth=( JIRA_USER, JIRA_PASSWORD ), options={ 'verify': False } )


def md_to_jira_format(subject, project):
    return html.unescape(mistletoe.markdown(subject.replace("](/","]("+GITLAB_URL+"/"+project+"/"), JIRARenderer))
 
transitions_dict = {
    'Backlog': 11,
    'Selected For Development': 21,
    'In Progress': 31,
    'Code Review': 71,
    'Internal Testing': 51,
    'Pending Release': 61,
    'Done': 41
}

#GitLab progress labels to Jira swimlanes mapping
gl_progress_tickets = {
    'Not ready': 'Backlog',
    'Backlog': 'Backlog',
    'To Do': 'Selected For Development',
    'Doing': 'In Progress',
    'Code Review': 'Code Review',
    'QA | Review': 'Pending Release',
    'Done': 'Done'
}

#GitLab epic labels to Jira epic IDs mapping
gl_label_epics = {
    'Moxtra Phase 1': 'TR-2'
}


## Lookup available transitions for an issue
for project_name in projects:
    print('--> Migrating project '+project_name)
    ## Get GitLab project
    gl_project = gitlab.projects.get( project_name )
    ## List project issues
    for issue in gl_project.issues.list( all=True ):
        title = issue.title.replace( "'", "\\'" ).replace('{', '').replace('}', '').replace('[', '').replace(']', '')\
        .replace('(', '').replace(')', '').replace('!', '').replace('*', '').replace('\\', "\\\\").replace('"', "\'")
        found_issues = jira.search_issues( 'project = \''+JIRA_PROJECT+'\' AND summary ~ \"'+ title +'\"')

        if len( found_issues ) == 0:
            issue_dict = {
                'project': JIRA_PROJECT,
                'summary': issue.title,
                'description': md_to_jira_format("Created by " + issue.author['name'] + " at " + issue.created_at + " :\n" + str(issue.description), project_name),
                'issuetype': { 'name': 'Bug' if 'Bug' in issue.labels else 'Task' },
                "components": [{"name": projects[project_name]}],
            }
            issue_dict['description'] = issue_dict['description'][:32764] + '...' if len(issue_dict['description']) > 32767 else issue_dict['description']

            if len(issue.assignees) > 0:
                if 'username' in issue.assignees[0]:
                    issue_dict['assignee'] = { 'name': issue.assignees[0]['username'] }

            jira_issue = jira.issue( jira.create_issue( fields = issue_dict ) )
            jira_issue.update( fields = { "labels": JIRA_LABELS } )

            print ('--> Created issue in Jira : %s' % str(jira_issue))

            for label in issue.labels:
                if gl_progress_tickets.get(label) != None:
                    jira.transition_issue(jira_issue, transitions_dict.get(str(gl_progress_tickets.get(label))))
                    print('--> Moving issue to lane '+gl_progress_tickets.get(label))

                if label in gl_label_epics:
                    jira.add_issues_to_epic(gl_label_epics.get(label), [str(jira_issue)])
                    print('--> Moving issue to lane '+gl_label_epics.get(label))

            if issue.state != 'opened':
                print ('--> Closing issue in Jira')
                jira.transition_issue( jira_issue, transitions_dict.get('Done'))

            try:
                notes = issue.notes.list( all=True )
            except:
                notes = issue.notes.list( all=True )

            for note in notes:
                if not note.system:
                    comment = jira.add_comment( jira_issue, "Comment from " + note.author['name'] + " at " + note.created_at + " :\n" + md_to_jira_format(note.body, project_name))
                    print ('--> Added comment from %s on issue' % note.author['name'])
        else:
            print ('--> Found JIRA issue ' + str(found_issues[0]) + ' for GL issue : ' + issue.title)
