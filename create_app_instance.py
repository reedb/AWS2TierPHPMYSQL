#!/usr/bin/python

"""Create an AWS EC2 instance. Basic 64-bit Amazon Linux AMI, Micro, 'reed_app_server'.

Usage:
  create_app_instance.py [--sg_name=<name>] [--ssh_key=<key>]
  create_app_instance.py -h | --help
  create_app_instance.py --version

Options:
  -h --help            Show this screen.
  --version            Show version.
  --sg_name=<name>     Security group name [default: reed_sg].
  --ssh_key=<key>      SSH key file name [default: aws_autoprovision_keypair].

"""

import boto.ec2 
import datetime  
import os
import sys
import time
from docopt import docopt  

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
  
# Find security group
#
def find_sg(sg_search_name):
    printf("Searching for security group %s...", sg_search_name)
    rs = conn.get_all_security_groups()
    for sg in rs:
        printf(".")
        if sg_search_name in sg.name:
            printf("found.\n")
            return sg
    printf("not found.\n")
    return None 
       
# Wait on instance status pending.
#    
def wait_on_pending(instance):
    printf('Waiting for instance to start')
    status = instance.update()
    while status == 'pending':
        time.sleep(2)
        status = instance.update()
        printf(".")
    if status == 'running':
        printf("New instance is running.\n")
        return True
    else: printf("Instance did not start. Status: %s\n", status)
    return False

# Wait on check instance/system status initializing.
#    
def wait_on_system_ok(instance):
    printf('Waiting for check system status.')
    instances = conn.get_all_instance_status(instance_ids=instance.id)
    status = instances[0].system_status.status
    time.sleep(1) 
    printf(".")
    while status == 'initializing':
        time.sleep(5)
        instances = conn.get_all_instance_status(instance_ids=instance.id)
        status = instances[0].system_status.status
        printf(".")
    if status == 'ok':
        printf("OK\n")
        return True
    else: printf("Failed. Status: %s\n", status)
    return False       

def wait_on_instance_ok(instance):
    printf('Waiting for check system status.')
    instances = conn.get_all_instance_status(instance_ids=instance.id)
    status = instances[0].instance_status.status 
    time.sleep(1) 
    printf(".")
    while status == 'initializing':
        time.sleep(5)
        instances = conn.get_all_instance_status(instance_ids=instance.id)
        status = instances[0].instance_status.status 
        printf(".")
    if status == 'ok':
        printf("OK\n")
        return True
    else: printf("Failed. Status: %s\n", status)
    return False       
        
# Get command line params see: http://docopt.org
#
arguments    = docopt(__doc__, version='create_app_instance 1.0')
sg_name      = arguments['--sg_name']
ssh_key_name = arguments['--ssh_key']

# Make sure Boto configuration file exists in the users home directory. We need the AWS security credentials in it.
#  
boto_config_path = os.path.join(os.path.expanduser("~"), ".boto")
if (os.path.exists(boto_config_path) == False):
    printf("\nConfiguration file not found: %s\n", boto_config_path) 
    printf("  Configuration file must contain valid AWS security credentials.\n")
    printf("  See: http://boto.readthedocs.org/en/latest/getting_started.html\n")
    sys.exit(1)

# Make sure SSH key file exists.
# 
ssh_key_path = os.path.join(os.path.expanduser("~"), ".ssh", ssh_key_name + ".pem")
if (os.path.exists(ssh_key_path) == False):
    printf("\nSSH key file not found: %s\n", ssh_key_path) 
    printf("  Key file must contain RSA private key portion of AWS registered key pair.\n")
    sys.exit(1)

# boto.set_stream_logger('boto')      # Enable debug logging

# Create boto context
#
conn = boto.ec2.connect_to_region("us-west-2")

# Get existing security groups. If target group found, create the instance.        
#                          
sg = find_sg(sg_name)
if (sg is None):
    printf("Unable to create instance.\n") 
    sys.exit(1)
else: 
    # Create and wait for an instance to be running
    #
    printf("Creating instance...")
    reservation = conn.run_instances('ami-ccf297fc', 
                                     key_name=ssh_key_name, 
                                     instance_type='t1.micro', 
                                     security_groups=[sg_name])

    # Find our instance. We don't know how to handle more than one returned instance
    #                             
    num_inst = len(reservation.instances)
    if (num_inst != 1):
        printf("Number of returned instances not one: %d\n", num_inst)
        
    else:
        instance = reservation.instances[0]
        printf("Done. Created %s\n", instance)

    	# Wait for instance to start.
    	#  
    	if (wait_on_pending(instance)) :

            printf("Adding tag...")
            instance.add_tag('Name', "reed_app_server") 
            printf("OK\n")    

            # Wait on check instance/system status not OK.
            #    
            if (wait_on_system_ok(instance)) :
                if (wait_on_instance_ok(instance)) :
                    printf("To connect to new instance use:\n")
                    printf("ssh -v -i %s ec2-user@%s\n", ssh_key_path, instance.public_dns_name)
                    sys.exit(0)

printf("Instance did not start.\n")
sys.exit(1)
