import os
import sys
import pwd
import re
import pwd
import grp
from subprocess import *


class GitError(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class Commit:

    """
    Represents an individual git commit
    """

    rt_header_fields = {
        'REF: ': re.compile(r'^#[\d]{2,4}$'),
        'Signed-off-by: ': re.compile(r'^((\S+)(\s){1}){2}(<\S+)@dev.rtsoft.ru+>$'),
    }

    def __init__(self):
        pass


class CommitSubHeader:

    def __init__(self):
        self.ref = None
        self.signed = None


class User(object):

    '''
    Contains information about the user running the current program

    Each instance contains the following attributes containing information
    about the user who is running the current program

        .name   Login name of the current user
        .groups Groups that the current user is a member of
    '''

    def __init__(self):
        pwent = pwd.getpwuid(os.getuid())
        self.name = pwent.pw_name
        self.real_name = pwent.pw_gecos.split(',', 2)[0]
        gids = os.getgroups()
        gid = os.getgid()
        if gid not in gids:
            gids.append(gid)
        self.groups = []
        for gid in gids:
            try:
                self.groups.append(grp.getgrgid(gid).gr_name)
            except:
                sys.stdout.write(
                    "Can't find name for gid %d.  (This can usually be safely ignored.)\n" % gid)


class Tag:

    """
    Represents a pushed git tag reference
    """

    zero_id = '0' * 40

    def __init__(self, name, id=None, new_id=None):
        if not id and not new_id:
            cmd = ['git', 'rev-parse', name]
            try:
                id = call(cmd)
            except:
                id = None
        elif id == self.zero_id:
            id = None

        self.id = id
        self.name = name


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

def make_pipeline(previous_output_pipe,*cmd_list):
    """
    Make pipeline and call terminal commands
    """

    proc_list = []
    for cmd in cmd_list:
        proc = Popen(
            cmd, stdin=previous_output_pipe, stdout=PIPE, close_fds=True)
        proc_list.append(proc)
        previous_output_pipe = proc.stdout
    lines = proc.stdout.readlines()
    exitcode_list = []
    for proc in proc_list:
        exitcode = proc.wait()
        exitcode_list.append(exitcode)
    for (cmd, exitcode) in zip(cmd_list, exitcode_list):
        if 'grep' in cmd:
            continue
        if exitcode != 0:
            raise GitError('"%s": returns exitcode %s' % (
                ' '.join(cmd), exitcode))
    lines = map(lambda l: l.rstrip(), lines)

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


def list_created_revs(rev):
    """
    This shows all log entries that are not already covered
    by another ref - i.e. commits that are now accessible
    from this ref that were previously not accessible
    """

    cmd1 = ["git", "rev-parse", "--not", "--branches"]
    cmd2 = ["grep", "-v", rev.new]
    cmd3 = ["git", "rev-list", "--reverse",
            "--pretty=oneline", "--stdin", rev.new]
    filter = lambda line: re.match('^([0-9a-f]+) (.*)$', line).groups()

    return map(filter, make_pipeline(None, cmd1, cmd2, cmd3))


def list_added_revs(rev):
    cmd1 = ["git", "rev-list", "--reverse",
        "--pretty=oneline", rev.old + ".." + rev.new]
    filter = lambda line: re.match('^([0-9a-f]+) (.*)$', line).groups()

    return map(filter, make_pipeline(None, cmd1))


def dump_header_body(rev):
    """
    git-log -n 1 --pretty=format:%b "$rev" |
    """

    cmd1 = ["git", "log", "-n", "1", "--pretty=format:%b", rev]

    return make_pipeline(None, cmd1)


def match_or_die_if_multiply_defined(line, prefix, var):
    if line.find(prefix) == 0:
        if var != None:
            ERROR("*** multiple '", prefix, ": *' lines")
            ERROR("*** previous value was", var)
            ERROR("*** current line is ", line)
            sys.exit(2)
        return True
    else:
        return False
