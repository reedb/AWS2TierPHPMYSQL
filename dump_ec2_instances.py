#!/usr/bin/python

"""Dump AWS EC2 instance_id data.

Usage:
  dump_instance_ids.py [--i=<inst_id>]
  dump_instance_ids.py -h | --help
  dump_instance_ids.py --version

Options:
  -h --help         Show this screen.
  --version         Show version.
  --i=<inst_id>     Instance ID [default: all].

"""

import boto.ec2 
import datetime  
import os
import sys
import time
from docopt import docopt  
from pprint import pprint

__author__ = 'reedb'

# printf cover for old C programmers.
# For formast specification see: http://docs.python.org/2/library/stdtypes.html#string-formatting-operations
# 
def printf(format, *args):
    sbuf = format % args
    count = len(sbuf)
    sys.stdout.write(sbuf)
    sys.stdout.flush()
    return count
             
def print_check_state(inst_status):
    printf("  ID:                    %s\n", inst_status.id)
    printf("  State:                 %s\n", inst_status.state_name)
    printf("  Check Instance Status: %s\n", inst_status.instance_status.status)
    printf("  Check System Status:   %s\n", inst_status.system_status.status)
  
# Get command line params see: http://docopt.org
#
arguments = docopt(__doc__, version='dump_instance_ids 1.0')
instance_id = arguments['--i']

conn = boto.ec2.connect_to_region("us-west-2")
              
# Get instance_id data
#
if ("all" in instance_id):
    reservations = conn.get_all_instances()
else:    
    reservations = conn.get_all_instances(instance_ids=instance_id)
    
instances = [i for r in reservations for i in r.instances]
for i in instances:
    pprint(i.__dict__)
                         
# Get Check Status data
#
printf("Check Status:\n")
if ("all" in instance_id):
    existing_instances = conn.get_all_instance_status()
else:
    existing_instances = conn.get_all_instance_status(instance_ids=instance_id)
        
for i in existing_instances:  
    print_check_state(i)

sys.exit(0)                                                                               
                                                                                           