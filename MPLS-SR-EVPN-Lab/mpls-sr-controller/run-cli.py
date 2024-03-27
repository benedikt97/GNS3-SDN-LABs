#!/usr/bin/python3

import os
import json
import pandas as pd
import sys
from mpls.sonictoolset import *
from mpls.generate import *
from mpls.generate_l3 import *

config_jsons = []
cmd = ''
mgmt_ips = []
username = 'admin'
password = 'YourPaSsWoRd'

with open('hosts', 'r') as f:
     lines = f.read().splitlines()
     for line in lines:
          mgmt_ips.append(line)

def userloop():
     print('Configured Management IPs:')
     print(mgmt_ips)
     cmd = input('''
Next Command? 
[#] Configuration Management            [##] Configuration Tasks                [##] Show-Outputs
-------------------------------------------------------------------------------------------------------------
[0] Generate Configuration
                 
[##] Configuration Checks
--------------------------------                                                                                


* Needs loaded Configurations
\r\n''')
     return(cmd)


print('### NLAB Interactive SONiC Configuration CLI fpr BGP-EVPN ### \r\n')
while(cmd != 'exit'):
        cmd = userloop()
        match cmd:
          case '0':
                  generate_configs = generate_config(mgmt_ips)

