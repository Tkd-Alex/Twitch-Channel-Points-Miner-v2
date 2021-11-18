# Contributing to this repository

## Getting started

Before you begin:
- Have you read the [code of conduct](CODE_OF_CONDUCT.md)?
- Check out the [existing issues](https://github.com/Tkd-Alex/Twitch-Channel-Points-Miner-v2/issues) & see if there is already an opened issue.

### Ready to make a change? Fork the repo

Fork using GitHub Desktop:

- [Getting started with GitHub Desktop](https://docs.github.com/en/desktop/installing-and-configuring-github-desktop/getting-started-with-github-desktop) will guide you through setting up Desktop.
- Once Desktop is set up, you can use it to [fork the repo](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/cloning-and-forking-repositories-from-github-desktop)!

Fork using the command line:

- [Fork the repo](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo#fork-an-example-repository) so that you can make your changes without affecting the original project until you're ready to merge them.

Fork with [GitHub Codespaces](https://github.com/features/codespaces):

- [Fork, edit, and preview](https://docs.github.com/en/free-pro-team@latest/github/developing-online-with-codespaces/creating-a-codespace) using [GitHub Codespaces](https://github.com/features/codespaces) without having to install and run the project locally.

### Open a pull request
When you're done making changes, and you'd like to propose them for review, use the [pull request template](#pull-request-template) to open your PR (pull request).

### Submit your PR & get it reviewed
- Once you submit your PR, other users from the community will review it with you. The first thing you're going to want to do is a [self review](#self-review).
- After that, we may have questions. Check back on your PR to keep up with the conversation.
- Did you have an issue, like a merge conflict? Check out our [git tutorial](https://lab.github.com/githubtraining/managing-merge-conflicts) on resolving merge conflicts and other issues.

### Your PR is merged!
Congratulations! The whole GitHub community thanks you. :sparkles:

Once your PR is merged, you will be proudly listed as a contributor in the [contributor chart](https://github.com/Tkd-Alex/Twitch-Channel-Points-Miner-v2/graphs/contributors).

### Keep contributing as you use GitHub Docs

Now that you're a part of the GitHub Docs community, you can keep participating in many ways.

**Learn more about contributing:**

- [Types of contributions :memo:](#types-of-contributions-memo)
  - [:beetle: Issues](#beetle-issues)
  - [:hammer_and_wrench: Pull requests](#hammer_and_wrench-pull-requests)
- [Starting with an issue](#starting-with-an-issue)
  - [Labels](#labels)
- [Opening a pull request](#opening-a-pull-request)
- [Reviewing](#reviewing)
  - [Self review](#self-review)
  - [Pull request template](#pull-request-template)
  - [Python Styleguide](#python-styleguide)
  - [Suggested changes](#suggested-changes)

## Types of contributions :memo:
You can contribute to the Twitch-Channel-Points-Miner-v2 in several ways. Bug reporting, pull request, propose new features, fork, donate, and much more :muscle: .

### :beetle: Issues
[Issues](https://docs.github.com/en/github/managing-your-work-on-github/about-issues) are used to report a bug, propose new features, or ask for help. When you open an issue, please use the appropriate template and label.

### :hammer_and_wrench: Pull requests
A [pull request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests) is a way to suggest changes in our repository.

When we merge those changes, they should be deployed to the live site within 24 hours. :earth_africa: To learn more about opening a pull request in this repo, see [Opening a pull request](#opening-a-pull-request) below.

## Starting with an issue
You can browse existing issues to find something that needs help!

### Labels
Labels can help you find an issue you'd like to help with.
- The `bug` label is used when something isn't working
- The `documentation` label is used when you suggest improvements or additions to documentation (README.md update)
- The `duplicate` label is used when this issue or pull request already exists
- The `enhancement` label is used when you ask for / or propose a new feature or request
- The `help wanted` is used when you need help with something
- The `improvements` label is used when you would suggest improvements on already existing features
- The `invalid` label is used for a non-valid issue
- The `question` label is used for further information is requested
- The `wontfix` label is used if we will not work on it

## Opening a pull request
You can use the GitHub user interface :pencil2: for minor changes, like fixing a typo or updating a readme. You can also fork the repo and then clone it locally to view changes and run your tests on your machine.

### Self review
You should always review your own PR first.

For content changes, make sure that you:
- [ ] Confirm that the changes address every part of the content design plan from your issue (if there are differences, explain them).
- [ ] Review the content for technical accuracy.
- [ ] Review the entire pull request using the checklist present in the template.
- [ ] Copy-edit the changes for grammar, spelling, and adherence to the style guide.
- [ ] Check new or updated Liquid statements to confirm that versioning is correct.
- [ ] Check that all of your changes render correctly in staging. Remember, that lists and tables can be tricky.
- [ ] If there are any failing checks in your PR, troubleshoot them until they're all passing.

### Pull request template
When you open a pull request, you must fill out the "Ready for review" template before we can review your PR. This template helps reviewers understand your changes and the purpose of your pull request.

### Python Styleguide
All Python code is formatted with [Black](https://github.com/psf/black) using the default settings. Your code will not be accepted if it is not blackened.
You can use the pre-commit hook.
```
pip install pre-commit
pre-commit install
```

### Suggested changes
We may ask for changes to be made before a PR can be merged, either using [suggested changes](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/incorporating-feedback-in-your-pull-request) or pull request comments. You can apply suggested changes directly through the UI. You can make any other changes in your fork, then commit them to your branch.

As you update your PR and apply changes, mark each conversation as [resolved](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/commenting-on-a-pull-request#resolving-conversations).
