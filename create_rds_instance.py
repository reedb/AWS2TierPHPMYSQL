#!/usr/bin/python

"""Create an AWS RDS DB instance, reed-db-server, 5GB of storage, db.t1.micro

Usage:
  create_rds_instance.py [--ip_add=<ipadd>]  [--sg_name=<name>] [--pg_name=<name>] [--db_pw=<pw>] 
  create_rds_instance.py -h | --help
  create_rds_instance.py --version

Options:
  -h --help         Show this screen.
  --version         Show version.
  --ip_add=<ipadd>  Whitelist IP Adress [default: 174.7.129.36].
  --sg_name=<name>  Security group name [default: reed_sg].
  --pg_name=<name>  Parameter group name [default: reed-param-grp].
  --db_pw=<pw>      MySQL database password [default: Astr0man].
  
"""

import boto.rds
import datetime  
import os
import sys
from   docopt import docopt  
from   pprint import pprint

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
def find_sg(conn, sg_search_name):
    printf("Searching for security group %s...", sg_search_name)
    rs = conn.get_all_security_groups()
    for sg in rs:
        printf(".")
        if sg_search_name in sg.name:
            printf("found.\n")
            return sg
    printf("not found.\n")
    return None 

# Find db parameter group
#
def find_pg(conn, pg_search_name):
    printf("Searching for parameter group %s...", pg_search_name)
    rs = conn. get_all_dbparameter_groups()
    for pg in rs:
        printf(".")
        if pg_search_name in pg.name:
            printf("found.\n")
            return pg
    printf("not found.\n")
    return None 

# Get command line params see: http://docopt.org
#
arguments = docopt(__doc__, version='create_rds_instance 1.0')
ip_add  = arguments['--ip_add']
sg_name = arguments['--sg_name']
db_pass = arguments['--db_pw']
pg_name = arguments['--pg_name']

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
printf("Create an AWS RDS DB instance.\n")

# Create boto context
#
connEC2 = boto.ec2.connect_to_region("us-west-2")
connRDS = boto.rds.connect_to_region("us-west-2")

# Verify security group exists
#   
sg = find_sg(connEC2, sg_name)
if (sg == None):
    printf("Unable to create instance.\n") 
    sys.exit(1)
                                      
# Create parameter group if it doesn't exist. This is an AWS abstraction of the mysql.conf file.
# Can't find a specific param, see: http://stackoverflow.com/questions/8873519/modify-db-parameter-group-in-aws-rds-using-boto
#   
pg = find_pg(connRDS, pg_name)
if (pg == None):
    printf("Creating parameter group %s...", pg_name) 
    pg = connRDS.create_parameter_group(pg_name, description='reeds parameter group')
    printf("OK\n")  
    pg1 = connRDS.get_all_dbparameters(pg_name)
    pg2 = connRDS.get_all_dbparameters(pg_name, marker = pg1.Marker)
    pg1.get_params()
    pprint(pg1.keys())                
    printf("*****")
    pg2.get_params()
    pprint(pg2.keys())                
else:        
    pg1 = connRDS.get_all_dbparameters(pg_name)
    pg2 = connRDS.get_all_dbparameters(pg_name, marker = pg1.Marker)
    pg1.get_params()
    pprint(pg1.keys())
    printf("*****")
    pg2.get_params()
    pprint(pg2.keys())                

inst = connRDS.create_dbinstance(id="reed-db-server", 
                                 allocated_storage=5,
                                 instance_class='db.t1.micro', 
                                 master_username='root',
                                 master_password=db_pass, 
                                 param_group=pg_name,
                                 security_groups=[sg_name])









#print db.status 
pprint(db.__dict__)
               
'''

# Wait on status creating backing-up available
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


instances = conn.get_all_dbinstances("db-master-1")
db = instances[0]
>>> db.status
u'available'
>>> db.endpoint
(u'db-master-1.aaaaaaaaaa.us-west-2.rds.amazonaws.com', 3306)
     
>>> db.endpoint
(u'db-master-1.aaaaaaaaaa.us-west-2.rds.amazonaws.com', 3306)

% mysql -h db-master-1.aaaaaaaaaa.us-west-2.rds.amazonaws.com -u root -phunter2
mysql>


try:
    # find mysql socket: mysql -uroot -proot -e "show variables"
    con = _mysql.connect('localhost', 'root', '@str0m@n', 'testdb', unix_socket='/var/mysql/mysql.sock')
        
    con.query("SELECT VERSION()")
    result = con.use_result()
    
    print "MySQL version: %s" % \
        result.fetch_row()[0]
    
except _mysql.Error, e:
  
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

finally:
    
    if con:
        con.close()




'''
