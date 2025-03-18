# Issue Automation Test

This project demonstrates an automated GitHub issue creation process. It dynamically detects errors, generates detailed reports, and submits them as issues to a specified GitHub repository.

## Features
- Automatically detects runtime errors (exceptions).
- Dynamically retrieves and confirms the repository name.
- Creates detailed GitHub issues with error details, stack traces, and unique exception hashes to prevent duplicates.
- Includes a setup process for saving configuration data (`config.json`) - **Note: Saves in plain text** 

## Usage
### Prerequisites
- Python 3.10 or higher.
- A GitHub account with access to the desired repository.
- A Personal Access Token (PAT) with the following scopes:
  - `repo` (for private repositories).
  - `public_repo` (for public repositories).

### Setup Process
1. Clone this repository:
   ```bash
   git clone https://github.com/RedNeckSnailSpit/IssueAutomationTest.git
    ```
2. Navigate to the repository directory:
   ```bash
   cd IssueAutomationTest
   ```
3. Run the script as-is and go through the setup process.
   ```bash
   python main.py
   ```
4. Once completed, you should see the `config.json` file in the repository - Keep this file safe, it contains your GitHub token.

## Credit
Please see the [CREDITS](CREDITS.md) for this project.

## License
Please see the [LICENSE](LICENSE.md) for this project.