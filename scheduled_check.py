from datetime import tzinfo, timedelta, datetime
import json
import StringIO
import re
import sys
import os
import jmespath
import util

from optparse import OptionParser
parser = OptionParser()

parser.add_option("-c", "--config", action="store", type="string", dest="confbuck")
parser.add_option("-s", "--system", action="store", type="string", dest="sysbuck")
parser.add_option("-w", "--work", action="store", type="string", dest="wpath")
parser.add_option("-p", "--project", action="store", type="string", dest="project")
parser.add_option("-t", "--topic", action="store", type="string", dest="topic")


(options, args) = parser.parse_args(sys.argv)

lines = [line.rstrip('\n') for line in open(os.path.join(options.wpath, 'allconfig'))]

configs = []
newconf = False
newmeta = False

projre = """gs:\/\/.*\/config\/(.*)\/storage\.config:"""
metare = """\s{4,4}Metadata:"""
buckre = """^\s{8,8}(.*):(.*)$"""
for line in lines:
    match = re.match(projre, line)
    if match:
        newconf = True
        project= match.group(1)
        continue
    if newconf:
        match = re.match(metare, line)
        if match:
            newmeta = True
            continue
        if newmeta:
            match = re.match(buckre, line)
            if match:
               configs.append( 
                    { "project": project,
                      "bucket" : match.group(1).strip(),
                      "audit"  : match.group(2).strip()
                    })
               continue
            newmeta = False
            newconf = False

scfg = "gs://{}/.config/.config/storage/".format(options.sysbuck)
dirlines = []
for line in open(os.path.join(options.wpath, 'allsysdir')):
    line = line.rstrip('\n')
    if line.endswith(':'): line=line[0:len(line)-1]
    if not line.endswith('/'): continue
    if scfg == line: continue
    dirlines.append(line)

CONFDIR="gs://{}/{}/storage/{}/"

for conf in configs:
    confdir = CONFDIR.format(options.sysbuck, conf["project"], conf["bucket"])
    if not confdir in dirlines:
        conf["new"] = True
    else:
        conf["new"] = False

buckre = """gs:\/\/.*/(.*)/storage/(.*)/"""
deletes=[]
for line in dirlines:
    match = re.match(buckre, line)
    if match:
        proj=match.group(1)
        buck=match.group(2)
        find = jmespath.search("[?project == '{}' && bucket=='{}']".format(proj, buck)
                , configs)
        if len(find) == 0:
            deletes.append(line)

def doNew(conf):
    confdir=CONFDIR.format(options.sysbuck, conf["project"], conf["bucket"])
    os.system("gsutil notification create -f json -t {} gs://{}".format(options.topic, conf["bucket"]))
    os.system("touch {}/.lastupdate && gsutil cp {}/.lastupdate {}".format(options.wpath, options.wpath, confdir))
    util.send_aws_sns({
        "message" : "Set up to tracking for bucket {} of project {}.".format(conf["bucket"],  conf["project"]),
        "type":"info", 
        "source" : "smx gcloud cis"}
        })

def doCheck(conf):
    confdir=CONFDIR.format(options.sysbuck, conf["project"], conf["bucket"])
    print "checking {}".format(confdir)

def doDelete(confdir):
    match = re.match(""".*gs:\/\/.*\/.*\/(.*)\/storage\/(.*)/.*""", confdir)
    if not match: return
    project=match.group(1)
    bucket=match.group(2)
    notifile = os.path.join(options.wpath,'notifile')
    os.system("gsutil notification list gs://{} > {}".format(bucket, notifile))
    if os.path.isfile(notifile):
      notes=[]
      cnote=None
      with open(notifile) as fp:
        nstart=True
        for line in fp:
           line = line.rstrip('\n')
           if nstart:
              nstart=False
              cnote=line
              continue
           nstart=True
           if line.endswith(options.topic):
              notes.append(cnote)
       
      for ln in notes:
          os.system("gsutil notification delete {}".format(ln))
    os.system("gsutil rm -r {}".format(confdir))
    util.send_aws_sns({
        "message" : "Removed tracking of bucket {} of project {}.".format(bucket, project),
        "type":"info",
        "source" : "smx gcloud cis"}
        })


#deal with new
for conf in configs:
    if conf["new"]:
        doNew(conf)
    else:
        doCheck(conf)

#deal with deletes
for confdir in deletes:
    doDelete(confdir)




