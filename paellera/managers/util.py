import tempfile
import subprocess
from datetime import datetime

from .path import path


def convert_range_to_datetime(start, end):
    "start and end are timestamps"
    start = datetime.fromtimestamp(float(start))
    end = datetime.fromtimestamp(float(end))
    return start, end
    


class Gpg(object):
    def __init__(self):
        self.directory = path(tempfile.mkdtemp('gpg'))
        self.keyring = self.directory / 'keyring'
        self.cmdbase = ['gpg', '--no-default-keyring', '--keyring', self.keyring]

    def __del__(self):
        self.directory.rmtree()
        
    def importkey(self, keydata):
        cmd = self.cmdbase + ['--import']
        prefix = 'gpg: key '
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        proc.stdin.write(keydata)
        proc.stdin.close()
        retval = proc.wait()
        lines = []
        errorlines = []
        for line in proc.stderr:
            errorlines.append(line)
            if line.startswith(prefix):
                lines.append(line)
        error = ''.join(errorlines)
        if len(lines) != 1:
            print "gpg returned an unexpected error:"
            print error
            raise RuntimeError, "gpg returned an unexpected error"
        if retval:
            raise RuntimeError, "gpg returned %d\n%s" % (retval, error)
        line = lines[0]
        keyid = line.split(prefix)[1].split(':')[0]
        return keyid
    
