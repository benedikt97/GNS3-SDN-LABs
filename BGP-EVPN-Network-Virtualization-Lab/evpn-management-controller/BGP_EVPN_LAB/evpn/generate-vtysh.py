
# Python program to read
# json file
import os
import json
import pandas as pd

def generate_config(mgmt_ips):
    for mgmt_ip in mgmt_ips:
        config = []
        last_ip_tupel = mgmt_ip.split('.')[-1]
        loopback_bgp = '10.0.3.'
        my_loopback_bgp = loopback_bgp + last_ip_tupel

        ## BGP Konfiguration
        config.append('!')
        config.append('router bgp 64020')
        config.append(' no bgp default ipv4-unicast')
        for rem_mgmt_ip in mgmt_ips:
            if last_ip_tupel in rem_mgmt_ip:
                continue
            neighbor_loopback = loopback_bgp + rem_mgmt_ip.split('.')[-1]
            config.append(' neighbor ' + neighbor_loopback + ' remote-as internal')
            config.append(' neighbor ' + neighbor_loopback + ' update-source ' + my_loopback_bgp)
        config.append(' !')
        config.append(' address-family l2vpn evpn')
        config.append('  advertise-all-vni')
        for rem_mgmt_ip in mgmt_ips:
            if last_ip_tupel in rem_mgmt_ip:
                continue
            neighbor_loopback = loopback_bgp + rem_mgmt_ip.split('.')[-1]
            config.append('  neighbor ' + neighbor_loopback + ' activate')
        config.append(' exit-address-family')
        config.append('exit')

        ## OSPF Konfiguration
        config.append('!')
        config.append('router ospf')
        config.append(' ospf router-id ' + my_loopback_bgp)
        config.append(' TBD...')
        config.append('exit')

        ## VRF Konfiguration
        config.append('!')
        config.append('router bgp 64020 vrf Vrf01')
        config.append(' no bgp default ipv4-unicast')
        config.append('!')
        config.append(' address-family ipv4 unicast')
        config.append('  redistribute connected')
        config.append(' exit-address-family')
        config.append('exit')

        print('\n'.join(config))

    
generate_config(['172.30.240.41', '172.30.240.42', '172.30.240.43', '172.30.240.44', '172.30.240.45'])