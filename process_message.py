import json
import os
import sys
from subprocess import call

with open(sys.argv[1]) as json_data:
  mess = json.load(json_data)

os.remove(sys.argv[1])

for m in mess:
   if not m.has_key("message"):
     continue
   if not m["message"].has_key("attributes"):
     continue
   if not m["message"]["attributes"].has_key("Command"):
     continue
   print "hhhhh"
   c = m["message"]["attributes"]["Command"]
   if c == "RunScan":
     if not m["message"]["attributes"].has_key("ScanType"):
       continue
     t = m["message"]["attributes"]["ScanType"]
     if t == "GCloudStorage":
       if not m["message"]["attributes"].has_key("Project"):
          continue
       else:
          p =  m["message"]["attributes"]["Project"]
       if not m["message"]["attributes"].has_key("Bucket"):
          b='*'
       else:
          b = m["message"]["attributes"]["Bucket"]
       os.system("/home/ubuntu/smx-cis-git/gsScan -p {} -b '{}'".format(p, b)) 
