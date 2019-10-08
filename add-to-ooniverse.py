import os
from github import Github

g = Github(os.environ['GITHUB_TOKEN'])

project = None
for p in g.get_organization('ooni').get_projects():
    if p.name == 'OONI-Verse':
        project = p

column = None
for c in project.get_columns():
    if c.name == 'Icebox':
        column = c

# Then play with your Github objects:
for repo in g.get_organization('ooni').get_repos():
    open_issues = repo.get_issues(state='open')
    for issue in open_issues:
        print("Adding {}".format(issue))
        try:
            column.create_card(content_id=issue.id, content_type='Issue')
        except Exception as exc:
            print("Already there {}".format(exc))
