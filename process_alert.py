import json
import os
import sys
import jmespath
import util
import re

from subprocess import call

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-s", "--system", action="store", type="string", dest="sysbuck")
parser.add_option("-f", "--file", action="store", type="string", dest="file")
parser.add_option("-t", "--tag", action="store", type="string", dest="tag")
parser.add_option("-w", "--wpath", action="store", type="string", dest="wpath")
parser.add_option("-p", "--project", action="store", type="string", dest="project")

(options, args) = parser.parse_args(sys.argv)

scfg = "gs://{}/.config/.config/storage/".format(options.sysbuck)
buckre = """gs:\/\/.*/(.*)/storage/(.*)/"""

config = []
for line in open(os.path.join(options.wpath, 'allsysdir')):
    line = line.rstrip('\n')
    if line.endswith(':'): line=line[0:len(line)-1]
    if not line.endswith('/'): continue
    if scfg == line: continue
    match = re.match(buckre, line)
    if match:
        proj=match.group(1)
        buck=match.group(2)
        config.append({
            "project" : proj,
            "bucket" : buck,
            "sysdir" : line
            })

def readjson(f):
    with open(f) as json_data:
        ret=json.load(json_data)
        json_data.close()
        return ret

mess=readjson(options.file)

# os.remove(sys.argv[1])

CONFDIR="gs://{}/{}/storage/{}/"
def doDelete(proj, buck):
    confdir=CONFDIR.format(options.sysbuck, proj, buck)
    os.system("gsutil rm -r {}".format(confdir))
    util.send_aws_sns({
        "message" : "Removed tracking of bucket {} of project {}.".format(buck, proj),
        "type":"info",
        "source" : "smx gcloud cis"
        })

def doNew(proj, back):
    confdir=CONFDIR.format(options.sysbuck, proj, buck)
    os.system("touch {}/.lastupdate && gsutil cp {}/.lastupdate {}".format(options.wpath, options.wpath, confdir))
    os.system("gsutil ls -b -L gs://{} > {}/acl.txt".format(buck, options.wpath))
    os.system("gsutil iam get gs://{} > {}/iam.json".format(buck, options.wpath))
    os.system("gsutil cp {}/acl.txt {}".format(options.wpath, confdir))
    os.system("gsutil cp {}/iam.json {}".format(options.wpath, confdir))

    util.send_aws_sns({
        "message" : "Set up to tracking for bucket {} of project {}.".format(buck, proj),
        "type":"info", 
        "source" : "smx gcloud cis"}
        )


# loop through the messages we got
for message in mess:

  # get the attributes we are interested out of the message
  data=json.loads(message["message"]["data"])
  severity=data["severity"]

  # we only eal with notice, not security complaints
  if not severity == "NOTICE": continue
  
  method=data["protoPayload"]["methodName"]
  proj=data["resource"]["labels"]["project_id"]
  buck=data["resource"]["labels"]["bucket_name"]
  
  # find our configuration of this bucket
  find = jmespath.search("[?project == '{}' && bucket=='{}']".format(proj, buck), config)
  findb = len(find) > 0

  if method=="storage.buckets.update":
      labfile = "{}/{}.lab".format(options.wpath, buck)      
      os.system("gsutil label get gs://{} > {}".format(buck, labfile))
      labels = readjson(labfile)
      
      if options.tag in labels and not findb:
          # it's new we need to add configuration for this bucket
          doNew(proj, buck)
          continue
      elif findb and not options.tag in labels:
          # it's just tagged off, we need to remove the configuration
          doDelete(proj, buck)
          continue

  # we are not hanlding this bucket         
  if not findb: continue 
  
  if method=="storage.objects.update":
      # we need to check what update on the object
      # if it is public report alert
      # else if it is acl report notify
      print "check...."
      continue

  if method=="storage.buckets.update":
      # we need to check acl?
       print "checking..."
       continue

  if method=="storage.setIamPermissions":
      # we need to check iam
      print "checking..."
      continue

  if method == "storage.buckets.delete":
      # the whole bucket got removed, we need to remove the configuration
      doDelete(proj, buck)
      # we are done with the message
      continue

  #print json.dumps(data)


