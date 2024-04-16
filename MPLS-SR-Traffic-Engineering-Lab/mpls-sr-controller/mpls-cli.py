#!/usr/bin/python3

import os
import json
import pandas as pd
import sys
from mpls.tools import *
from mpls.generate import *
import http
import socket


config_jsons = []
cmd = ''
mgmt_ips = []
username = 'admin'
password = 'arista'

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
[0] Show Configuration                  [10] Configure MPLS-SR / Reset Lab      [20] Show IS-IS State
[1] Write Configuration                 [11] Configure Routed VLAN              [21] Show BGP-EVPN State
[2] Reboot all Switches                 [12] Bind VLAN to Interface             [22] Show EVPN Routes
[3] Download Configs                    [13] Create SR-Tunnel                   [23] Show VLAN Mappings
                                        [14] Add Traffic Policy                 [24] Show MPLS-SR TE Policies
                                                                                [25] Show Color-Mappings
[##] Configuration Checks               [##] Additional Tasks
[30] Check Connectivity                 [40] Disable GRO on all Interfaces
--------------------------------                                                                                


* Needs loaded Configurations
\r\n''')
     return(cmd)

print(socket.gethostbyname(socket.gethostname()))
print('### NLAB - Interactive MPLS-CLI for managing a MPLS Segment Routing Network with Arista vEOS ### \r\n')
while(cmd != 'exit'):
        cmd = userloop()
        match cmd:

          case '0':
               for ip in mgmt_ips:
                    n = show_running_config(ip, username, password)
                    print('#### ' + ip)
                    print(n[0]['result']['output'])
               input('Press enter to return...')

          case '1':
               cmd = 'write'
               for ip in mgmt_ips:
                    c = enable(ip, cmd, username, password)
                    print(c[0]['result']['output'])

          case '2':
               cmd = 'reload now'
               for ip in mgmt_ips:
                    try:
                         c = enable(ip, cmd, username, password)
                    except:
                         pass
                    print('#### ' + ip)
                    print('Reloading...\r\n')

          case '3':
               for ip in mgmt_ips:
                    n = show_running_config(ip, username, password)
                    path = './configs/' + ip + '.txt'
                    with open(path, 'w') as file:
                         print('Writing config from ' + ip + ' to ' + path)
                         file.write(n[0]['result']['output'])
               input('Press enter to return...')
                  

          case '10':
               generated_configs = generate_config(mgmt_ips)
               for config in generated_configs:
                    print(config['mgmt_ip'])
                    configure(config['startup_conf'], config['mgmt_ip'], username, password)
          case '11':
               vlan_id = input('Specify VLAN ID: ')
               default_gw = input('Specify Subnet Gateway [XXX.XXX.XXX.XXX/YY]: ')
               n = 0
               for ip in mgmt_ips:
                    print(str(n) + ' - ' + ip)
                    n += 1
               choosen_n = int(input('Choose Device by ID: '))
               ip = mgmt_ips[choosen_n]
               config_temp = [] 
               config_temp.append('vlan ' + vlan_id)
               config_temp.append('interface Vlan' + vlan_id)
               config_temp.append('     vrf NLAB')
               config_temp.append('     ip address ' + default_gw)
               print('\n'.join(config_temp))

               configure(config_temp, ip, username, password)

          case '12':
               vlan_id = input('Specify VLAN ID: ')
               interface_id = input('Specify Interface ID: ')
               n = 0
               for ip in mgmt_ips:
                    print(str(n) + ' - ' + ip)
                    n += 1
               choosen_n = int(input('Choose Device by ID: '))
               ip = mgmt_ips[choosen_n]
               config_temp = [] 
               config_temp.append('vlan ' + vlan_id)
               config_temp.append('interface Ethernet' + interface_id)
               config_temp.append('switchport access vlan ' + vlan_id)
               print('\n'.join(config_temp))

               configure(config_temp, ip, username, password)

          case '13':
               color = input('Specify Tunnel-Color [eg. GREEN]: ')
               color_id = input('Specifiy Tunnel-ID [eg. 100]: ')
               endpoint_device= input('Choose Endpoint-Device by Loopback IP [eg 10.0.0.45]: ')
               segment_list = input('Specify Label-Stack [eg. 900044 900042 ...]')
               n = 0
               for ip in mgmt_ips:
                    print(str(n) + ' - ' + ip)
                    n += 1
               choosen_n = int(input('Choose Headend-Device by ID: '))
               headend_device = mgmt_ips[choosen_n]
               config_a_temp = [] 
               config_a_temp.append('router traffic-engineering')
               config_a_temp.append('     segment-routing')
               config_a_temp.append('          rib system-colored-tunnel-rib')
               config_a_temp.append('          !')
               config_a_temp.append('          default policy endpoint ' + endpoint_device + ' color ' + color_id)
               config_a_temp.append('          policy endpoint ' + endpoint_device + ' color ' + color_id)
               config_a_temp.append('               binding-sid 1000' + color_id)
               config_a_temp.append('               name ' + color)
               config_a_temp.append('               !')
               config_a_temp.append('               path-group preference 1')
               config_a_temp.append('                    segment-list label-stack ' + segment_list)
               config_a_temp.append('exit')
               config_a_temp.append('exit')
               config_a_temp.append('exit')
               config_a_temp.append('!')
               print(' ### Please review generated config ###')
               print('\n'.join(config_a_temp))
               y = input('Write Config to Device ' + headend_device + ' ? [y/n]: ')
               if 'y' in y:
                    configure(config_a_temp, mgmt_ips[choosen_n], username, password)

          case '14':
               config_temp = []
               n = 0
               for ip in mgmt_ips:
                    print(str(n) + ' - ' + ip)
                    n += 1
               choosen_n = int(input('Choose Device where to place policy: '))
               color_id = input('Specify Tunnel by Color-ID [eg. 300]: ')
               prefix = input('Specify Traffic by destination Prefix [eg. 192.168.2.0/24]: ')
               prefix_name = input('Specify Name for Prefix list [eg. NLAB-02]: ')
               map_seq = input('Specify Route-Map Sequence: ')
               config_temp.append('!')
               config_temp.append('ip prefix-list ' + prefix_name + ' seq 10 permit ' + prefix)
               config_temp.append('!')
               config_temp.append('route-map SET-COLOR permit ' + map_seq)
               config_temp.append('     match ip address prefix-list ' + prefix_name)
               config_temp.append('     set extcommunity color ' + color_id + ' additive')
               config_temp.append('exit')
               config_temp.append('!')
               config_temp.append('router bgp 64020')
               config_temp.append('     vrf NLAB')
               config_temp.append('          route-target export evpn route-map SET-COLOR')
               config_temp.append('exit')
               print('\n'.join(config_temp))
               y = input('Write Config to Device ' + mgmt_ips[choosen_n] + ' ? [y/n]: ')
               if 'y' in y:
                    configure(config_temp, mgmt_ips[choosen_n], username, password)           
             

          case '20':
               cmd = 'show isis neighbors'
               for ip in mgmt_ips:
                    c = enable(ip, cmd, username, password)
                    print('#### ' + ip)
                    print(c[0]['result']['output'])
               input('Press enter to return...')

          case '21':
               cmd = 'show bgp evpn summary'
               for ip in mgmt_ips:
                    c = enable(ip, cmd, username, password)
                    print('#### ' + ip)
                    print(c[0]['result']['output'])
               input('Press enter to return...')

          case '22':
               cmd = 'show bgp evpn'
               for ip in mgmt_ips:
                    c = enable(ip, cmd, username, password)
                    print('#### ' + ip)
                    print(c[0]['result']['output'])
               input('Press enter to return...')

          case '23':
               cmd = 'show interfaces vlans'
               for ip in mgmt_ips:
                    c = enable(ip, cmd, username, password)
                    print('#### ' + ip)
                    print(c[0]['result']['output'])
               input('Press enter to return...')

          case '24':
               cmd = 'show traffic-engineering segment-routing policy segment-list'
               for ip in mgmt_ips:
                    c = enable(ip, cmd, username, password)
                    print('#### ' + ip)
                    print(c[0]['result']['output'])
               input('Press enter to return...')

          case '25':
               cmd = 'show running-config section route-map'
               cmd1 = 'show running-config section ip prefix-list seq'
               for ip in mgmt_ips:
                    c = enable(ip, cmd, username, password)
                    c1 = enable(ip, cmd1, username, password)
                    print('#### ' + ip)
                    print('### - Route Maps \r\n')
                    print(c[0]['result']['output'])
                    print('### - Prefix Lists \r\n')
                    print(c1[0]['result']['output'])
               input('Press enter to return...')

          case '40':
               cmd = 'bash timeout 1 pwd'
               for ip in mgmt_ips:

                    for i in [1,2,3,4,5,6,7,8,9]:
                         cmd = 'bash timeout 1 sudo ethtool --offload vmnicet'+str(i)+' gro off'
                         echocmd = 'bash timeout 1 echo "sudo ethtool --offload vmnicet'+str(i)+' gro off"'
                         c = command(ip, echocmd, username, password)
                         c1 = command(ip, cmd, username, password)
                         print('#### ' + ip)
                         print(c[0]['output'])
                         print(c1[0]['output'])
               input('Press enter to return...')

          case '30':
               for ip in mgmt_ips:
                    c = check_connectivity(ip, username, password)
                    print('# Connectivity for ' + ip)
                    print(c)
               input('Press enter to return...')


          case '40':
               cmd = 'bash timeout 1 pwd'
               for ip in mgmt_ips:

                    for i in [1,2,3,4,5,6,7,8,9]:
                         cmd = 'bash timeout 1 sudo ethtool --offload vmnicet'+str(i)+' gro off'
                         echocmd = 'bash timeout 1 echo "sudo ethtool --offload vmnicet'+str(i)+' gro off"'
                         c = command(ip, echocmd, username, password)
                         c1 = command(ip, cmd, username, password)
                         print('#### ' + ip)
                         print(c[0]['output'])
                         print(c1[0]['output'])
               input('Press enter to return...')

          case '100':
               cmd = ['bash', 'pwd']
               for ip in mgmt_ips:
                    c = command(ip, cmd, username, password)
                    print('#### ' + ip)
                    print(c[0]['result']['output'])


