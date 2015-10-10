#!/usr/bin/env python3

# The MIT License (MIT)
#
# Copyright (c) 2015 Olivier Huber <oli.huber@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import json
import requests
import re
import sys
import os
import getopt

import colorama

# Customize this to add new repositories
# the key must be the name of the program
# the value is the repo on github
repo = {'changelog-gentoo.py': 'gentoo/gentoo',
        'changelog-sci.py': 'gentoo-science/sci'}


def usage_cli():
    print("You need to specify a single argument: cat-name/package-name")


def usage_repo():
    print("The same script is used for different repositories")
    print("To add a new repository, you need to edit the \"repo\" dictionary in the script")
    print("The key is the basename of a symlink to the script and the value is the github repo name")
    print("Then you can create a new symlink to the script with the corresponding basename")


def usage():
    usage_cli()
    usage_repo()


if __name__ == '__main__':

    colorama.init()

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], 'h', ['help'])
    except getopt.GetoptError as err:
        sys.stderr.write('{0} : {1}\n'.format(sys.argv[0], str(err)))
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == '-h' or o == '--help':
            usage()
            sys.exit(0)

    if len(sys.argv) != 2:
        print("Error, no package given on the command line")
        usage_cli()
        sys.exit(1)
    package = sys.argv[1]

    # try to do some validation
    if len(package.split('/')) != 2:
        print("Error, package name does not have the right format!\nIt must be cat/package. Instead we got {:}".format(package))
        sys.exit(1)

    headers = {}
    if 'GITHUB_OAUTH_TOKEN' in os.environ:
        headers['Authorization'] = 'token ' + os.environ['GITHUB_OAUTH_TOKEN']

    repo_name = repo.get(os.path.basename(sys.argv[0]), None)

    if not repo_name:
        print("No repository is mapped to the name of the commad")
        usage_repo()
        sys.exit(1)

    r = requests.get("https://api.github.com/repos/{:}/commits?path={:}".format(repo_name, package), headers=headers)

    if (r.ok):
        packageData = json.loads(r.text or r.content)

        if len(packageData) == 0:
            print("Opps, something went wrong, no data back from github")
            sys.exit(1)

        for commitData in packageData:
            sha1 = commitData['sha']
            commit = commitData['commit']
            rsha1 = requests.get("https://api.github.com/repos/{:}/commits/{:}".format(repo_name, sha1), headers=headers)

            if (rsha1.ok):
                sha1Data = json.loads(rsha1.text or rsha1.content)

                fileData = [(i['filename'].replace(package + '/', ''), i['status']) for i in sha1Data['files'] if re.match(package, i['filename'])]
                changedFiles = []
                for f, s in fileData:
                    if s == 'added':
                        changedFiles.append(colorama.Back.BLUE + '+' + f + colorama.Back.RESET)
                    elif s == 'renamed':
                        changedFiles.append(colorama.Back.BLUE + '+' + f + colorama.Back.RESET)
                        # search for removed file
                        rmFile = [i['previous_filename'].replace(package + '/', '') for i in sha1Data['files'] if re.match(package + '/' + f, i['filename'])]
                        if len(rmFile) == 1:
                            changedFiles.append(colorama.Back.YELLOW + '-' + rmFile[0] + colorama.Back.RESET)
                        else:
                            print(colorama.Fore.RED + "Error, file {:} was created from unkwown file!".format(s) + colorama.Fore.RESET)
                            print(rmFile)
                    elif s == 'removed':
                        changedFiles.append(colorama.Back.YELLOW + '-' + f + colorama.Back.RESET)
                    elif s == 'modified':
                        changedFiles.append(colorama.Fore.RED + f + colorama.Fore.RESET)
                    else:
                        print(colorama.Fore.RED + "Error, status {:} unknown".format(s) + colorama.Fore.RESET)
                        print("sha = {:}".format(sha1))
                        print(sha1Data)

                addedEbuild = [i[0] for i in fileData if (i[1] == 'added' or i[1] == 'renamed') and re.search('\.ebuild$', i[0])]

                date = colorama.Fore.BLUE + commit['committer']['date'] + colorama.Fore.RESET
                for ebuild in addedEbuild:
                    print(colorama.Fore.RED + '*{:}{:} ({:})'.format(ebuild, colorama.Fore.RESET, date))
                if len(addedEbuild) > 0:
                    print('')

                print('  {:}; {:}{:}{:} {:}<{:}>{:}'.format(date, colorama.Fore.GREEN, commit['author']['name'], colorama.Fore.RESET,
                                                            colorama.Fore.CYAN, commit['author']['email'], colorama.Fore.RESET))
                print(', '.join(changedFiles))
                print(commit['message'])
                print('')

            else:
                print('Problem while querying commit {:}'.format(sha1))
                sys.exit(1)

    else:
        print("Problem with the request for package {:}".format(package))
        print(r.text)
        print(r.content)
