import os
from github import Github

g = Github(login_or_token="e6a0f426c665b4050f4efb8210131b6f33899a91")
for repo in g.get_user().get_repos():
    print(repo.name)

