import os
from sh import git

import logging
from ..logger import getlogger
logger = getlogger()

def get_repo(repodir):
        repo = None
        if not os.path.exists(repodir):
                os.makedirs(repodir)
        repo = git.init(repodir)
        return repo
	
def git_commit(filepath, repo):
        commit = None
        try:
	        git(
			"--git-dir", repo + "/.git",
        	        "--work-tree", repo,
                	"add", filepath
		)
                git(
                        "--git-dir", repo + "/.git",
                        "--work-tree", repo,
                        "commit", "-m", "None"
                )
		commit = git(
			"--git-dir", repo + "/.git",
                	"--work-tree", repo,
			"--no-pager",
			'log', '-1', '--pretty=format:%H', '--', filepath
		).strip()
        except Exception as e:
                logger.error(str(filepath))
                #logger.error(str(e))
		commit = git(
			"--git-dir", repo + "/.git",
                	"--work-tree", repo,
			"--no-pager",
			'log', '-1', '--pretty=format:%H', '--', filepath
		).strip()
	logger.debug(commit)
        return commit

