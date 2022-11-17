---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''

---

⚠ REPORTS WITHOUT THIS INFORMATION WILL NOT BE ACCEPTED! PLEASE RESPECT OTHER'S TIME! ⚠

Please make a proper bug report. The template is put here for a reason, edit it according to your situation.

It's not cool to just throw lines of log without any context and comments. You have to be specific if you want people to help you.

👆

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Desktop (please complete the following information):**
 - OS: [e.g. Windows]
 - Python version [e.g. 3.x]
 - Miner version
 - Other relevant software versions

**Log**
How to provide a DEBUG log:
1. Set
```py
logger_settings=LoggerSettings(
	save=True,
	console_level=logging.INFO,
	file_level=logging.DEBUG,
	less=True,
```
in your runner script (`run.py`).

2. Start the miner, wait for the error, then stop the miner and post the contents of the log file (`logs\username.log`) to https://gist.github.com/ and post a link here.

3. Create another gist with your console output, just in case. Paste a link here as well.

**Additional context**
Add any other context about the problem here.
