#!/usr/bin/python3 

# scans public GitHub repositories to perform the following tasks:
# 1. determine if a github repository is archived or set as read-only.
# 2. assess the frequency of code commits within the repository.
# 3. verify whether the main or master branch protection is enabled.

import argparse
import requests
import datetime
import textwrap

GITHUB_API = 'https://api.github.com/repos/'

def check_valid_repo(repo_name):
    response = requests.get(GITHUB_API + repo_name)
    if response.status_code == 200:
        return True
    return False

def check_archived_repo(repo_name):
    response = requests.get(GITHUB_API + repo_name)
    data = response.json()
    if 'archived' in data and data['archived']:
        return True
    return False

def check_branch_protection(repo_name):
    response = requests.get(GITHUB_API + repo_name + '/branches/main')
    data = response.json()
    if 'protected' in data and data['protected']:
        return True
    return False

def get_commit_frequency(repo_name):
    response = requests.get(GITHUB_API + repo_name + '/commits')
    data = response.json()
    last_commit_date = data[0]['commit']['committer']['date']
    today = datetime.date.today()
    last_commit_date = datetime.datetime.strptime(last_commit_date, "%Y-%m-%dT%H:%M:%SZ").date()
    commit_frequency_30 = 0
    commit_frequency_60 = 0
    commit_frequency_90 = 0

    for commit in data:
        commit_date = datetime.datetime.strptime(commit['commit']['committer']['date'], "%Y-%m-%dT%H:%M:%SZ").date()
        days_ago = (today - commit_date).days

        if days_ago <= 30:
            commit_frequency_30 += 1
        if days_ago <= 60:
            commit_frequency_60 += 1
        if days_ago <= 90:
            commit_frequency_90 += 1

    if (today - last_commit_date).days >= 180:
        return "Last code commit: six months ago or beyond"
    
    return f"Last 30 days: {commit_frequency_30} commits\nLast 60 days: {commit_frequency_60} commits\nLast 90 days: {commit_frequency_90} commits"

def main():
    parser = argparse.ArgumentParser(description='GitHub Repository Checker')
    parser.add_argument('repo', help='GitHub repository name (e.g., owner/repo)')
    parser.add_argument('--report', metavar='FILE', help='Output file for the report')
    args = parser.parse_args()

    repo_name = args.repo

    if check_valid_repo(repo_name) and not check_archived_repo(repo_name):
        if check_branch_protection(repo_name):
            branch_protection_status = "Enabled"
        else:
            branch_protection_status = "Not enabled"
        
        commit_frequency = get_commit_frequency(repo_name)

        output = f"Repository: {repo_name}\n"
        output += f"Status: Valid\n"
        output += f"Archival Status: Not archived\n"
        output += f"Branch Protection: {branch_protection_status}\n"
        output += f"Commit Frequency:\n{textwrap.indent(commit_frequency, '  ')}\n"

        if args.report:
            with open(args.report, 'w') as file:
                file.write(output)
            print(f"Information written to {args.report}")
        else:
            print(output)
    elif check_archived_repo(repo_name):
        print(f'The repository "{repo_name}" is archived.')
    else:
        print(f'The repository "{repo_name}" is not valid.')

if __name__ == '__main__':
    main()
