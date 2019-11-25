import os
from pprint import pprint
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

effort_map = {
        'effort/xs': 2,
        'effort/s': 3,
        'effort/m': 5,
        'effort/l': 8,
        'effort/xl': 13,
}

total_effort = 0
efforts_by_person = {}

for team_name, repos in teams.items():
    project = None
    for p in g.get_organization('ooni').get_projects():
        if p.name == team_name:
            project = p

    column = None
    for c in project.get_columns():
        if c.name == 'Cycle Backlog':
            column = c
            break

    for card in column.get_cards():
        issue = card.get_content()
        if issue is None:
            continue

        effort_list = list(filter(lambda x: x.name.startswith('effort/'), issue.labels))
        if len(effort_list) == 0:
            print('ERR NO EFFORT: {}'.format(issue))
            continue
        effort = effort_list[0].name
        effort_num = effort_map[effort.lower()]
        assignee = issue.assignee
        if assignee:
            efforts_by_person[assignee.login] = efforts_by_person.get(assignee.login, 0)
            efforts_by_person[assignee.login] += effort_num
        total_effort += effort_num

for name, val in efforts_by_person.items():
    print('{}: {}'.format(name, val))
print('Total Story Points: {}'.format(total_effort))
