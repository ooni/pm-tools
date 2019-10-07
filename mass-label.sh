# hub api /orgs/ooni/repos | jq -r '.[] | .name' > repos.txt
for repo in $(cat repos.txt);
do
    labeler scan labels-${repo}.yaml --repo ooni/${repo}
done
