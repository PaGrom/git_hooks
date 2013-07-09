import os
import sys
import pwd
from subprocess import *


class GitError(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def running_as_hook():
    """
    Check for running as hook
    """

    return 'GIT_DIR' in os.environ


def call(cmd, lcnt=1):
    """
    Call terminal command and return output lines
    """

    proc = Popen(cmd, stdout=PIPE, close_fds=True)
    lines = proc.stdout.readlines()
    exitcode = proc.wait()

    if exitcode != 0:
        raise GitError('"%s": returns exitcode %s. ' % (
            ' '.join(cmd), exitcode))

    lines = map(lambda l: l.rstrip(), lines)
    if lcnt != None and len(lines) != lcnt:
        raise GitError("\"%s\": couldn't retrieve exactly %s value(s)" % (
            ' '.join(cmd), lcnt))

    return lines


def get_config(key):
    """
    Get git config
    """

    cmd = ['git', 'config', key]

    return call(cmd)[0]


def get_rev_type(rev):
    """
    Get rev type: git cat-file -t rev_name
    """

    cmd = ['git', 'cat-file', '-t', rev]

    return call(cmd)[0]

def get_user_name():
    """
    Get user name
    """
    
    return pwd.getpwuid(os.getuid())[0]
