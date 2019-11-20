import os
import yaml
from github import Github

g = Github(os.environ['GITHUB_TOKEN'])

def load_base_labels():
    repo = g.get_organization('ooni').get_repo('pm-tools')
    base_labels = {}
    for label in repo.get_labels():
        base_labels[label.name.lower()] = label
    return base_labels

def sync_labels(repo, base_labels):
    repo = g.get_organization('ooni').get_repo(repo)
    for label in repo.get_labels():
        base_label = base_labels.pop(label.name.lower(), None)
        if base_label is not None:
            print('editing label {}'.format(label.name))
            label.edit(
                    name=base_label.name,
                    color=base_label.color,
                    description=base_label.description
            )
    for label_name, label in base_labels.items():
        print('adding label {}'.format(label.name))
        repo.create_label(name=label.name, color=label.color, description=label.description or '')

base_labels = load_base_labels()
sync_labels(repo='github-webhooks', base_labels=base_labels)
