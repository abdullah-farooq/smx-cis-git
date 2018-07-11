from datetime import tzinfo, timedelta, datetime
import json
import StringIO
import re
import sys
import os

from optparse import OptionParser
parser = OptionParser()

parser.add_option("-r", "--report", action="store", type="string", dest="report")
parser.add_option("-p", "--project", action="store", type="string", dest="project")
parser.add_option("-s", "--summary", action="store_true", dest="summary", default=False)

(options, args) = parser.parse_args(sys.argv)

report_path=os.path.join(options.report, options.project)

if not os.path.exists(report_path):
   print "Report path for project {} does not exist. Please check the inputs.\n\n".format(options.project)
   quit()

bucket_dirs=filter(lambda x: os.path.isdir(os.path.join(report_path, x)), os.listdir(report_path))

project={}
project["name"]=options.project
project["buckets"]=len(bucket_dirs)
project["violations"]=0
project["bucketlevel"]=0
project["size"]=0
project["objects"]=0


def build_summary(bucket):
    bs = {}
    bs["name"] = bucket
    bpath=os.path.join(report_path, bucket)
    buck_info = os.path.join(bpath, "bucket")
    with open(buck_info) as fp:
       for line in fp:
           match = re.search('^\s*Time created:\s+([^ ].*)\n$', line)
           if match:
              bs["created"] = match.group(1)
              continue
           match = re.search('^\s*Time updated:\s+([^ ].*)\n$', line)
           if match:
              bs["updated"] = match.group(1)
              break
    mypath=os.path.join(bpath, "violation")
    vlfiles=[]
    if (os.path.isdir(mypath)):
      vlfiles = [f for f in os.listdir(mypath) if os.path.isfile( os.path.join(mypath, f))]
    bs["violations"] = len(vlfiles)
    project["violations"] += len(vlfiles)
    bs["isbucket"] = os.path.isfile(os.path.join(bpath, "violation/vl.0"))
    if bs["isbucket"]:
       project["bucketlevel"]+=1
    stsfile=os.path.join(bpath, "bucket_sts")
    bs["objects"]=0
    bs["size"]=0
    if bs["violations"] > 0:
       bs["color"]="#ef3d47"
    else:
       bs["color"]="lightgreen"

    with open(stsfile) as fp:
       for line in fp:
           match = re.search('^(\d+).*(gs:.*)\n$', line)
           if match:
               bs["size"]+=int(match.group(1))
               bs["objects"]+=1
    project["size"] += bs["size"]
    project["objects"] += bs["objects"]
    return bs


buckets = []
for b in bucket_dirs:
   buckets.append(build_summary(b))


def do_offending():
  body =  StringIO.StringIO()
  b_html="""
<tr><td style="background-color:#ef3d47;"></td><td><table><tr><th nowrap>Offending Object</th><td>{}</td></tr> <tr><th nowrap>Offending Grant Counts</th><td>{}</td></tr><tr><th nowrap>Offending Grant(s)</th><td>{}</td></tr></table></td></tr>
  """

  html="""
  <br/><table><thead><tr><th colspan="20"> Bucket: {}, Violations: {}, Bucket level: {}</b></th></tr></thead>{}
     </table>"""

  for bucket in buckets:
    bpath=os.path.join(report_path, bucket["name"])
    mypath=os.path.join(bpath, "violation")
    vlfiles=[]
    ofr = []
    if (os.path.isdir(mypath)):
        vlfiles = [f for f in os.listdir(mypath) if os.path.isfile( os.path.join(mypath, f))]
    else:
        continue
    offender=None
    for f in vlfiles:
      offender=None
      with open(os.path.join(mypath, f)) as fp:
        for line in fp:
          if offender== None:
              offender=line
              continue
          ary = line.split('} {')
          ofr.append(b_html.format(offender,len(ary),line))
    if len(ofr) > 0:
      print >>body, html.format(bucket["name"], bucket["violations"],bucket["isbucket"]," ".join(ofr))
  print body.getvalue()

def do_summary():
 
 body = StringIO.StringIO()
 dt = datetime.now()
 dtstr = dt.isoformat(' ')
 for b in buckets:
     print >>body, "<tr><th style='background-color:{}'>&nbsp;</th><td><b>{}</b></td><td nowrap>{}</td><td nowrap>{:.2f}</td><td>{}</td><td>{} </td><td>{}</td><td>{}</td></tr>".format(b["color"],b["name"], b["objects"], b["size"]/1000.0, b["violations"],b["isbucket"], b["created"], b["updated"])


 html="""
   <table>
      <thead>
         <tr>
            <th colspan='2' rowspan='2'>Scan Summary For Project: {}</th>
            <th colspan='1'>Buckets Scanned: {}</th>
            <th colspan='1'>Total Objects: {}</th>
            <th colspan='1'>Total Size: {:.2f} MB</th>
         </tr><tr>
            <th colspan='1'>Total Violations: {}</th>
            <th colspan='1'>Bucket Level Violations: {}</th>
            <th colspan='1'>Report Date: {}</th>
         </tr>
      </thead>
      <tr>
          <td colspan="20"><table><thead><tr><th colspan="2">Bucket</th><th>Objects</th><th>Size (KB)</th><th>Violations</th><th>Bucket Level</th><th>Created</th><th>LastUpdate</th></tr></thead>
      {}
   </table></td></tr></table>
""".format(project["name"], project["buckets"],project["objects"],
        project["size"]/1000000.0, project["violations"], 
        project["bucketlevel"], dtstr, body.getvalue())

 print html

if options.summary:
   do_summary()
else:
   do_offending()
