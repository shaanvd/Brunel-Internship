import csv
import requests
import time


GITHUB_TOKEN = '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'

session = requests.Session()

def fetch_issues(repo_url):
    issues = []
    page = 1
    while True:
        issues_url = f"{repo_url}/issues"
        params = {'state': 'all', 'page': page, 'per_page': 30}  # Include both open and closed issues, 30 per page
        headers = {'Authorization': f'token {GITHUB_TOKEN}'}
        
        response = session.get(issues_url, params=params, headers=headers)
        try:
            response.raise_for_status()  # Raise an exception for HTTP errors
            page_issues = response.json()  # Parse JSON response
            if not page_issues:
                break  
            issues.extend(page_issues)
            page += 1  # Increment page number for next request
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            break
        except ValueError as json_err:
            print(f"JSON decoding error occurred: {json_err}")
            print(f"Response content: {response.text}")  # Print response content for debugging
            break
        except Exception as err:
            print(f"An error occurred: {err}")
            break
    
    return issues  # Return the list of issues

def check_rate_limit():
    rate_limit_url = "https://api.github.com/rate_limit"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    
    response = session.get(rate_limit_url, headers=headers)
    rate_limit_info = response.json()
    remaining_requests = rate_limit_info['rate']['remaining']
    reset_time = rate_limit_info['rate']['reset']
    
    if remaining_requests == 0:
        current_time = time.time()
        wait_time = reset_time - current_time
        if wait_time > 0:
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
            time.sleep(wait_time)

def save_issues_to_csv(issues, output_file):
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Repository', 'Issue Label', 'Issue ID', 'Issue Title', 'Issue Body', 'State', 'Created At', 'Updated At', 'Author']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header only if file is empty
        if csvfile.tell() == 0:
            writer.writeheader()

        for issue in issues:
            labels = ', '.join([label['name'] for label in issue['labels']])
            writer.writerow({'Repository': issue['repository_url'].split('/')[-1],
                             'Issue Label': labels,
                             'Issue ID': issue['number'],
                             'Issue Title': issue['title'],
                             'Issue Body': issue['body'],
                             'State': issue['state'],
                             'Created At': issue['created_at'],
                             'Updated At': issue['updated_at'],
                             'Author': issue['user']['login']})

# repo urls
if __name__ == "__main__":
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
    output_file = "github_issues_4.csv"

    for repo_url in github_repo_urls:
        check_rate_limit()  # Check rate limit before fetching issues
        repo_name = repo_url.split("/")[-1]  # Extract repository name from URL
        issues = fetch_issues(repo_url)
        if issues:
            save_issues_to_csv(issues, output_file)
        else:
            print(f"No issues found for {repo_url}")
