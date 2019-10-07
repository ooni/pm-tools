#!/bin/bash
set -ex

# hub api /orgs/ooni/repos | jq -r '.[] | .name' > repos.txt
echo "Synching labels with repo"
for repo in $(cat repos.txt | grep -v '^#');
do
    labeler scan labels-${repo}.yaml --repo ooni/${repo}
done

echo "Merging with base labels"
python merge-labels.py

echo "Writing changes to remote"
for repo in $(cat repos.txt | grep -v '^#');
do
    labeler apply labels-${repo}.yaml --repo ooni/${repo}
done
