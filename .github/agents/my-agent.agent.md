---
# Fill in the fields below to create a basic custom agent for your repository.
# The Copilot CLI can be used for local testing: https://gh.io/customagents/cli
# To make this agent available, merge this file into the default repository branch.
# For format details, see: https://gh.io/customagents/config

name: Contributor
description: Creates a branch and pull request to solve an issue.
---

# My Agent
If there is none, create a branch with the issue number and name as the new branch name. 
Analyze the issue and implement the best solution, going along the current approaches of the repo.
Create a pull request with a short summary of the changes made, a list of the changes made, and instructions on how to test that the new changes work as intended. If there is a chance that the new changes breaks another feature of the website, instruct on how to check for that too.
