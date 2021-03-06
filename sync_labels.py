import os
import yaml
import argparse
from pprint import pprint
from github import Github

g = Github(os.environ['GITHUB_TOKEN'])

def load_base_labels():
    repo = g.get_organization('ooni').get_repo('pm-tools')
    base_labels = {}
    for label in repo.get_labels():
        base_labels[label.name.lower()] = label
    return base_labels

def sync_labels(repo, base_labels):
    for label in repo.get_labels():
        base_label = base_labels.pop(label.name.lower(), None)
        if base_label is not None:
            if label.color == base_label.color and label.description == base_label.description:
                continue
            print('editing label {}'.format(label.name))
            label.edit(
                    name=base_label.name,
                    color=base_label.color,
                    description=base_label.description or ''
            )
    for label_name, label in base_labels.items():
        print('adding label {}'.format(label.name))
        repo.create_label(name=label.name, color=label.color, description=label.description or '')

def main():
    parser = argparse.ArgumentParser(description="Cycle planner")
    parser.add_argument("--repo", help="limit to a single repository")
    args = parser.parse_args()

    base_labels = load_base_labels()
    pprint(base_labels)
    if args.repo:
        print('Synching labels in ooni/{}'.format(args.repo))
        repo = g.get_organization('ooni').get_repo(args.repo)
        sync_labels(repo=repo, base_labels=base_labels)
        return

    for repo in g.get_organization('ooni').get_repos():
        print('Synching labels in ooni/{}'.format(repo.name))
        sync_labels(repo=repo, base_labels=base_labels)

if __name__ == '__main__':
    main()
