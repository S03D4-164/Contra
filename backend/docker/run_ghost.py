#!/usr/bin/env python

import os, sys, tldextract, hashlib
#from sh import git
from ghost import Ghost
import gzip

"""
def git_commit(repo, filepath):
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
		commit = git.rev-parse("HEAD")
	except Exception as e:
		pass
		#print(e)
	return commit
"""
	
def save_resource(savedir, resource):
	no_fetch_extract = tldextract.TLDExtract(suffix_list_url=False)
	ext = no_fetch_extract(resource.url.encode("utf-8"))

	rdir = "/".join([ext.suffix,ext.domain,ext.subdomain])
	savedir = "/".join([repo, rdir])
	if not os.path.exists(savedir):
		os.makedirs(savedir)

	url_md5 = hashlib.md5(resource.url.encode("utf-8")).hexdigest()
	filepath = os.path.join(rdir, url_md5)
	fullpath = os.path.join(savedir, url_md5)

	with open(fullpath, "wb") as output:
		output.write(page.content)
	#commit = git_commit(repo, filepath)
	return filepath
	#print page.http_status
	#print page.headers

def dump_resource(savedir, resource):
	r = {
		"url":resource.url,
		"status_code":resource.status_code,
		"headers":resource.headers,
		"content":resource.content,
	}

if __name__ == "__main__":
	url = None
	if sys.argv[1]:
		url = sys.argv[1].decode("utf-8")
	else:
		sys.exit("no argument.")
	output = "test"
	try:
		output = sys.argv[2]
	except:
		pass
	appdir = "/logs"
	savedir = appdir + "/" +  output
	if not os.path.exists(savedir):
		os.makedirs(savedir)
	ghost = Ghost()
	with ghost.start() as session:
		page, resources = session.open(url)
		import pickle
		result = {
			"status":"Start",
			"page":{},
			"resources":[],
			"capture":None,
		}
		if page:
			result["page"] = {
				"url":page.url,
				"http_status":page.http_status,
				"headers":page.headers,
				"content":page.content,
			}
			capture = savedir + "/capture.png"
			session.capture_to(capture)
			if os.path.isfile(capture):
				with open(capture, 'rb') as c:
					result["capture"] = c.read()
		if resources:
			for r in resources:
				dict = {
					"url":r.url,
					"http_status":r.http_status,
					"headers":r.headers,
					"content":r.content,
				}
				result["resources"].append(dict)

		dump = savedir +  "/ghost.pkl.gz"
		#pickle.dump(result, open(dump, 'wb'))
		with gzip.open(dump, 'wb') as d:
			pickle.dump(result, d)
