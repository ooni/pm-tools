import os
from github import Github

g = Github(os.environ['GITHUB_TOKEN'])

ooni = g.get_organization('ooni')
ooni_team = ooni.get_team_by_slug('ooni-team')
default_permission = 'admin'

team_repos = set()
for repo in ooni_team.get_repos():
    print('setting {} permission to {}'.format(default_permission, repo.full_name))
    ooni_team.set_repo_permission(repo, default_permission)
    team_repos.add(repo.full_name)

all_repos = set()
for repo in ooni.get_repos():
    all_repos.add(repo.full_name)

missing_repos = all_repos - team_repos
for repo_slug in missing_repos:
    print('adding {}'.format(repo_slug))
    repo = g.get_repo(repo_slug)
    ooni_team.add_to_repos(repo)
    ooni_team.set_repo_permission(repo, default_permission)
