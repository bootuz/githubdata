import argparse

from github import GitHubData
from helpers import print_like_table

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get some information about github repos via github REST API')
    parser.add_argument('-l', '--link', type=str, help='Provide repo\'s link', required=True)
    parser.add_argument('-s', '--since', default=None, help='Provide a date from where you\'d like to parse commits. '
                                                            'Format DD-MM-YY')
    parser.add_argument('-u', '--until', default=None, help='Provide a date until where you\'d like to parse commits. '
                                                            'Format DD-MM-YY')
    parser.add_argument('-b', '--branch', default='master', help='Provide branch name')
    args = parser.parse_args()

    github = GitHubData(repo_link=args.link, since=args.since, until=args.until, branch=args.branch)

    print('Collecting contributors and their\'s commits')
    data = github.contributions()
    print('Finished')
    print('Collecting information about pull requests')
    pulls, old_pulls = github.pull_requests()
    print('Finished')
    print('Collecting information about issues')
    issues, old_issues = github.issues()
    print('Finished')

    print_like_table(data)
    print(f'Open pull requests: {pulls["open"]}\n'
          f'Old pull requests: {old_pulls}\n'
          f'Closed pull requests: {pulls["closed"]}')
    print('============================')
    print(f'Open issues: {issues["open"]}\n'
          f'Old issues: {old_issues}\n'
          f'Closed issues: {issues["closed"]}')
