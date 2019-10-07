import yaml
import copy
from glob import glob

def load_base_labels():
    labels = {}
    with open('base-labels.yaml') as in_file:
        y = yaml.safe_load(in_file)
    for label in y['labels']:
        if 'equiv' in label:
            equivs = label.pop('equiv')
            for equiv in equivs:
                labels[equiv.lower()] = label
        labels[label['name'].lower()] = label
    return labels

def load_repo(filename):
    labels = {}
    with open(filename) as in_file:
        y = yaml.safe_load(in_file)
    for label in y['labels']:
        labels[label['name'].lower()] = label
    return y['repo'], labels

def get_extra_labels(base_labels, current_labels):
    extra_labels = copy.deepcopy(current_labels)
    for label in base_labels.keys():
        if label in extra_labels:
            extra_labels.pop(label)
    return [label for label in extra_labels.values()]

def dump_labels(repo_name, extra_labels):
    with open('base-labels.yaml') as in_file:
        content = yaml.safe_load(in_file)
    content['repo'] = repo_name
    for label in content['labels']:
        if 'equiv' in label:
            label.pop('equiv')
    for label in extra_labels:
        content['labels'].append(label)
    with open('labels-{}.yaml'.format(repo_name), 'w') as out_file:
       yaml.dump(content, out_file)

base_labels = load_base_labels()
for fn in glob('labels-*.yaml'):
    repo_name, current_labels = load_repo(fn)
    extra_labels = get_extra_labels(base_labels, current_labels)
    dump_labels(repo_name, extra_labels)
