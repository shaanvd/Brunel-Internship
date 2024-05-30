import csv
import requests
import time

ACCESS_TOKEN = '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'

github_repo_urls = [
    "https://api.github.com/repos/OpenZeppelin/openzeppelin-contracts",
    "https://api.github.com/repos/Dexaran/ERC223-token-standard",
    "https://api.github.com/repos/gr3yc4t/ERC20-Staking-Machine",
    "https://api.github.com/repos/1x-eng/Decentralized_eCom",
    "https://api.github.com/repos/lidofinance/core",
    "https://api.github.com/repos/aave/gho-core",
    "https://api.github.com/repos/jklepatch/eattheblocks",
    "https://api.github.com/repos/compound-finance/compound-protocol",
    "https://api.github.com/repos/aragon/aragonOS",
    "https://api.github.com/repos/ProjectOpenSea/seaport"
]

session = requests.Session()

# Function to check rate limit
def check_rate_limit():
    rate_limit_url = "https://api.github.com/rate_limit"
    headers = {'Authorization': f'token {ACCESS_TOKEN}'}
    
    response = session.get(rate_limit_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching rate limit: {response.status_code}, Response: {response.text}")
    
    rate_limit_info = response.json()
    if 'rate' not in rate_limit_info:
        raise KeyError(f"'rate' key not found in rate limit info. Response: {rate_limit_info}")
    
    remaining_requests = rate_limit_info['rate']['remaining']
    reset_time = rate_limit_info['rate']['reset']
    
    if remaining_requests == 0:
        current_time = time.time()
        wait_time = reset_time - current_time
        if wait_time > 0:
            print(f"Rate limit exceeded. Waiting for {wait_time:.0f} seconds.")
            time.sleep(wait_time)

# Function to fetch commits
def fetch_commits(repo_url):
    headers = {
        "Authorization": f"token {ACCESS_TOKEN}",
    }
    commits = []
    page = 1
    
    while True:
        check_rate_limit()  # Check rate limit before making API call
        try:
            response = session.get(repo_url + "/commits", headers=headers, params={"page": page, "per_page": 100})
            response.raise_for_status()
            page_commits = response.json()
            if not page_commits:
                break
            commits.extend(page_commits)
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying...")
            time.sleep(5)
            continue
    
    return commits

# Function to fetch detailed commit information
def fetch_commit_details(repo_url, sha):
    headers = {
        "Authorization": f"token {ACCESS_TOKEN}",
    }
    check_rate_limit()  # Check rate limit before making API call
    for _ in range(3):  # Retry up to 3 times
        try:
            response = session.get(repo_url + "/commits/" + sha, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request for commit details failed: {e}. Retrying...")
            time.sleep(5)
    raise Exception(f"Failed to fetch commit details after 3 attempts for {repo_url} with SHA {sha}")

# Function to write commits to CSV
def write_commits_to_csv(commits, repo_name, writer):
    for commit in commits:
        sha = commit["sha"]
        author = commit["commit"]["author"]["name"]
        date = commit["commit"]["author"]["date"]
        message = commit["commit"]["message"]
        
        # Fetch commit information
        details = fetch_commit_details(repo_name, sha)
        additions = details["stats"]["additions"]
        deletions = details["stats"]["deletions"]
        total_changes = additions + deletions
        
        writer.writerow([repo_name, sha, author, date, message, additions, deletions, total_changes])

# Main execution
if __name__ == "__main__":
    csv_filename = "github_commits.csv"
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Repository", "Commit ID", "Author", "Date", "Message", "Additions", "Deletions", "Total Changes"])  # CSV header
        
        for repo_url in github_repo_urls:
            print(f"Fetching commits for repository: {repo_url}")
            repo_commits = fetch_commits(repo_url)
            repo_name = repo_url.split("/")[-1]  # Extract repository name from URL
            print(f"Writing commits data for repository {repo_name} to {csv_filename}")
            write_commits_to_csv(repo_commits, repo_url, writer)
            print(f"Commits data with changes for repository {repo_name} has been written to {csv_filename}")
            
