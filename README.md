# Github Data Extraction Tools

#### These are a collection of scripts designed to extract commit, issue and issue comment information from a set of chosen repositories, to a csv file, stored on your local machine. 

Before you begin:

Install the python requests library by running the following line in your terminal:

    pip install requests

(or if using python3)

    pip3 install requests


Generate a GitHub Token:

1. Go into your GitHub settings
2. Select Developer settings
3. Select Personal Access Tokens
4. Select 'Tokens (classic)'
5. Select 'Generate new token'
6. Select 'classic'
7. Select all relevant fields
8. Press 'Generate token'
9. Copy and save your token somewhere safe

When complete, paste your token into the 'GITHUB_TOKEN' line of code. 

GitHub API URLs are required to use these scripts. (https://api.github.com/repos/owner/reponame)

Simply paste the URLs of the repositories you want to run the script with in 'github_repo_urls'. If you have multiple URLS paste as such:

    github_repo_urls = [
    'https://api.github.com/repos/owner/reponame1',
    'https://api.github.com/repos/owner/reponame2',
    # Add more repositories as needed
    ]  

After the above steps have been completed, you are ready to run your script!

### What script should I use?

To extract commit information use gitcommitsauth.py. 

To extract issue information use gitissuesauth.py

To extract issue comments use gitcommentsauth.py

### What does each script save?

gitcommitsauth.py - (Repo Name, Commit ID, Commit Author, Commit Date, Commit Message, Commit Additions, Deletions and Total Changes are saved into a csv file)

gitissuesauth2.py - (Repo Name, Issue Label, Issue ID, Issue Author, Issue Title, Issue Body, Issue State, Created At, Updated At and Closed At are saved into a csv file)

gitcommentsauth2.py - (Repo Name, Issue ID, Comment Author, Comment Body and Comment Date are saved into a csv file)


