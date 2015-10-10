# Quick and dirty python 3 script to create changelog-like ouput for ebuilds

Due to the transition to git in Gentoo, the Changelog stopped being updated. They should be generated during the git -> rsync synchronization, but it was not available soon enough.
Out of frustration this small script was born. It uses the Github API to get the history on a package. The output tries to mimic the Changelog layout and coloring (as seen with vim).

It is not bug-free, the repository configuration is hardcoded in the script, and the output coloring may not suite you.
Also it may be useful to filter out part of the log (like the "Package-Manager: ..." statement).
Feel free to submit some PR.

# Requirements

- Python 3 (because it works out of the box with unicode in names)
- dev-python/requests
- dev-python/simplejson

# Install

The script uses the basename of the command invoked to find out which repository to check.
This means that you have to create symlinks to `changelog-base.py` to use the command
Right now, only two repositories are supported:
- gentoo with changelog-gentoo.py
- gentoo-science with changelog-sci.py

You may had more, see [Adding a new repository](#adding-a-new-repository)

# Usage

```
changelog-gentoo.py sys-apps/portage
```
Github limits the number of anonymous queries to a few dozens. You may want to create a [OAuth token](https://help.github.com/articles/creating-an-access-token-for-command-line-use/)
and put it into the `GITHUB_OAUTH_TOKEN` environment variable. The script will then use it and you should not run into any issue.


# Adding a new repository

Right now, to add a new repo, you need to edit the script changelog-base.py and add the new repository to the repo dictionary.
The key should be the basename of the symlink you are going to use for the new repo. The value is the location of the repository.

# License

MIT
