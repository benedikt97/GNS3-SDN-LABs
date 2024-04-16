
# Python program to read
# json file
import os
import json
import pandas as pd

def generate_config(mgmt_ips):
    generated_configs = []
    links = []
    i = 1
    while i < 255:
        transfer = {"ip1": "10.200.0." + str(i) + "/30", "ip2": "10.200.0." + str(i+1) + "/30"}
        links.append(transfer)
        i += 4

    df = pd.read_csv('topology.csv')
    
    for i in range(len(df.index)):
        df.at[i, "links" ] = i
        df_short = df.iloc[:i]
        a1 = len(df_short[df_short["peer1"] == df.at[i, "peer1"]].index)
        a2 = len(df_short[df_short["peer2"] == df.at[i, "peer1"]].index)
        b1 = len(df_short[df_short["peer1"] == df.at[i, "peer2"]].index)
        b2 = len(df_short[df_short["peer2"] == df.at[i, "peer2"]].index)
        df.at[i, "port1"] = a1 + a2 + 1
        df.at[i, "port2"] = b1 + b2 + 1
    print('Interface Mapping: \r\n')
    print(df)

    ip_index = 0
    for ip in mgmt_ips:
        last_ip_tupel = ip.rsplit('.')[-1]
        config = []

        config.append('! Defaulting some sections')
        config.append('default ip prefix-list NLAB-Prefixes')
        config.append('default route-map NLAB')
        config.append('default route-map SET-COLOR')
        config.append('default router traffic-engineering')
        
        ## Generate VRF
        config.append('!')
        config.append('default vrf defaults')
        config.append('vrf instance NLAB')
        config.append('    rd 64020:1')

        config.append('!')
        config.append('spanning-tree mode none')


        ## Generate Transferlink w Subnets
        interface_gen = {}
        for i in range(len(df.index)):
            if int(last_ip_tupel) == int(df.at[i, 'peer1']):
                id = str(int(df.at[i, 'port1']))
                tf_ip = links[i]
                tf_ip = tf_ip.get("ip1")
                config.append('!')
                config.append('default interface Ethernet' + id)
                config.append('interface Ethernet' + id)
                config.append('    no switchport')
                config.append('    ip address ' + tf_ip)
                config.append('    isis enable ISIS-SR')
                config.append('    speed forced 10full')

        for i in range(len(df.index)):
            if int(last_ip_tupel) == int(df.at[i, 'peer2']):
                id = str(int(df.at[i, 'port2']))
                tf_ip = links[i]
                tf_ip = tf_ip.get("ip2")
                config.append('!')
                config.append('default interface Ethernet' + id)
                config.append('interface Ethernet' + id)
                config.append('    no switchport')
                config.append('    ip address ' + tf_ip)
                config.append('    isis enable ISIS-SR')
                config.append('    speed forced 10full')

#        config.append('!')
#        config.append('interface Management 1')
#        config.append('    ip address ' + ip + '/16')

        ## Generate Loopback
        loopback_ip = "10.0.0." + last_ip_tupel 
        config.append('!')
        config.append('default interface Loopback1')
        config.append('interface Loopback1')
        config.append('    ip address ' + loopback_ip + '/32')
        config.append('    node-segment ipv4 index ' + last_ip_tupel)
        config.append('    isis enable ISIS-SR')
        loopback_ip2 = "10.0.40." + last_ip_tupel + '/32'

#        config.append('!')
        config.append('no interface Loopback2')
#        config.append('interface Loopback2')
#        config.append('    vrf NLAB')
#        config.append('    ip address ' + loopback_ip2)

        config.append('!')
        config.append('default ip routing')
        config.append('ip routing')
        config.append('ip routing vrf NLAB')

        config.append('!')
        config.append('mpls ip')

        config.append('!')
        config.append('default router bgp')
        config.append('router bgp 64020')
        config.append('    router-id ' + loopback_ip)
        config.append('    neighbor NLAB-CORE peer group')
        config.append('    neighbor NLAB-CORE remote-as 64020')
        config.append('    neighbor NLAB-CORE next-hop-self')
        config.append('    neighbor NLAB-CORE update-source Loopback1')
        config.append('    neighbor NLAB-CORE additional-paths receive')
        config.append('    neighbor NLAB-CORE additional-paths send any')
        config.append('    neighbor NLAB-CORE send-community standard extended')
        config.append('    neighbor NLAB-CORE maximum-routes 0')

        for rem_ip in mgmt_ips:
            rem_last_ip_tupel = rem_ip.split('.')[-1]
            if rem_last_ip_tupel == last_ip_tupel:
                continue
            rem_loopback_ip = '10.0.0.' + rem_last_ip_tupel
            config.append('    neighbor ' + rem_loopback_ip + ' peer group NLAB-CORE')

        config.append('    !')
        config.append('    address-family evpn')
        config.append('        neighbor default encapsulation mpls next-hop-self source-interface Loopback1')
        for rem_ip in mgmt_ips:
            rem_last_ip_tupel = rem_ip.split('.')[-1]
            if rem_last_ip_tupel == last_ip_tupel:
                continue
            rem_loopback_ip = '10.0.0.' + rem_last_ip_tupel
            config.append('    neighbor ' + rem_loopback_ip + ' activate')
 
        config.append('    !')
        config.append('    vrf NLAB')
        config.append('         route-target import evpn 64020:1')
        config.append('         route-target export evpn 64020:1')
        config.append('         rd 64020:1')
        config.append('         redistribute connected')

        config.append('!')
        config.append('default router isis ISIS-SR')
        config.append('router isis ISIS-SR')
        config.append('    net 20.0000.0020.0200.20' + last_ip_tupel + '.00')
        config.append('    is-type level-2')
        config.append('    !')
        config.append('    address-family ipv4 unicast')
        config.append('    !')
        config.append('    segment-routing mpls')
        config.append('        router-id 10.0.0.' + last_ip_tupel)
        config.append('        no shutdown')
        config.append('!')
        config.append('traffic-engineering')
        config.append('    no shutdown')

        config.append('!')
        config.append('end')
 
        print('\n'.join(config))

#        with open(ip + '.conf', 'w') as f:
#            for line in config:
#                f.write("%s\n" % line)

        config_dict = {'mgmt_ip': ip, 'startup_conf': config}
        generated_configs.append(config_dict) 


    return generated_configs





    



