#!/usr/bin/python

"""Create a personal AWS Security group whitelisted to your IP address.

Usage:
  create_reed_sg.py [--ip_add=<ipadd>]  [--sg_name=<name>]
  create_reed_sg.py -h | --help
  create_reed_sg.py --version

Options:
  -h --help         Show this screen.
  --version         Show version.
  --ip_add=<ipadd>  Whitelist IP Adress [default: 174.7.129.36].
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
arguments = docopt(__doc__, version='create_reed_sg 1.0')
ip_add  = arguments['--ip_add']
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

# Build  CIDR. Match all 32 bits. See: http://wiki.inspircd.org/tutorial/CIDR
#                                                                   
CIDR_IP_Add = ip_add  + "/32"
printf("Create security group using whitelist IP: %s\n", CIDR_IP_Add)

# Create boto context
#
conn = boto.ec2.connect_to_region("us-west-2")

# Get existing security groups        
#                          
rs = conn.get_all_security_groups()
for sg in rs:
    if sg_name in sg.name:
        printf("%s already exists. To delete run: delete_reed_sg.py\n", sg.name)
        printSG(sg)
        sys.exit(0)
              
# Build the desciption string                           
timestr = '{:%Y/%m/%d %H:%M:%S}'.format(datetime.datetime.now()) 
desc = 'HTTP, HTTPS, SSH and MYSQL, whitelisted to ' + CIDR_IP_Add + ', Created: ' + timestr
                                                                  
# Create the security group. See: http://boto.readthedocs.org/en/latest/security_groups.html
#
new_sg = conn.create_security_group(sg_name, desc)

new_sg.authorize(ip_protocol='tcp', from_port=80, to_port=80,     cidr_ip=CIDR_IP_Add)
new_sg.authorize(ip_protocol='tcp', from_port=22, to_port=22,     cidr_ip=CIDR_IP_Add)
new_sg.authorize(ip_protocol='tcp', from_port=443, to_port=443,   cidr_ip=CIDR_IP_Add)
new_sg.authorize(ip_protocol='tcp', from_port=3306, to_port=3306, cidr_ip=CIDR_IP_Add)

printf("Created new security group:\n") 
printSG(new_sg)
