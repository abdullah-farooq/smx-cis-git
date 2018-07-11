import sys
import re
from StringIO import StringIO

results = StringIO()
print >>results, '['
obj_start = False
acl_start = False
for line in sys.stdin:
    line = line.strip('\n')
    match = re.search('^(gs:\/\/.*):$', line) 
    if match:
        obj_start = True
        print >>results, '{'
        print >>results, '"gso":"{}",'.format(match.group(1).replace('"','\"'))
        continue
    if obj_start:
      match =  re.search('^\s*ACL:\s*\[\s*$', line)
      if match:
        acl_start = True
        print >>results, '"acl":['
        continue
      if acl_start:
        match = re.search('^\s*]\s*$', line)
        if match:
          print >>results, ']},'
          obj_start = False
          acl_start = False
          continue
        print >>results, line
        continue
print >>results, '{"gso":"","acl":[]}]'
print results.getvalue()
