import subprocess

def get_latest_commit_hash():
    # Runs 'git rev-parse HEAD' to grab the latest commit hash
    result = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
    return result.decode('utf-8').strip()

def get_latest_commit_details():
    # Runs 'git log -1' to get formatted hash, author, date, and subject
    format_str = "%H%n%an%n%ad%n%s"
    result = subprocess.check_output(['git', 'log', '-1', f'--pretty=format:{format_str}'])
    details = result.decode('utf-8').strip().split('\n')
    return {
        "hash": details[0],
        "author": details[1],
        "date": details[2],
        "message": details[3]
    }

def get_patch_notes():
    latest_commit_details = get_latest_commit_details()
    return f"Hey guys! I just got a new update! 🚀🚀\nLatest changes: ```{latest_commit_details['message']}```"