# hub api /orgs/ooni/repos | jq -r '.[] | .name' > repos.txt
for repo in $(cat repos.txt | grep -v '^#');
do
    labeler scan labels-${repo}.yaml --repo ooni/${repo}
done
