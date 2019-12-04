import os
from github import Github

g = Github(os.environ['GITHUB_TOKEN'])

teams = {
    'OONI Backends': [
        'api',
        'orchestra',
        'sysadmin',
        'pipeline',
        'backend-legacy',
        'collector',
    ],
    'OONI Measurements': [
        'probe-engine',
        'jafar',
        'netx',
        'spec',
        'EvilGenius',
    ],
    'OONI Apps': [
        'probe-cli',
        'design-system',
        'probe-desktop',
        'probe-ios',
        'probe-android',
        'probe-legacy',
        'run',
        'probe-react-native',
        'explorer',
        'probe',
        'explorer-legacy',
        'design.ooni.io',
    ],
    'OONI Research': [
        'translations',
        'datk',
        'slides',
        'notebooks',
        'license',
        'code-style',
        'labs',
        'ooni.io',
        'gatherings',
    ]
}

for team_name, repos in teams.items():
    project = None
    for p in g.get_organization('ooni').get_projects():
        if p.name == team_name:
            project = p

    column = None
    for c in project.get_columns():
        if c.name == 'Icebox':
            column = c

    for repo in g.get_organization('ooni').get_repos():
        if repo.name not in repos:
            print("skipping {}".format(repo.name))
            continue

        open_issues = repo.get_issues(state='open')
        for issue in open_issues:
            print("Adding {}".format(issue))
            try:
                column.create_card(content_id=issue.id, content_type='Issue')
            except Exception as exc:
                print("Already there {}".format(exc))
