# Github Data Extraction Tools

### This is designed to extract commit, issue and issue comment data from a set of chosen repositories, to csv files, stored on your local machine. 

### Before you begin:

#### Save the main.py file onto your device.

#### Install the python requests library by running the following line in your terminal:

    pip install requests

#### Install the python pyyaml library by running the following line in your terminal:

    pip install pyyaml

#### Generate a GitHub Token:

1. Go into your GitHub settings
2. Select Developer settings
3. Select Personal Access Tokens
4. Select 'Tokens (classic)'
5. Select 'Generate new token'
6. Select 'classic'
7. Select all relevant fields
8. Press 'Generate token'
9. Copy and save your token somewhere safe as you will need it

#### GitHub API URLs are required to run this code. (https://api.github.com/repos/owner/reponame)

#### Create a 'config.yaml' file in the directory of the project. Use this structure to list your Github Token and the repositories you want to fetch data from:

    github_token: paste_your_token_here
    repositories:
      - https://api.github.com/repos/owner/reponame1
      - https://api.github.com/repos/owner/reponame2
      - https://api.github.com/repos/owner/reponame3
        #add as many repositories as you like

#### After the above steps have been completed, you are ready to run your script!

### When prompted, input a number into the terminal based on what type(s) of data you want to fetch:

#### '1' for commits, '2' for issues, '3' for comments, '4' for all.

### What data is saved?

Commits - (Repo Name, Commit ID, Commit Author, Commit Date, Commit Message, Commit Additions, Deletions and Total Changes are saved into a file called github_commits.csv)

Issues - (Repo Name, Issue Label, Issue ID, Issue Author, Issue Title, Issue Body, Issue State, Created At, Updated At and Closed At are saved into a file called github_issues.csv)

Issue Comments - (Repo Name, Issue ID, Comment Author, Comment Body and Comment Date are saved into a file called github_comments.csv)
