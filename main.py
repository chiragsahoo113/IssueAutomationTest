import hashlib
import requests
import json
import traceback
import os
import sys
import inspect
import subprocess

from torchgen.executorch.api.et_cpp import return_names

GITHUB_TOKEN = None

# Define the current version of the app
APP_VERSION = "1.0.2a"

# Path to the config file
CONFIG_FILE = "config.json"

# Initialize the repository name
REPO_NAME = None

def get_repo_name():
    """
    Dynamically retrieves the repository name from the Git remote URL
    or prompts the user for input if automatic detection fails.
    """
    try:
        # Run 'git remote get-url origin' to get the remote URL
        remote_url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], text=True
        ).strip()

        # Extract the repo name
        if remote_url.startswith("https://") or remote_url.startswith("http://"):
            repo_name = remote_url.split("/")[-2] + "/" + remote_url.split("/")[-1].replace(".git", "")
        elif remote_url.startswith("git@"):
            repo_name = remote_url.split(":")[-1].replace(".git", "")
        else:
            repo_name = None
    except subprocess.CalledProcessError:
        repo_name = None

    # Confirm with the user or ask for manual input
    if repo_name:
        print(f"Detected repository: {repo_name}")
        user_input = input("Is this correct? (yes/no): ").strip().lower()
        if user_input != "yes":
            repo_name = None

    if not repo_name:
        repo_name = input("Please enter the repository name (e.g., owner/repo): ").strip()

    print(f"Final repository name: {repo_name}")
    return repo_name

def setup():
    """
    Sets up the application by ensuring a valid config.json file exists
    and that required fields (GitHub PAT and repository name) are set.
    Prompts the user for any missing information.
    """
    global REPO_NAME  # Declare as global so we can modify it inside the function
    config = {}

    # Load existing config if available
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as config_file:
            config = json.load(config_file)

    # Ensure GitHub PAT exists in config
    if "github_token" not in config or not config["github_token"].strip():
        print("GitHub Personal Access Token (PAT) is not configured.")
        print(
            "You need to provide a Personal Access Token (PAT) from GitHub to use this script.\n"
            "1. Go to https://github.com/settings/tokens\n"
            "2. Generate a new token with the following required access:\n"
            "   - repo\n"
            "3. Copy the token and paste it below."
        )
        pat = input("Enter your GitHub Personal Access Token (PAT): ").strip()

        if not validate_token(pat):
            print("Exiting setup due to invalid or insecure token.")
            sys.exit(1)

        config["github_token"] = pat
        print("GitHub PAT validated and added to configuration.")

    # Ensure repository name exists in config
    if "repo_name" not in config or not config["repo_name"].strip():
        print("Repository name is not configured.")
        repo_name = get_repo_name()
        config["repo_name"] = repo_name
        REPO_NAME = repo_name  # Set the global REPO_NAME here
    else:
        REPO_NAME = config["repo_name"]  # Load directly from config

    # Save updated config to file
    save_config(config)
    print("Setup complete. Your configuration has been saved to config.json.")

def save_config(data):
    """
    Saves data to config.json, preserving existing keys if the file already exists.
    """
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as config_file:
            config = json.load(config_file)

    config.update(data)  # Add or update the provided data
    with open(CONFIG_FILE, "w", encoding="utf-8") as config_file:
        json.dump(config, config_file, ensure_ascii=False)
    print("Configuration saved to config.json.")

def validate_token(pat):
    """
    Validates the GitHub PAT for required access scopes.
    """
    url = "https://api.github.com/user"
    headers = {"Authorization": f"Bearer {pat}"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Error: Unable to validate token. Please check if it's valid.")
        return False

    scopes = response.headers.get("x-oauth-scopes", "").split(", ")
    if "repo" not in scopes:
        print("Error: Token is missing the required 'repo' scope.")
        return False

    print("Token validation successful.")
    return True

def load_config():
    """
    Loads the configuration from config.json.
    """
    if not os.path.exists(CONFIG_FILE):
        print("Config file not found. Please run the setup process.")
        sys.exit(1)

    with open(CONFIG_FILE) as config_file:
        return json.load(config_file)

def generate_exception_hash(traceback_details):
    """
    Generates a unique hash for an exception based on its traceback details.
    """
    return hashlib.md5(traceback_details.encode()).hexdigest()

def check_for_existing_issue(exception_hash):
    """
    Checks if an issue with the same hash already exists in the GitHub repository.
    """
    url = f"https://api.github.com/repos/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        issues = response.json()
        for issue in issues:
            # Look for the hash in the issue body
            if exception_hash in issue["body"]:
                print(f"Duplicate issue found: {issue['html_url']}")
                return True  # Duplicate found
        return False  # No duplicates found
    else:
        print(f"Failed to fetch issues: {response.status_code}")
        print(response.text)
        return False

def report_issue(exception_title, exception_body, traceback_details):
    """
    Reports an issue to the specified GitHub repository.
    """
    exception_hash = generate_exception_hash(traceback_details)

    if check_for_existing_issue(exception_hash):
        print("Duplicate issue detected. Skipping issue creation.")
        return

    url = f"https://api.github.com/repos/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {
        "title": f"[{APP_VERSION}] {exception_title}",
        "body": (
            f"**Version:** {APP_VERSION}\n\n{exception_body}\n\n"
            f"**Exception Hash:** `{exception_hash}`\n\n"
            f"**Stack Trace:**\n```\n{traceback_details}\n```"
        ),
        "labels": ["bug", "automatic", "Automatic Bug Report", f"version:{APP_VERSION}"]
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print("Bug report successfully created on GitHub!")
    else:
        print(f"Failed to create bug report: {response.status_code}")
        print(response.text)

def simulate_and_report_exception():
    """
    Simulates an exception and reports it to GitHub.
    """
    try:
        # Simulating an error
        sample_list2 = [1, 2, 3]
        print(sample_list2[5])  # This will raise an IndexError
    except Exception as e:
        # Prepare exception details
        exception_title = f"{inspect.currentframe().f_code.co_name} - {type(e).__name__} - {str(e)}"
        exception_body = f"An exception occurred:\n\n- **Type:** {type(e).__name__}\n- **Message:** {str(e)}"
        traceback_details = "".join(traceback.format_exception(type(e), e, e.__traceback__))

        # Call report_issue to create the GitHub issue
        report_issue(exception_title, exception_body, traceback_details)

# Run the test
if __name__ == "__main__":
    setup()
    config = load_config()

    print(f"Repo Name: {REPO_NAME}")

    GITHUB_TOKEN = config.get("github_token")
    if GITHUB_TOKEN is None:
        print("GitHub token not found in config.json. Please run the setup process.")
        sys.exit(1)
    simulate_and_report_exception()
