#!/usr/bin/python3

import os
import json
import pandas as pd
import sys
from evpn.sonictoolset import *
from evpn.generate import *
from evpn.generate_l3 import *

config_jsons = []
cmd = ''
sonic_mgmt_ips = []
username = 'admin'
password = 'YourPaSsWoRd'

with open('hosts', 'r') as f:
     lines = f.read().splitlines()
     for line in lines:
          sonic_mgmt_ips.append(line)

def userloop():
     print('Configured Management IPs:')
     print(sonic_mgmt_ips)
     print('Loaded Configs: \r\n')
     for d in config_jsons:
          print(d['DEVICE_METADATA']['localhost']['hostname'])
     if len(config_jsons) == 0:
          print('!!! Please start with [0] - Pulling Configs from Devices !!!')       
     cmd = input('''
Next Command? 
[#] Configuration Management            [##] Configuration Tasks                [##] Show-Outputs
-------------------------------------------------------------------------------------------------------------
[0]Pull configs from devices            [10] Configure User-Interfaces          [20] Show VXLAN-Port-Mappings
[1]Show loaded Config*                  [11] Configure VLAN-VXLAN-Mappings      [21] Show VLXAN-Tunnel
[2]Save config on device                [12] Reset UNIs and VXLAN-Mappings      [22] Show MAC-Table
[3]Dump loaded config to json*          [13] Configure Layer-3 VNI Routing      [23] Show IP-Routing-Table
[4]Reset devices                        [14] Fix VTYSH Configuration            [24] Show VLANs
[5]Push loaded configs to Devices*      [15] Configure Routed VLAN              [25] Show IP Interface
[6]Generate BGP-EVPN base-config*                                               [26] Show Interface
                                                                                [27] Show BGP Peers
                                                                                [28] Show LLDP
                                                                                [29] Show remote Macs
                                                                                [30] Show EVPN routes
[##] Configuration Checks
--------------------------------                                                                                
[30] Test Loopback connectivity*

* Needs loaded Configurations
\r\n''')
     return(cmd)

def configloop_interface():
    rangex = input('Interface ID: ')
    rangey = rangex
    vlan = input('Access Vlan for Interface [' + str(rangex) + ']: ')
    config = create_vlan_port_config(rangex, rangey, vlan)
    print(json.dumps(config, indent='   '))
    user = input('Write to all devices ?[y/n]')
    if 'y' in user:
        load_config(config, sonic_mgmt_ips,username,password)
    elif 'n' in user:
        deviceid = input("Write to Devices ? [MGMT_IP];[MGMT_IP2]...")
        ips = deviceid.split(';')
        load_config(config, ips,username,password)
    else:
         return

def configloop_vxlan():
    vlan = input('VLAN ID: ')
    vxlan = input('VXLAN VNI: ')
    config = create_vxlan_port_mapping(vlan,vxlan)
    print(json.dumps(config, indent='   '))
    user = input('Write to all devices ?[y/n]')
    if 'y' in user:
        load_config(config, sonic_mgmt_ips,username,password)
    else:
         return

print('### NLAB Interactive SONiC Configuration CLI fpr BGP-EVPN ### \r\n')
while(cmd != 'exit'):
        cmd = userloop()
        match cmd:
          case '0':
            print('[0]- Pulling Config from Devices...')
            config_jsons = get_config(username, password, sonic_mgmt_ips)
          case '1':
            print('[1]- Show Config from Devices...')
            i = 0
            for config in config_jsons:
                 print('['+str(i)+'] - ' + config['DEVICE_METADATA']['localhost']['hostname'])
                 i += 1
            input_i = input('Specifiy Config by ID: ')
            print('Available Keys: ')
            for config_element in config_jsons[int(input_i)]:
               print(config_element)
            input_y = input('Specifiy Config by Key or type "ALL": ')
            try:
               if not 'ALL' in input_y:
                    while(input_y != 'exit'):
                         print(json.dumps(config_jsons[int(input_i)][input_y]))
                         input_y = input('Type another Key or "exit" to return: ')
                         
               else:                               
                    print(json.dumps(config_jsons[int(input_i)], indent='    '))
            except():
               print('Bad ID')
            input('Press return to continue...')
          case '2':
             save_config(username, password,sonic_mgmt_ips)
          case '3':
             backup_config(config_jsons,username, password)
          case '4':
             reset_config(username, password, sonic_mgmt_ips)
          case '5':
             push_config(config_jsons, sonic_mgmt_ips, username, password)
          case '6':
            config_jsons = generate_config(config_jsons, sonic_mgmt_ips)

          case '10':
             configloop_interface()
          case '11':
             configloop_vxlan()
          case '12':
             reset_tenant_ports(username, password,sonic_mgmt_ips)
          case '13':
            vni_id = input('Transfer VNI/VLAN?:')
            config = generate_config_l3(vni_id)
            print(json.dumps(config, indent='   '))
            user = input('Write to all devices ?[y/n]')
            if 'y' in user:
                load_config(config, sonic_mgmt_ips,username,password)
          case '14':
                temporary_vtysh_fix(sonic_mgmt_ips, username, password)
          case '15':
            host = input('Specify Switch-Host IP Address: ')
            vlan_id = input('Specifiy VLAN ID: ')
            ip_address = input('Specify CIDR Subnet for Interface: ')
            config_list = generate_routing_interfaces(vlan_id, ip_address)
            for config in config_list:
               print(json.dumps(config, indent='  '))
            user = input('Write to all devices ?[y/n]')
            ip_list = []
            ip_list.append(host)
            if 'y' in user:
                for config in config_list:
                  load_config(config, ip_list,username,password)

          case '20':
             show_vxlan_port_mapping(sonic_mgmt_ips, username, password)
          case '21':
             show_bgp_partner(sonic_mgmt_ips, username, password)
          case '22':
             show_mac(sonic_mgmt_ips, username, password)
          case '23':
             show_iproute(sonic_mgmt_ips, username, password)
          case '24':
             show_vlan(sonic_mgmt_ips, username, password)
          case '25':
             show_ip_interface(sonic_mgmt_ips, username, password)
          case '26':
             show_interface_status(sonic_mgmt_ips, username, password)
          case '27':
             show_bgp(sonic_mgmt_ips, username, password)
          case '28':
             show_lldp(sonic_mgmt_ips, username, password)
          case '29':
             show_vxlan_remotemac(sonic_mgmt_ips, username, password)
          case '30':
             show_evpn_table(sonic_mgmt_ips, username, password)
          

          case '40':
            validate_underlay(config_jsons, username, password)






