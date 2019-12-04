import os
import csv
import argparse
import json
import requests
from pprint import pprint
from github import Github

from cycle_planner import cycle_backlog_issues

g = Github(os.environ["GITHUB_TOKEN"])


for repo in g.get_organization('ooni').get_repos():
    open_issues = repo.get_issues(state='open')
    for issue in open_issues:
        print("{}#{}".format(repo.id, issue.id))
