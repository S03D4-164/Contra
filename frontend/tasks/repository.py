import os
from sh import git

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
			'rev-parse', 'HEAD'
		).strip()
        except Exception as e:
                #print(e)
		print "no commit"
        return commit

