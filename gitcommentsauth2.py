import csv
import requests
import time

GITHUB_TOKEN = #insert github token here

    github_repo_urls = [
        #insert api urls here
    ]

session = requests.Session()  # Create session to make requests

def fetch_issues(repo_url):
    issues = []  # Where issues will be stored
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

def fetch_comments(repo_url, issue_number):
    comments = []  # Where comments are stored
    page = 1
    while True:
        comments_url = f"{repo_url}/issues/{issue_number}/comments"
        params = {'page': page, 'per_page': 30}  # 30 comments per page
        headers = {'Authorization': f'token {GITHUB_TOKEN}'}
        
        response = session.get(comments_url, params=params, headers=headers)
        try:
            response.raise_for_status()  # Raise an exception for HTTP errors
            page_comments = response.json()  # Parse JSON response
            if not page_comments:
                break  # Exit loop if no more comments are returned
            comments.extend(page_comments)
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
    
    return comments  # Return the list of comments

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
    
def save_comments_to_csv(repo_name, issue_number, comments, output_file):
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Repository', 'Issue ID', 'Comment Author', 'Comment Body', 'Comment Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header only if file is empty
        if csvfile.tell() == 0:
            writer.writeheader()

        for comment in comments:
            writer.writerow({'Repository': repo_name,
                             'Issue ID': issue_number,
                             'Comment Author': comment['user']['login'],
                             'Comment Body': comment['body'],
                             'Comment Date': comment['created_at']})

if __name__ == "__main__":
    output_file = "github_issue_comments.csv" #change this to what you want your output file to be called
    for repo_url in github_repo_urls:
        check_rate_limit()  # Check rate limit before fetching issues
        repo_name = repo_url.split("/")[-1]  # Extract repository name from URL
        issues = fetch_issues(repo_url)
        for issue in issues:
            check_rate_limit()  # Check rate limit before fetching comments
            issue_number = issue['number']  # Extract issue number
            comments = fetch_comments(repo_url, issue_number)
            if comments:
                save_comments_to_csv(repo_name, issue_number, comments, output_file)
            else:
                print(f"No comments found for {repo_name} - Issue {issue_number}")
