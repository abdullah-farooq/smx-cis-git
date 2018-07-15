import util
import sys

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-m", action="store", type="string", dest="message")
parser.add_option("-t", action="store", type="string", dest="type")

(options, args) = parser.parse_args(sys.argv)
message = {"message": options.message, "type": options.type, "source" : "smx gcloud cis"}

res = util.send_aws_sns(message=message)
