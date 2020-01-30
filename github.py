import re
from http.client import HTTPSConnection
import json
from datetime import datetime
from helpers import date_formatter


class GitHubData:
    TOKEN = 'YOUR TOKEN'
    BASE_URL = 'api.github.com'
    HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
               'Authorization': f'token {TOKEN}'}

    def __init__(self, repo_link, since, until, branch='master'):
        self.repo_link = repo_link
        self.since = date_formatter(since) if since is not None else None
        self.until = date_formatter(until) if until is not None else None
        self.branch = branch
        self.conn = HTTPSConnection(self.BASE_URL)

    def _make_request(self, url):
        self.conn.request("GET", url, headers=self.HEADERS)
        res = self.conn.getresponse()
        data = res.read()
        json_data = json.loads(data.decode("utf-8"))
        return json_data

    @property
    def _owner_and_repo_name(self):
        pattern = re.compile('https://github.com/([a-zA-Z0-9-]+/[a-zA-Z0-9-]+)')
        result = re.search(pattern, self.repo_link)
        return result.group(1)

    @property
    def _branch_sha(self):
        url = f'/repos/{self._owner_and_repo_name}/branches/{self.branch}'
        json_data = self._make_request(url)
        return json_data['commit']['sha']

    def contributions(self):
        page = 1
        flag = True
        contributions = {}
        since = f'&since={self.since}' if self.since is not None else ''
        until = f'&until={self.until}' if self.until is not None else ''
        while flag:
            relative_url = f"/repos/{self._owner_and_repo_name}/commits?per_page=200&sha={self._branch_sha}&page={page}{since}{until}"
            json_data = self._make_request(relative_url)
            page += 1
            if json_data:
                for js in json_data:
                    try:
                        if js['author']['login'] in contributions:
                            contributions[js['author']['login']] += 1
                        else:
                            contributions[js['author']['login']] = 1
                    except TypeError:
                        # В некоторых коммитах отсутствует значение поля author,
                        # поэтому решил в таких случаях вместо login использовать name
                        if js['commit']['author']['name'] in contributions:
                            contributions[js['commit']['author']['name']] += 1
                        else:
                            contributions[js['commit']['author']['name']] = 1
            else:
                flag = False

        # with open('result.json', 'w') as fp:
        #     json.dump(contributions, fp)

        return contributions

    def pull_requests(self):
        pull_states = {'open': 0,
                       'closed': 0}
        old_pulls = 0
        flag = True
        page = 1
        while flag:
            url = f'/repos/{self._owner_and_repo_name}/pulls?per_page=200&state=all&page={page}'
            page += 1
            json_data = self._make_request(url)
            if json_data:
                for element in json_data:
                    if element['state'] == 'open':
                        pull_states['open'] += 1
                        created_at = datetime.strptime(element['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                        days = (datetime.now() - created_at).days
                        if days > 30:
                            old_pulls += 1
                    elif element['state'] == 'closed':
                        pull_states['closed'] += 1
            else:
                flag = False
        return pull_states, old_pulls

    def issues(self):
        # Есть сомнения по поводу этого метода,
        # т.к. он практически идентичен pull_requests,
        # но решил все-таки оставить.
        issues_states = {'open': 0,
                         'closed': 0}
        old_issues = 0
        page = 1
        flag = True
        while flag:
            url = f'/repos/{self._owner_and_repo_name}/issues?per_page=200&state=all&page={page}'
            page += 1
            json_data = self._make_request(url)
            if json_data:
                for element in json_data:
                    if 'pull_request' in element.keys():
                        continue
                    else:
                        if element['state'] == 'open':
                            issues_states['open'] += 1
                            created_at = datetime.strptime(element['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                            days = (datetime.now() - created_at).days
                            if days > 14:
                                old_issues += 1
                        elif element['state'] == 'closed':
                            issues_states['closed'] += 1
            else:
                flag = False
        return issues_states, old_issues
