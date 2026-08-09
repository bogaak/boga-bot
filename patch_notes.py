# Every time Boga bot starts up, post to server to notify of latest changes. 

# import os
# from git import Repo

# # I could also check commit hashes to make sure we collect all commits since last change, but I'm lazy. 
# # Could also add version identifier, but also we've gone thru so many versions without it that it's not worth it. 
# def post_patch_notes():
#     repo = Repo(os.getcwd())
#     latest_commit_message = repo.head.commit.message
#     commit_message = (latest_commit_message.strip())
    
#     note = "Boga bot has received an update! 🚀🚀\n\n Latest changes: ```{commit_message}```"
#     return note.format(commit_message=commit_message)
