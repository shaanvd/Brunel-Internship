import csv
import requests
import time
import yaml
from typing import List, Dict, Any

def load_config_from_yaml(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        return config

config = load_config_from_yaml('config.yaml')
GITHUB_TOKEN = config['github_token']
GITHUB_REPO_URLS = config['repositories']

class GitHubUtils:
    def __init__(self, token: str):
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'token {token}'})

    def check_rate_limit(self):
        for attempt in range(3):
            try:
                response = self.session.get("https://api.github.com/rate_limit")
                response.raise_for_status()
                rate_limit_info = response.json()
                remaining_requests = rate_limit_info['rate']['remaining']
                reset_time = rate_limit_info['rate']['reset']

                if remaining_requests == 0:
                    wait_time = reset_time - time.time()
                    if wait_time > 0:
                        print(f"Rate limit exceeded. Waiting for {wait_time:.0f} seconds.")
                        time.sleep(wait_time)
                return
            except requests.exceptions.HTTPError as e:
                if response.status_code == 503:
                    print(f"Attempt {attempt + 1}: Service unavailable. Retrying...")
                    time.sleep(2 ** attempt)
                else:
                    raise

class GitHubDataFetcher:
    def __init__(self, utils: GitHubUtils):
        self.utils = utils

    def fetch_data(self, url: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if params is None:
            params = {}
        data = []
        page = 1

        while True:
            self.utils.check_rate_limit()
            for attempt in range(5):
                try:
                    response = self.utils.session.get(url, params={**params, 'page': page, 'per_page': 100})
                    if response.status_code == 403:
                        print(f"Access forbidden for URL: {url}. Retrying...")
                        time.sleep(2 ** attempt)
                        continue
                    response.raise_for_status()
                    page_data = response.json()
                    if not page_data:
                        break
                    data.extend(page_data)
                    page += 1
                    break
                except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
                    print(f"Attempt {attempt + 1}: Error fetching data from {url}. Error: {e}. Retrying...")
                    time.sleep(2 ** attempt)
            else:
                print(f"Failed to fetch data from {url} after multiple attempts.")
                break

        return data

class GitHubOperationFactory:
    def __init__(self, fetcher: GitHubDataFetcher, repo_urls: List[str]):
        self.fetcher = fetcher
        self.repo_urls = repo_urls

    def create_operation(self, choice: str):
        if choice == '1':
            return GitHubCommits(self.fetcher, self.repo_urls)
        elif choice == '2':
            return GitHubIssues(self.fetcher, self.repo_urls)
        elif choice == '3':
            return GitHubComments(self.fetcher, self.repo_urls)
        elif choice == '4':
            return GitHubAllData(self.fetcher, self.repo_urls)
        else:
            raise ValueError("Invalid choice")

class GitHubCommits:
    def __init__(self, fetcher: GitHubDataFetcher, repo_urls: List[str]):
        self.fetcher = fetcher
        self.repo_urls = repo_urls

    def fetch_commits(self, repo_url: str) -> List[Dict[str, Any]]:
        return self.fetcher.fetch_data(repo_url + "/commits")

    def fetch_commit_details(self, repo_url: str, sha: str) -> Dict[str, Any]:
        self.fetcher.utils.check_rate_limit()

        for attempt in range(3):
            try:
                response = self.fetcher.utils.session.get(f"{repo_url}/commits/{sha}")
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}: Failed to fetch commit details for {repo_url} with SHA {sha}. Error: {e}")
                time.sleep(5)

        raise Exception(f"Failed to fetch commit details after 3 attempts for {repo_url} with SHA {sha}")

    def save_commits_to_csv(self, commits: List[Dict[str, Any]], repo_url: str, writer: csv.writer):
        for commit in commits:
            sha = commit["sha"]
            author = commit["author"]["login"] if commit["author"] else "Unknown"
            date = commit["commit"]["author"]["date"]
            message = commit["commit"]["message"]

            details = self.fetch_commit_details(repo_url, sha)
            additions = details["stats"]["additions"]
            deletions = details["stats"]["deletions"]
            total_changes = additions + deletions

            writer.writerow([repo_url.split('/')[-1], sha, author, date, message, additions, deletions, total_changes])

    def execute(self):
        commits_output_file = "github_commits.csv"
        with open(commits_output_file, mode='a', newline='') as commits_file:
            commits_writer = csv.writer(commits_file)
            if commits_file.tell() == 0:
                commits_writer.writerow(["Repository", "Commit ID", "Author", "Date", "Message", "Additions", "Deletions", "Total Changes"])

            for repo_url in self.repo_urls:
                repo_name = repo_url.split("/")[-1]
                print(f"Fetching commits for repository: {repo_name}")
                repo_commits = self.fetch_commits(repo_url)
                self.save_commits_to_csv(repo_commits, repo_url, commits_writer)
                print(f"Commits data with changes for repository {repo_name} has been written to {commits_output_file}")

