import util

message = {"message": "this is an alert", "type":"alert", "source" : "smx gcloud cis"}

res = util.send_aws_sns(message=message)

print res
