This is a Python script I wrote to move my Bitbucket Mercurial repositories to Github as Git repositories.

Compared to the Frankenstein UI of Git, Mercurial has the perfect elegance and simplicity for personal projects.
So I had been using Bitbucket to host all of my personal projects, numbering almost 100 for about a decade.
When Bitbucket [announced](https://bitbucket.org/blog/sunsetting-mercurial-support-in-bitbucket) that they were shutting down Mercurial projects, I had no choice but to convert to Git and move my projects to Github.


# Quickstart

This process has been broken into 2 steps, on purpose:

1. Create empty Git repositories on Github for each Bitbucket Hg repository:

```
$ ./bitbucket_hg_to_github.py --create_gh_repos <other args...>
```

2. Convert Bitbucket Hg repositories to Git and push them to Github:

```
$ ./bitbucket_hg_to_github.py --push_gh_repos <other args...>
```

# Steps

These are the steps I followed:

* Make sure that `hg` and `git` can work with Bitbucket and Github respectively without asking for your credentials at the shell.
To do this, you essentially [create a SSH public-private key pair](https://codeyarns.github.io/tech/2016-01-20-how-to-ssh-without-username-or-password.html) and add the public key to your account in Github and Bitbucket.

* Create an **app password** at Bitbucket as described [here](https://confluence.atlassian.com/bitbucket/app-passwords-828781300.html).
You need to provide the *Repositories - Read* permission for this app password.
Note down the app password that you created.

* Create an **access token** at Github as described [here](https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line).
You need to enable everything under the *repo* scope for this access token.
Note down the access token that you created.

* Peruse my post on [converting Hg repository to Git](https://codeyarns.github.io/tech/2019-09-20-how-to-convert-mercurial-repository-to-git.html).
Make sure you have all those packages installed and the conversion is working on a dummy Hg repo.

* Install the `requests` and `pygithub` packages, if you do not have them already:

```
$ python3 -m pip install --user requests pygithub
```

* Create empty Git repositories on Github for each Bitbucket Hg repository:

```
$ ./bitbucket_hg_to_github.py --create_gh_repos \
--bb_username <your-bitbucket-username> \
--bb_app_password <bitbucket-app-password> \
--gh_username <your-github-username> \
--gh_access_token <github-access-token>
```

* Convert Bitbucket Hg repositories to Git and push them to Github:

```
$ ./bitbucket_hg_to_github.py --push_gh_repos \
--bb_username <your-bitbucket-username> \
--bb_app_password <bitbucket-app-password> \
--gh_username <your-github-username> \
--gh_access_token <github-access-token>
```

# Notes

* The script only moves a single repository.
This enables you to test out the script before trying it on all your Bitbucket Hg repos.
When you are ready to pull the trigger, add the `--do_it` option to the two commands.

* The Github repositories are created as *private* by default.

* A `_PRIVATE` suffix is added to the Hg repo when it is created on Github.
Use the `--git_suffix` option to control this.

* The script creates and uses a `tmp` directory to place the Hg and Git repos it is working with.
You can change this location using the `--tmp_dir` option.

# Arguments

```
$ ./bitbucket_hg_to_github.py --help
usage: bitbucket_hg_to_github.py [-h] [--create_gh_repos] [--push_gh_repos]
                                 --bb_username BB_USERNAME --bb_app_password
                                 BB_APP_PASSWORD --gh_username GH_USERNAME
                                 --gh_access_token GH_ACCESS_TOKEN
                                 [--git_suffix GIT_SUFFIX] [--tmp_dir TMP_DIR]
                                 [--do_it]

Move Bitbucket Hg repositories to Github.

optional arguments:
  -h, --help            show this help message and exit
  --create_gh_repos     Create Github repos for Bitbucket Hg repos (default:
                        False)
  --push_gh_repos       Push Bitbucket Hg repos to Github repos (default:
                        False)
  --bb_username BB_USERNAME
                        Bitbucket username (default: None)
  --bb_app_password BB_APP_PASSWORD
                        Bitbucket app password (default: None)
  --gh_username GH_USERNAME
                        Github username (default: None)
  --gh_access_token GH_ACCESS_TOKEN
                        Github access token (default: None)
  --git_suffix GIT_SUFFIX
                        Suffix for Git repo names (default: _PRIVATE)
  --tmp_dir TMP_DIR     Dir to use for repo work (default: tmp)
  --do_it               Use when you really want to convert all repos
                        (default: False)
```