class GitHubIssues:
    def __init__(self, fetcher: GitHubDataFetcher, repo_urls: List[str]):
        self.fetcher = fetcher
        self.repo_urls = repo_urls

    def fetch_issues(self, repo_url: str) -> List[Dict[str, Any]]:
        return self.fetcher.fetch_data(f"{repo_url}/issues", {'state': 'all', 'per_page': 30})

    def save_issues_to_csv(self, issues: List[Dict[str, Any]], output_file: str):
        with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Repository', 'Issue Label', 'Issue ID', 'Issue Title', 'Issue Body', 'State', 'Created At',
                          'Updated At', 'Closed At', 'Author']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if csvfile.tell() == 0:
                writer.writeheader()

            for issue in issues:
                labels = ', '.join(label['name'] for label in issue['labels'])
                closed_at = issue.get('closed_at', 'N/A')
                writer.writerow({
                    'Repository': issue['repository_url'].split('/')[-1],
                    'Issue Label': labels,
                    'Issue ID': issue['number'],
                    'Issue Title': issue['title'],
                    'Issue Body': issue['body'],
                    'State': issue['state'],
                    'Created At': issue['created_at'],
                    'Updated At': issue['updated_at'],
                    'Closed At': closed_at,
                    'Author': issue['user']['login']
                })

    def execute(self):
        issues_output_file = "github_issues.csv"
        for repo_url in self.repo_urls:
            repo_name = repo_url.split("/")[-1]
            repo_issues = self.fetch_issues(repo_url)
            if repo_issues:
                self.save_issues_to_csv(repo_issues, issues_output_file)
            else:
                print(f"No issues found for {repo_url}")

class GitHubComments:
    def __init__(self, fetcher: GitHubDataFetcher, repo_urls: List[str]):
        self.fetcher = fetcher
        self.repo_urls = repo_urls

    def fetch_comments(self, repo_url: str, issue_number: int) -> List[Dict[str, Any]]:
        return self.fetcher.fetch_data(f"{repo_url}/issues/{issue_number}/comments", {'per_page': 30})

    def save_comments_to_csv(self, repo_name: str, issue_number: int, comments: List[Dict[str, Any]], output_file: str):
        with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Repository', 'Issue ID', 'Comment Author', 'Comment Body', 'Comment Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if csvfile.tell() == 0:
                writer.writeheader()

            for comment in comments:
                writer.writerow({
                    'Repository': repo_name,
                    'Issue ID': issue_number,
                    'Comment Author': comment['user']['login'],
                    'Comment Body': comment['body'],
                    'Comment Date': comment['created_at']
                })

    def execute(self):
        comments_output_file = "github_comments.csv"
        for repo_url in self.repo_urls:
            repo_name = repo_url.split("/")[-1]
            issues_fetcher = GitHubIssues(self.fetcher, self.repo_urls)
            repo_issues = issues_fetcher.fetch_issues(repo_url)
            for issue in repo_issues:
                issue_number = issue['number']
                repo_comments = self.fetch_comments(repo_url, issue_number)
                if repo_comments:
                    self.save_comments_to_csv(repo_name, issue_number, repo_comments, comments_output_file)
                else:
                    print(f"No comments found for issue {issue_number} in {repo_url}")

class GitHubAllData:
    def __init__(self, fetcher: GitHubDataFetcher, repo_urls: List[str]):
        self.commits = GitHubCommits(fetcher, repo_urls)
        self.issues = GitHubIssues(fetcher, repo_urls)
        self.comments = GitHubComments(fetcher, repo_urls)

    def execute(self):
        self.commits.execute()
        self.issues.execute()
        self.comments.execute()

def main():
    utils = GitHubUtils(GITHUB_TOKEN)
    fetcher = GitHubDataFetcher(utils)
    factory = GitHubOperationFactory(fetcher, GITHUB_REPO_URLS)

    print("Choose an option:")
    print("1. Fetch and save commits")
    print("2. Fetch and save issues")
    print("3. Fetch and save comments")
    print("4. Fetch and save all data (commits, issues, comments)")

    choice = input("Enter the number corresponding to your choice: ").strip()
    try:
        operation = factory.create_operation(choice)
        operation.execute()
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
