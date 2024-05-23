
import subprocess
import csv
import os

def clone_repositories(repo_urls, destination):  
    for url in repo_urls:  
        repo_name = url.split('/')[-1].split('.')[0]  #extracts name of the repo from url
        repo_path = f"{destination}/{repo_name}"
        if os.path.isdir(repo_path) and os.listdir(repo_path): #checks if directory exists
            print(f"Skipping {repo_name}: Directory already exists and is not empty.")
        else:
            print(f"Cloning {repo_name}")  
            subprocess.run(["git", "clone", url, repo_path])
            
def save_commit_logs(repos, destination): 
    with open(f"{destination}/commits_all.csv", "a", newline='') as csvfile:  #change w to a if file exists
        fieldnames = ['Repository', 'Commit ID', 'Author', 'Date', 'Message']
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)  # Write header row
        for repo in repos:  
            repo_name = repo.split('/')[-1]  
            print(f"Saving commit logs for {repo_name}") 
            try:
                result = subprocess.run(["git", "log"], cwd=repo, capture_output=True, text=True)  #run git log to view commits
                commits_data = result.stdout.split('\ncommit ')[1:]  # splits list of commits into individual lines
                for commit in commits_data: #extracts commit info
                    lines = commit.split('\n')
                    commit_id = lines[0]
                    author_line = lines[1]
                    author = author_line.split(':')[1].strip()
                    date_line = lines[2]
                    date = date_line.split(':')[1].strip()
                    message = '\n'.join(lines[4:])
                    writer.writerow([repo_name, commit_id, author, date, message])
            except Exception as e:
                print(f"Error processing {repo_name}: {e}")

def main():  
    repo_urls = [
        "https://github.com/OpenZeppelin/openzeppelin-contracts",
        "https://github.com/Dexaran/ERC223-token-standard",
        "https://github.com/gr3yc4t/ERC20-Staking-Machine",
        "https://github.com/1x-eng/Decentralized_eCom",
        "https://github.com/lidofinance/core",
        "https://github.com/aave/gho-core",
        "https://github.com/jklepatch/eattheblocks",
        "https://github.com/compound-finance/compound-protocol",
        "https://github.com/aragon/aragonOS",
        "https://github.com/ProjectOpenSea/seaport" 

 
    ]
    destination = "/users/shaan/gitlogger/gitproj"
    os.makedirs(destination, exist_ok=True)
    clone_repositories(repo_urls, destination)
    repos = [f"{destination}/{url.split('/')[-1].split('.')[0]}" for url in repo_urls]
    save_commit_logs(repos, destination)

if __name__ == "__main__":  
    main()
