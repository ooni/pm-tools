import os
import csv
import argparse
import json
from pprint import pprint
from github import Github

g = Github(os.environ["GITHUB_TOKEN"])

teams = {
    "OONI Backends": [
        "api",
        "orchestra",
        "sysadmin",
        "pipeline",
        "backend-legacy",
        "collector",
    ],
    "OONI Measurements": [
        "probe-engine",
        "jafar",
        "netx",
        "spec",
        "EvilGenius",
    ],
    "OONI Apps": [
        "probe-cli",
        "design-system",
        "probe-desktop",
        "probe-ios",
        "probe-android",
        "probe-legacy",
        "run",
        "probe-react-native",
        "explorer",
        "probe",
        "explorer-legacy",
        "design.ooni.io",
    ],
    "OONI Research": [
        "translations",
        "datk",
        "slides",
        "notebooks",
        "license",
        "code-style",
        "labs",
        "ooni.io",
        "gatherings",
    ]
}

effort_map = {
        "XS": 2,
        "S": 3,
        "M": 5,
        "L": 8,
        "XL": 13,
}

total_effort = 0
efforts_by_person = {}

class IssueError(Exception):
    def __init__(self, issue_title, issue_url):
        self.issue_title = issue_title
        self.issue_url = issue_url

    def print_error(self):
        print("Problem with '{}' ({})".format(self.issue_title, self.issue_url))

class MissingLabel(IssueError):
    def __init__(self, label_class, issue_title, issue_url):
        super(IssueError)
        self.label_class = label_class

    def print_error(self):
        print("{} Missing '{}' ({})".format(self.label_class, self.issue_title, self.issue_url))

class DuplicateLabel(IssueError):
    def __init__(self, label_class, issue_title, issue_url):
        super(IssueError)
        self.label_class = label_class

    def print_error(self):
        print("Duplicate {} '{}' ({})".format(self.label_class, self.issue_title, self.issue_url))

def get_effort(issue):
    effort_list = list(filter(lambda x: x.name.startswith("effort/"), issue.labels))
    if len(effort_list) == 0:
        raise MissingLabel("Effort", issue.title, issue.html_url)
    if len(effort_list) > 1:
        raise DuplicateLabel("Effort", issue.title, issue.html_url)

    effort = effort_list[0].name.upper().split("/")[1]
    effort_num = effort_map[effort]
    return effort, effort_num

def get_priority(issue):
    priority_list = list(filter(lambda x: x.name.startswith("priority/"), issue.labels))
    if len(priority_list) == 0:
        raise MissingLabel("Priority", issue.title, issue.html_url)
    if len(priority_list) > 1:
        raise DuplicateLabel("Priority", issue.title, issue.html_url)

    return priority_list[0].name.split("/")[1].lower()

class MissingAssignee(IssueError):
    def print_error(self):
        print("Missing Assignee '{}' ({})".format(self.issue_title, self.issue_url))

def get_assignees(issue):
    assignees = []
    for a in issue.assignees:
        assignees.append(a.login)
    if len(assignees) == 0:
        raise MissingAssignee(issue.title, issue.html_url)
    return assignees


def cycle_backlog_issues():
    for team_name, repos in teams.items():
        project = None
        for p in g.get_organization("ooni").get_projects():
            if p.name == team_name:
                project = p

        column = None
        for c in project.get_columns():
            if c.name == "Cycle Backlog":
                column = c
                break

        for card in column.get_cards():
            issue = card.get_content()
            yield project, issue

def get_cycle_backlog():
    cycle_backlog = []
    for project, issue in cycle_backlog_issues():
        if issue is None:
            continue

        try:
            effort, effort_num = get_effort(issue)
        except IssueError as err:
            err.print_error()
            continue

        try:
            priority = get_priority(issue)
        except IssueError as err:
            err.print_error()
            continue

        all_labels = list(map(lambda x: x.name, issue.labels))

        try:
            assignee_list = get_assignees(issue)
        except MissingAssignee as err:
            err.print_error()

        cycle_backlog.append({
            "assignees": "|".join(assignee_list),
            "repository": issue.repository.name,
            "labels": "|".join(all_labels),
            "priority": priority,
            "effort": effort,
            "effort_points": effort_num,
            "issue_url": issue.html_url,
            "project": project.name,
        })
    return cycle_backlog

def write_to_csv(dst_file):
    print("Fetching cycle backlog")
    cycle_backlog = get_cycle_backlog()

    print("Writing to {}".format(dst_file))
    with open(dst_file, 'w') as out_file:
        field_names = [
            "priority",
            "effort",
            "effort_points",
            "issue_url",
            "assignees",
            "repository",
            "labels",
            "project"
        ]
        writer = csv.DictWriter(out_file, fieldnames=field_names)
        writer.writeheader()
        for row in cycle_backlog:
            writer.writerow(row)

def print_summary(src_file):
    total_effort = 0
    efforts_by_person = {}

    with open(src_file) as in_file:
        reader = csv.DictReader(in_file)
        for row in reader:
            effort_num = int(row["effort_points"])
            for assignee in row["assignees"].split("|"):
                efforts_by_person[assignee] = efforts_by_person.get(assignee, 0)
                efforts_by_person[assignee] += int(effort_num)
            total_effort += effort_num

    for name, val in efforts_by_person.items():
        print("{}: {}".format(name, val))
    print("Total Story Points: {}".format(total_effort))

def main():
    parser = argparse.ArgumentParser(description="Cycle planner")
    parser.add_argument("--output", help="Where to write the csv file to", required=True)
    args = parser.parse_args()

    write_to_csv(args.output)
    print_summary(args.output)

if __name__ == "__main__":
    main()
