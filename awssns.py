################################################################################
#            Copyright 2018 Smartronix Inc. All Rights Reserved.               #
#                                                                              #
################################################################################
import util
import sys

#
# This is a test for the aws sns callable
#
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-m", action="store", type="string", dest="message")
parser.add_option("-t", action="store", type="string", dest="type")

(options, args) = parser.parse_args(sys.argv)

# take the message, type parameters from input
message = {"message": options.message, "type": options.type, "source" : "smx gcloud cis"}
# call the sub to send the message out
res = util.send_aws_sns(message=message)
