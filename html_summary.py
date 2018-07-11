from datetime import tzinfo, timedelta, datetime
import json
import StringIO

body = StringIO.StringIO()
dt = datetime.now()
dtstr = dt.isoformat(' ')
buckets = json.loads("""
   [{
       "name" : "bucket #1",
       "objects" : 100,
       "violations":0
     },
     {
        "name" : "bucket #2",
        "objects" : 100,
        "violations": 5                      
    }]
  """)
project = "test project"

for b in buckets:
    print >>body, "<tr><td colspan='2'>Backet: {}</td><td>{} objects</td><td>{} violations</td>".format(b["name"], b["objects"],b["violations"])


html="""
   <table>
      <thead>
         <tr>
            <th colspan='2'>Scan Summary For Project: {}</th>
            <th colspan='1'>Buckets Scanned: {}</th>
            <th colspan='1'>Report Date: {}</th>
         </tr>
      </thead>
      {}
   </table>
""".format(project, len(buckets), dtstr, body.getvalue())
print html
