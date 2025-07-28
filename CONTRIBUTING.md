# Contributing to KemonoDownloader

Thank you for your interest in contributing to KemonoDownloader! We welcome contributions from the community to help improve this tool for downloading content from Kemono.cr. Whether you’re fixing bugs, adding features, or improving documentation, your efforts are greatly appreciated.

## Table of Contents
- [Community Guidelines](#community-guidelines)
- [How to Contribute](#how-to-contribute)
  - [Follow the Code of Conduct](#follow-the-code-of-conduct)
  - [Check Existing Issues](#check-existing-issues-and-discussions)
  - [Fork and Clone](#fork-and-clone-the-repository)
  - [Development Environment](#set-up-your-development-environment)
  - [Making Changes](#make-your-changes)
  - [Testing](#test-your-changes)
  - [Submitting a Pull Request](#push-and-submit-a-pull-request)
- [Coding Standards](#coding-standards)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Reporting Security Issues](#reporting-security-issues)
- [Getting Help](#getting-help)

## Community Guidelines
To maintain a safe and productive environment, please adhere to the following rules:
- **No Spam or Unverified Links**: Do not post links to unverified or external tools, as they may pose security risks. Such actions will be considered spam and may lead to removal of comments, temporary or permanent bans, or reporting to GitHub.
- **Provide Constructive Feedback**: When reporting issues, include detailed information, reproducible steps, or code samples. Avoid vague or promotional content.
- **Respect Intellectual Property**: Contributions must comply with intellectual property laws and the terms of service of Kemono.cr, as outlined in our [README](README.md).
- **Respect the Community**: Be respectful in all interactions.

Violations of these guidelines may result in warnings, removal of comments, temporary or permanent bans from contributing, or reporting to GitHub for further action. If you notice violations, report them to [izeno.contact@gmail.com](mailto:izeno.contact@gmail.com) or open a private issue labeled "Code of Conduct Violation."

These guidelines are also referenced in our issue templates and pinned in the Issues tab for easy access.

## How to Contribute

### Follow the Code of Conduct
All contributors are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) and [Security Policy](SECURITY.md). By contributing, you agree that your contributions will be licensed under the project’s [MIT License](LICENSE).

### Check Existing Issues and Discussions
Before starting work, check the [Issues page](https://github.com/VoxDroid/KemonoDownloader/issues) and [Discussions tab](https://github.com/VoxDroid/KemonoDownloader/discussions) to see if your idea or bug has already been reported. If not, open an issue using the appropriate template:
- [Bug Report](.github/ISSUE_TEMPLATE/bug_report.yml)
- [Feature Request](.github/ISSUE_TEMPLATE/feature_request.yml)
- [Support Question](.github/ISSUE_TEMPLATE/support_question.yml)
- [Documentation Issue](.github/ISSUE_TEMPLATE/documentation_issue.yml)
- [Security Report](.github/ISSUE_TEMPLATE/security_report.yml)

### Fork and Clone the Repository
1. Fork the repository by clicking the "Fork" button on the [KemonoDownloader GitHub page](https://github.com/VoxDroid/KemonoDownloader).
2. Clone your fork to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/KemonoDownloader.git
   cd KemonoDownloader
   ```

### Development Environment
1. Ensure you have **Python 3.9+** installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install [Briefcase](https://briefcase.readthedocs.io/) for building the app:
   ```bash
   pip install briefcase
   ```
4. Test the app locally to ensure it runs:
   ```bash
   briefcase run
   ```

### Making Changes
- Write clean, readable code following Python best practices (e.g., [PEP 8](https://www.python.org/dev/peps/pep-0008/)).
- If adding a new feature, ensure it aligns with the project’s goals (e.g., enhancing download functionality, improving the UI, or adding support for new file types).
- If fixing a bug, include a clear description of the issue and how your changes address it.
- Update documentation (e.g., `README.md`, `SUPPORT.md`, in-app Help tab) if your changes affect usage or installation.

### Testing
- Test your changes thoroughly on your local machine across supported platforms (Windows, macOS, Linux) if possible, using Briefcase commands (e.g., `briefcase run windows`).
- Ensure the app works as expected (e.g., downloading posts, archiving creators, UI functionality).
- Verify that your changes don’t break existing features or introduce new bugs.

### Push and Submit a Pull Request
1. Push your branch to your fork:
   ```bash
   git push origin feature/add-new-feature
   ```
2. Go to the [KemonoDownloader GitHub page](https://github.com/VoxDroid/KemonoDownloader) and click "New Pull Request."
3. Select your branch and submit the pull request using the [Pull Request template](.github/PULL_REQUEST_TEMPLATE.md). Include:
   - A detailed description of your changes and why they are needed.
   - Links to any issues addressed (e.g., `Fixes #123`).
   - Screenshots or logs, if applicable (e.g., for UI changes).
4. Respond to feedback from maintainers, making updates to your branch as needed.

## Coding Standards
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style (e.g., 4-space indentation, 79-character line length).
- Use descriptive variable and function names (e.g., `download_post` instead of `dp`).
- Add comments for complex logic to improve readability.
- Ensure compatibility with Python 3.9+ and PyQt6.
- Avoid hardcoding values; use constants or configuration files where appropriate.

## Reporting Bugs
If you find a bug but aren’t ready to fix it, open an issue using the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.yml) on the [Issues page](https://github.com/VoxDroid/KemonoDownloader/issues) with:
- A clear description of the bug.
- Steps to reproduce the issue.
- Expected behavior vs. actual behavior.
- Screenshots or logs, if applicable.
- Your operating system, Python version, and KemonoDownloader version.

## Suggesting Features
To suggest a new feature, use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.yml) on the [Issues page](https://github.com/VoxDroid/KemonoDownloader/issues) or start a thread in the [Discussions tab](https://github.com/VoxDroid/KemonoDownloader/discussions). Include:
- A description of the feature and why it would be useful.
- Any potential challenges or considerations.
- Examples or mockups, if applicable.

## Reporting Security Issues
If you discover a security vulnerability, please follow our [Security Policy](SECURITY.md) by:
- Emailing [izeno.contact@gmail.com](mailto:izeno.contact@gmail.com) with details.
- Using the [Security Report template](.github/ISSUE_TEMPLATE/security_report.yml) only if public disclosure is acceptable.
- Opening a private issue labeled "Security Violation" for sensitive matters.

## Getting Help
If you need help with contributing, check the [Support page](SUPPORT.md) for resources or ask a question in the [Discussions tab](https://github.com/VoxDroid/KemonoDownloader/discussions).

Thank you for contributing to KemonoDownloader!