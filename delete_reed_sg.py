#!/usr/bin/python

"""Delete an AWS Security group.

Usage:
  delete_reed_sg.py [--sg_name=<name>]
  delete_reed_sg.py -h | --help
  delete_reed_sg.py --version

Options:
  -h --help         Show this screen.
  --version         Show version.
  --sg_name=<name>  Security group name [default: reed_sg].

"""

import boto.ec2 
import datetime  
import os
import sys
from docopt import docopt  

__author__ = 'reedb'

# Cover for printf for old C programmers
# 
def printf(format, *args):
    return sys.stdout.write(format % args)
    
# Print security group attributes
#
def printSG(sg):                             
    printf("Name:  %s\n", sg.name);
    printf("ID:    %s\n", sg.id);
    printf("Rules:\n");
    for perm in sg.rules:
        port_str = "%s(%s-%s)" % (perm.ip_protocol, perm.from_port, perm.to_port)
        printf("  %-17s", port_str) # left align in a 17 space field
        for grant in perm.grants:
            printf(" %s", grant)
        printf("\n")
        

# Get command line params see: http://docopt.org
#
arguments = docopt(__doc__, version='delete_reed_sg 1.0')
sg_name = arguments['--sg_name']

# Make sure Boto configuration file exists in the users home directory. We need the AWS security credentials in it.
#  
boto_config_path = os.path.join(os.path.expanduser("~"), ".boto")
if (os.path.exists(boto_config_path) == False):
    printf("\nConfiguration file not found: %s\n", boto_config_path) 
    printf("  Configuration file must contain valid AWS security credentials.\n")
    printf("  See: http://boto.readthedocs.org/en/latest/getting_started.html\n")
    sys.exit(1)

# boto.set_stream_logger('boto')      # Enable debug logging

# delete boto context
#
conn = boto.ec2.connect_to_region("us-west-2")

# Get existing security groups        
#                          
printf("Searching for security group %s...", sg_name)
rs = conn.get_all_security_groups()
for sg in rs:
    if sg_name in sg.name:
        printf("found.\n")
        printSG(sg)
        conn.delete_security_group(sg.name, sg.id)
        printf("Security group %s deleted.\n", sg_name)
        sys.exit(0)
printf("not found.\n")
              
