from datetime import tzinfo, timedelta, datetime
import json
import StringIO
import re
import sys
import os

from optparse import OptionParser
parser = OptionParser()

parser.add_option("-r", "--root", action="store", type="string", dest="bucket")
parser.add_option("-w", "--work", action="store", type="string", dest="wpath")
parser.add_option("-p", "--project", action="store", type="string", dest="project")

(options, args) = parser.parse_args(sys.argv)

lines = [line.rstrip('\n')[len(options.bucket)+6:] for line in open(os.path.join(options.wpath, 'config_all'))]

for ln in lines:
    if ln.endswith('.config'):
        fn = ln[0:len(ln)-7] + '/'
        if not fn in lines:
            os.system("touch {}/.schd_check && gsutil cp {}/.schd_check gs://{}/{}".format(options.wpath,options.wpath, options.bucket, fn))
        continue
    if ln.endswith('/'):
        cn = ln[0:len(ln)-1] + '.config'
        if not cn in lines:
            os.system("gsutil rm -r gs://{}/{}".format(options.bucket, ln))
        continue
