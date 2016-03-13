import os
from sh import git

import logging
from ..logger import getlogger
logger = getlogger()

appdir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_repo(repodir):
    repo = None
    if not os.path.exists(repodir):
        os.makedirs(repodir)
    repo = git.init(repodir)
    return repo


def git_log(filepath, commit):
    #repo = appdir + "/static/repository"
    repo = appdir + "/" + "/".join(filepath.split("/")[0:-1])
    d = None
    try:
        d = git(
            "--git-dir", repo + "/.git",
            "--work-tree", repo,
            "--no-pager",
            "log", "--oneline", commit, "-2",
            '--pretty=format:%H', '--', appdir + "/" + filepath
        )
        #c = "..".join(d.split("\n"))
    except Exception as e:
        #d = str(e)
        return None
    return d


def git_diff(filepath, commit):
    repo = appdir + "/static/repository"
    d = None
    try:
        d = git(
            "--git-dir", repo + "/.git",
            "--work-tree", repo,
            "--no-pager",
            "log", "--no-color",  commit,
            "-p", "-1", appdir + "/" + filepath
        )
    except Exception as e:
        d = str(e)
    return d


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
        logger.error(filepath)
        #logger.error(str(e))
        commit = git(
            "--git-dir", repo + "/.git",
            "--work-tree", repo,
            "--no-pager",
            'log', '-1', '--pretty=format:%H', '--', filepath
        ).strip()
    logger.debug(commit)
    return commit

