from datetime import tzinfo, timedelta, datetime
import json
import StringIO
import re
import sys
import os
import jmespath

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

project={}
project["name"]=options.project
project["iam"]=0
project["sas"]=0
project["violations"]=0
project["warnings"]=0
project["kms"]=0
project["vpcs"]=0
project["subnets"]=0
project["fwr"]=0
project["roles"]=0
project["peers"]=0

c2d1={}
c2d1["violation"]=False
c1d12={}
c1d12["violation"]=False
c2d8={}
c2d8["violation"]=False
c2d8["offendings"]=[]
c4d3={}
c4d3["violation"]=False
c4d3["offendings"]=[]
c4d1={}
c4d2={}
c4d1["violation"]=False
c4d1["offendings"]=[]
c4d2["violation"]=False
c4d2["offendings"]=[]


f = open(os.path.join(report_path, 'project-iam'))
iam = json.loads(f.read())
f.close()

iam["totalAuditConfig"]=0
iam["hasAllServices"]=False
if "auditConfigs" in iam:
    iam["totalAuditConfig"]=len(iam["auditConfigs"])
    allservice = jmespath.search("auditConfigs[?service == 'allServices']", iam)
    if len(allservice) > 0 and len(allservice[0])==3:
      iam["hasAllServices"]=True 

if iam["totalAuditConfig"]==0:
  c2d1["violation"]=True
  project["violations"] += 1
elif not iam["hasAllServices"]:
  c2d1["violation"]=True
  c2d1["message"]="No audit settings found for this project. Please set it explicitely"

if "bindings" in iam:
  project["roles"] = len(iam["bindings"])
  members=jmespath.search("bindings[].members[]", iam)
  members=list(set(members))
  project["iam"] = len(members)
  sas=jmespath.search("[?starts_with(@, `serviceAccount:`)]", members)
  project["sas"] = len(sas)
  owner= jmespath.search("bindings[?role==`roles/owner` && members[?starts_with(@,`serviceAccount:`)]]", iam)
  
  if len(owner)>0:
      c1d12["violation"]=True
      c1d12["offendings"]=[]
      for onrs in owner:
        for onr in onrs["members"]:
          if onr.startswith('serviceAccount:'):
             project["violations"] += 1
             c1d12["offendings"].append(onr)

kmsfile=os.path.join(report_path,'project-kms')
if os.path.isfile(kmsfile):
  with open(kmsfile) as fp:
    kstart=True
    for line in fp:
      line = re.sub('[\n"]','',line)
      if kstart:
        project["kms"] += 1
        kms=line
        kstart=False
      else:
          if line=="null":
              c2d8["violation"]=True
              project["violations"] += 1
              c2d8["offendings"].append(kms)
          else:
              line = re.sub('s', '', line)
              period = int(line) / 24/ 60 /60
              if period > 90:
                    c2d8["violation"]=True
                    project["violations"] += 1
                    c2d8["offendings"].append(kms)
          kstart=True

nwpath=os.path.join(report_path,'project-network')
f=open(nwpath)
network = json.loads(f.read())
f.close()
subspath=os.path.join(report_path,'project-subnets')
f=open(subspath)
subnets = json.loads(f.read())
f.close()

dt = datetime.now()
dtstr = dt.isoformat(' ')

project["vpcs"] = len(network)
project["subnets"] = len(subnets)

noflowflag= jmespath.search("[?!enableFlowLogs]", subnets)

c4d3["violation"] = len(noflowflag) > 0
project["violations"] += len(noflowflag)
for sbn in noflowflag:
   c4d3["offendings"].append({"name":sbn["name"], "vpc":sbn["network"], "region": sbn["region"]})

fwrpath=os.path.join(report_path,'project-firewall-rules')
f=open(fwrpath)
firewallrs = json.loads(f.read())
f.close()

def arr_in_range (arr, num):
   return any([in_range(s, num) for s in arr])

def in_range(rg, num):
   if rg.isdigit():
      return int(rg) == num
   sar = rg.split('-')
   if len(sar)!=2:
      return False
   if not sar[0].isdigit() or int(sar[0]) > num:
      return False
   if not sar[1].isdigit() or int(sar[1]) < num:
      return False
   return True

project["fwr"] = len(firewallrs)
for rule in firewallrs:
    if any([s.startswith('0.0.0.0') for s in rule["sourceRanges"]]):
        for ald in rule["allowed"]:
            if ald["IPProtocol"] == 'tcp' and arr_in_range(ald["ports"],22):
                c4d1["violation"]=True
                c4d1["offendings"].append(rule)
                project["violations"] += 1
            if ald["IPProtocol"] == 'tcp' and arr_in_range(ald["ports"],3389):
                c4d2["violation"]=True
                c4d2["offendings"].append(rule)
                project["violations"] += 1
            if ald["IPProtocol"] == 'ssh':
                c4d1["violation"]=True
                c4d1["offendings"].append(rule)
                project["violations"] += 1
            if ald["IPProtocol"] == 'rdp':
                c4d2["violation"]=True
                c4d2["offendings"].append(rule)
                project["violations"] += 1

