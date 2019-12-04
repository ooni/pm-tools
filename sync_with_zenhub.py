import os
import csv
import argparse
import json
import requests
from pprint import pprint
from github import Github

from cycle_planner import cycle_backlog_issues, get_effort, IssueError

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
ZENHUB_TOKEN = os.environ["ZENHUB_TOKEN"]
g = Github(GITHUB_TOKEN)

def zenhub_request(method, path, data=None):
    base_url = "https://api.zenhub.io"
    headers = {
        "X-Authentication-Token": ZENHUB_TOKEN
    }
    return requests.request(
        method,
        base_url + path,
        headers=headers,
        json=data
    )

def is_in_cycle_backlog(issue):
    cycle_backlog = list(filter(lambda x: x.name.lower() == "cycle backlog", issue.labels))
    return len(cycle_backlog) > 0

def get_issue_data(repo_id, issue_number):
    path = "/p1/repositories/{}/issues/{}".format(repo_id, issue_number)
    return zenhub_request("GET", path).json()

def set_issue_estimate(repo_id, issue_number, estimate_num):
    path = "/p1/repositories/{}/issues/{}/estimate".format(repo_id, issue_number)
    data = {
        "estimate": estimate_num
    }
    return zenhub_request("PUT", path, data).json()

def get_workspaces(repo_id):
    path = "/p2/repositories/{}/workspaces".format(repo_id)
    return zenhub_request("GET", path).json()

def get_zenhub_boards(repo_id, workspace_id):
    path = "/p2/workspaces/{}/repositories/{}/board".format(workspace_id, repo_id)
    return zenhub_request("GET", path).json()

class CannotFindPipeline(Exception):
    pass

def get_cycle_backlog_pipeline(repo_id):
    workspaces = get_workspaces(repo_id)
    if len(workspaces) == 0:
        raise CannotFindPipeline("Could not find pipeline id")
    workspaces = list(filter(lambda w: w["name"] != None, workspaces))
    try:
        workspace = workspaces[0]
    except IndexError:
        raise CannotFindPipeline("Could not find pipeline id")
    boards = get_zenhub_boards(repo_id, workspace["id"])
    for pipeline in boards["pipelines"]:
        if pipeline["name"].lower() == "cycle backlog":
            return workspace["id"], pipeline["id"]
    raise CannotFindPipeline("Could not find pipeline id")

def move_issue_to_pipeline(workspace_id, repo_id, issue_number, pipeline_id):
    path = "/p2/workspaces/{}/repositories/{}/issues/{}/moves".format(workspace_id, repo_id, issue_number)
    data = {
        "pipeline_id": pipeline_id,
        "position": 0
    }
    return zenhub_request("POST", path, data)


def add_cycle_backlog_labels():
    for project, issue in cycle_backlog_issues():
        if issue is None:
            continue
        print("Adding label to {} {}".format(project, issue.number))
        issue.add_to_labels("cycle backlog")

#add_cycle_backlog_labels()
for repo in g.get_organization('ooni').get_repos():
    workspace_id = None
    try:
        workspace_id, pipeline_id = get_cycle_backlog_pipeline(repo.id)
    except CannotFindPipeline:
        print("ERR cannot find pipeline for {}".format(repo.name))

    open_issues = repo.get_issues(state='open')
    for issue in open_issues:
        if is_in_cycle_backlog(issue) and workspace_id is not None:
            print("moving {}#{} into cycle backlog".format(repo.name, issue.number))
            move_issue_to_pipeline(workspace_id, repo.id, issue.number, pipeline_id)
        try:
            _, effort_num = get_effort(issue)
            zenhub_data = get_issue_data(repo.id, issue.number)
            zenhub_estimate = zenhub_data.get("estimate", {}).get("value", 0)
            if zenhub_estimate == effort_num:
                print("effort {} for {}#{} is synched".format(effort_num, repo.name, issue.number))
                continue
            print("Setting effort {} for {}#{}".format(effort_num, repo.name, issue.number))
            set_issue_estimate(repo.id, issue.number, effort_num)
        except IssueError:
            continue
