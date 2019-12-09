import os
import csv
import argparse
import json
from pprint import pprint
from github import Github
from constants import OONI_TEAMS_BY_NAME, EFFORT_MAP

g = Github(os.environ["GITHUB_TOKEN"])

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
        super().__init__(issue_title, issue_url)
        self.label_class = label_class

    def print_error(self):
        print("{} Missing '{}' ({})".format(self.label_class, self.issue_title, self.issue_url))

class DuplicateLabel(IssueError):
    def __init__(self, label_class, issue_title, issue_url):
        super().__init__(issue_title, issue_url)
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
    effort_num = EFFORT_MAP[effort]
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


def issues_in_column(column_name):
    for team_name, repos in OONI_TEAMS_BY_NAME.items():
        project = None
        for p in g.get_organization("ooni").get_projects():
            if p.name == team_name:
                project = p

        column = None
        for c in project.get_columns():
            if c.name.lower() == column_name.lower():
                column = c
                break

        for card in column.get_cards():
            issue = card.get_content()
            yield project, issue

def get_issues_in_column(column_name):
    column = []
    for project, issue in issues_in_column(column_name):
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

        column.append({
            "assignees": "|".join(assignee_list),
            "repository": issue.repository.name,
            "labels": "|".join(all_labels),
            "priority": priority,
            "effort": effort,
            "effort_points": effort_num,
            "issue_title": issue.title,
            "issue_url": issue.html_url,
            "project": project.name,
            "column": column_name.lower()
        })
    return column

def write_to_csv(dst_file, column_name):
    print("Fetching {}".format(column_name))
    column = get_issues_in_column(column_name)

    print("Writing to {}".format(dst_file))
    with open(dst_file, 'a') as out_file:
        field_names = [
            "priority",
            "effort",
            "effort_points",
            "issue_title",
            "issue_url",
            "assignees",
            "repository",
            "labels",
            "column",
            "project"
        ]
        writer = csv.DictWriter(out_file, fieldnames=field_names)
        writer.writeheader()
        for row in column:
            writer.writerow(row)

def print_summary(src_file):
    total_effort = 0
    efforts_by_person = {}

    with open(src_file) as in_file:
        reader = csv.DictReader(in_file)
        for row in reader:
            try:
                effort_num = int(row["effort_points"])
            except:
                effort_num = 0
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
    parser.add_argument("--column", help="Which column to retrieve", default="Cycle Backlog")
    args = parser.parse_args()

    write_to_csv(args.output, args.column)
    print_summary(args.output)

if __name__ == "__main__":
    main()
