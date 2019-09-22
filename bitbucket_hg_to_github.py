#!/usr/bin/env python3

"""Move Bitbucket Hg repositories to Github."""

# Std
import argparse
import collections
import json
import os
import sys

# Ext
import requests
from github import Github

def my_print(s):
    """Print messages to stand out."""
    print(f"\n==> {s}")

def run_cmd(s):
    """Print the command and then run it. Hacky."""
    my_print(f"Running: {s}")
    r = os.system(s)
    if r != 0:
        print("os.system error!")
        sys.exit(1)

class BitbucketQuery:
    """Wrapper to call Bitbucket APIs."""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.root_api = "https://api.bitbucket.org/2.0"

    def get_repositories(self):
        """Get Hg repo names."""

        repos_info = self.get_repos_info()
        repo_names = []

        for repo in repos_info:
            if repo["scm"] != "hg":
                continue
            repo_names.append(repo["name"])

        return repo_names

    def get_repos_info(self):
        repos_info = []
        api = "{}/repositories/{}".format(self.root_api, self.username)
        while api:
            my_print(f"Get: {api}")
            r = self.call_get_api(api)
            repos_info.extend(r["values"])
            api = r.get("next", None)
        return repos_info

    def call_get_api(self, api):
        r = requests.get(api, auth=(self.username, self.password))
        return r.json()

def get_repo_dpath(repo_name, tmp_root, suffix=""):
    """Get the repo path."""

    dpath = "{}/{}".format(tmp_root, repo_name)
    if suffix:
        dpath = "{}_{}".format(dpath, suffix)
    return dpath

def clone_bb_repos(hg_repo_names, username, tmp_root):
    """Clone Bitbucket Hg repos to local dir."""

    os.makedirs(tmp_root, exist_ok=True)
    for hg_repo_name in hg_repo_names:
        repo_dpath = get_repo_dpath(hg_repo_name, tmp_root)
        clone_cmd = "hg clone ssh://hg@bitbucket.org/{}/{} {}".format(username, hg_repo_name, repo_dpath)
        run_cmd(clone_cmd)

def hg_to_git_name(hg_name, git_suffix, is_bare=False):
    """Convert Hg repo name to Git repo name."""

    bare_suffix = "_bare" if is_bare else ""
    git_name = f"{hg_name}{git_suffix}{bare_suffix}"
    return git_name

def hg_to_git(hg_repo_names, git_repo_names, git_bare_repo_names, tmp_root):
    """Convert Hg repos to Git repos."""

    os.chdir(tmp_root)

    for (hg_repo_name, git_name, git_bare_name) in zip(hg_repo_names, git_repo_names, git_bare_repo_names):

        # Create git bare repo
        cmd = f"git init --bare {git_bare_name}"
        run_cmd(cmd)

        # Push hg to git bare
        my_print(f"cd to: {hg_repo_name}")
        os.chdir(hg_repo_name)
        cmd = "hg bookmarks hg"
        run_cmd(cmd)
        cmd = f"hg push ../{git_bare_name}"
        run_cmd(cmd)
        os.chdir("..")

        # Clone git bare to git
        cmd = f"git clone {git_bare_name} {git_name}"
        print(f"Running: {cmd}")
        run_cmd(cmd)

        # Checkout master
        my_print(f"cd to: {git_name}")
        os.chdir(git_name)
        cmd = "git checkout -b master origin/hg"
        run_cmd(cmd)
        os.chdir("..")

    os.chdir("..")

def push_to_gh(git_repo_names, tmp_root, gh_username):
    """Push local Git repos to Github repos."""

    os.chdir(tmp_root)

    for i, git_repo_name in enumerate(git_repo_names):

        my_print(f"Pushing repo {i}/{len(git_repo_names)}")

        os.chdir(git_repo_name)

        cmd = f"git remote add gh_origin git@github.com:{gh_username}/{git_repo_name}.git"
        run_cmd(cmd)

        cmd = f"git push -u gh_origin master"
        run_cmd(cmd)

        os.chdir("..")

    os.chdir("..")

def create_gh_repos(git_repo_names, gh_access_token):
    """Create new Git repos on Github."""

    gh = Github(gh_access_token)
    gh_user = gh.get_user()
    for git_repo_name in git_repo_names:
        gh_repo = gh_user.create_repo(git_repo_name, private=True)
        my_print(f"Created Github repo: {gh_repo.full_name}")

def get_args():

    aparser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
    aparser.add_argument("--create_gh_repos", action="store_true", default=False, help="Create Github repos for Bitbucket Hg repos")
    aparser.add_argument("--push_gh_repos", action="store_true", default=False, help="Push Bitbucket Hg repos to Github repos")
    aparser.add_argument("--bb_username", type=str, required=True, help="Bitbucket username")
    aparser.add_argument("--bb_app_password", type=str, required=True, help="Bitbucket app password")
    aparser.add_argument("--gh_username", type=str, required=True, help="Github username")
    aparser.add_argument("--gh_access_token", type=str, required=True, help="Github access token")
    aparser.add_argument("--git_suffix", type=str, default="_PRIVATE", help="Suffix for Git repo names")
    aparser.add_argument("--tmp_dir", type=str, default="tmp", help="Dir to use for repo work")
    aparser.add_argument("--do_it", action="store_true", default=False, help="Use when you really want to convert all repos")
    return aparser.parse_args()

def main():

    args = get_args()
    if not args.create_gh_repos and not args.push_gh_repos:
        print("No action specified. Specify either --create_gh_repos or --push_gh_repos")
        return

    # Get your Bitbucket Hg repo names
    bb_query = BitbucketQuery(args.bb_username, args.bb_app_password)
    hg_repo_names = bb_query.get_repositories()

    # Test with 1 repo, unless you are sure
    if not args.do_it:
        hg_repo_names = hg_repo_names[:1]

    git_repo_names = [hg_to_git_name(h, args.git_suffix) for h in hg_repo_names]
    git_bare_repo_names = [hg_to_git_name(h, args.git_suffix, True) for h in hg_repo_names]

    if args.create_gh_repos:
        create_gh_repos(git_repo_names, args.gh_access_token)
    elif args.push_gh_repos:
        clone_bb_repos(hg_repo_names, args.bb_username, args.tmp_dir)
        hg_to_git(hg_repo_names, git_repo_names, git_base_repo_names, args.tmp_dir)
        push_to_gh(git_repo_names, args.tmp_dir, args.gh_username)

if __name__ == "__main__":
    main()