peers=jmespath.search("[?peerings]", network)
c4d5={}
c4d5["warning"]=len(peers) > 0
c4d5["offendings"]=[]

for pr in peers:
    project["warnings"] += len(pr["peerings"])
    project["peers"] += len(pr["peerings"])
    for p in pr["peerings"]:
      c4d5["offendings"].append({"vpc": pr["name"], "state": p["state"], "network":p["network"]})

def do_offending():
  print """<tr><td colspan="20"><table><thead><tr><th colspan="2">SMX Benchmark</th><th>Level</th><th>VPC</th><th>Findings</th></tr></thead>"""
  if c1d12["violation"]:
      for v in c1d12["offendings"]:
          print """<tr><th style='background-color:#ef3d47'>&nbsp;</th><td><b>{}</b></td><td nowrap>{}</td><td nowrap>{}</td><td>{}</td></tr>""".format("SMX-1.12", "Alert", "ALL", "Service account {} has an owner role".format(v))


  if c2d1["violation"]:
      print """<tr><th style='background-color:#ef3d47'>&nbsp;</th><td><b>{}</b></td><td nowrap>{}</td><td nowrap>{}</td><td>{}</td></tr>""".format("SMX-2.1",
        "Alert","ALL", "No log audit settings found for this project. Please set it explicitely globally using 'allServices'")
  
  if c2d8["violation"]:
     for k in c2d8["offendings"]:
       vio = "Cryptographic key {} does not have a rotation schedule or schedule period is longer that 90 days.".format(k)
       print """<tr><th style='background-color:#ef3d47'>&nbsp;</th><td><b>{}</b></td><td nowrap>{}</td><td>{}</td><td>{}</td></tr>""".format("SMX-2.8", "Alert", "ALL", vio)

  if c4d1["violation"]:
     for k in c4d1["offendings"]:
         print """<tr><th style='background-color:#ef3d47'>&nbsp;</th><td><b>{}</b></td><td nowrap>{}</td><td>{}</td><td>Wide open SSH:<br/>{}</td></tr>""".format("SMX-4.1", "Alert", os.path.basename(k["network"]), json.dumps(k))

  if c4d2["violation"]:
      for k in c4d2["offendings"]:
          print """<tr><th style='background-color:#ef3d47'>&nbsp;</th><td><b>{}</b></td><td nowrap>{}</td><td>{}</td><td>Wide open RDP:<br/>{}</td></tr>""".format("SMX-4.2", "Alert", os.path.basename(k["network"]), json.dumps(k))

  if c4d3["violation"]:
      for k in c4d3["offendings"]:
          print """<tr><th style='background-color:#ef3d47'>&nbsp;</th><td><b>{}</b></td><td nowrap>{}</td><td>{}</td><td>Subnet flow log need to be turn on for subnet '{}' in region '{}'.</td></tr>""".format("SMX-4.3", "Alert", os.path.basename(k["vpc"]), k["name"], os.path.basename(k["region"]))


  if c4d5["warning"]:
      for k in c4d5["offendings"]:
          print """<tr><th style='background-color:orange'>&nbsp;</th><td><b>{}</b></td><td nowrap>{}</td><td>{}</td><td>Network Contains {} peered VPCs. Peer network security need to be checked to ensure security.<br/></td></tr>""".format("SMX-4.5", "Warning", k["vpc"], json.dumps(k))


def do_summary():
 html="""
      <thead>
         <tr>
            <th colspan='2' rowspan='3'>Scan Summary For Project: {}</th>
            <th colspan='1'>IAM Principals: {}</th>
			<th colspan='1'>Service Accounts: {}</th>
            <th colspan='1'>Cypher Keys: {}, Peer VPC: {}</th>
         </tr>
         <tr>
            <th colspan='1'>VPCs: {}</th>
            <th colspan='1'>Subnets: {}</th>
            <th colspan='1'>Firewall Rules: {}</th>
         </tr>		 
    	 <tr>
            <th colspan='1'>Violations: {}</th>
            <th colspan='1'>Warnings: {}</th>
            <th colspan='1'>Report Date: {}</th>
         </tr>
      </thead>
""".format(project["name"], project["iam"],project["sas"],
        project["kms"], project["peers"], project["vpcs"], 
        project["subnets"], project["fwr"], project["violations"], project["warnings"], dtstr)
 print html

print "<table>"
do_summary()
do_offending()
print "</table></div></body></html>"
