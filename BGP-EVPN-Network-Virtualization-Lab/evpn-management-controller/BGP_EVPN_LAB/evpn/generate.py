
# Python program to read
# json file
import os
import json
import pandas as pd

def generate_config(configurations, sonic_mgmt_ips):
    generated_configs = []
    links = []
    i = 1
    while i < 255:
        transfer = {"ip1": "192.168.5." + str(i) + "/30", "ip2": "192.168.5." + str(i+1) + "/30"}
        links.append(transfer)
        i += 4
#    link_map = []
#    link_map.append({"peer1": 41, "peer2": 44})
#    link_map.append({"peer1": 41, "peer2": 43})
#    link_map.append({"peer1": 43, "peer2": 44})
#    link_map.append({"peer1": 43, "peer2": 45})
#    link_map.append({"peer1": 42, "peer2": 44})
#    link_map.append({"peer1": 42, "peer2": 45})
#    df = pd.DataFrame(link_map)
#    df.to_csv('topology.csv')

    df = pd.read_csv('topology.csv')
    

    for i in range(len(df.index)):
        df.at[i, "links" ] = i
        df_short = df.iloc[:i]
        a1 = len(df_short[df_short["peer1"] == df.at[i, "peer1"]].index)
        a2 = len(df_short[df_short["peer2"] == df.at[i, "peer1"]].index)
        b1 = len(df_short[df_short["peer1"] == df.at[i, "peer2"]].index)
        b2 = len(df_short[df_short["peer2"] == df.at[i, "peer2"]].index)
        df.at[i, "port1"] = a1 + a2 
        df.at[i, "port2"] = b1 + b2
    print('Interface Mapping: \r\n')
    print(df)

    ip_index = 0
    for startup_conf in configurations:
        host = ''
        host = sonic_mgmt_ips[ip_index]
        ip_index += 1
        last_ip_tupel = host.rsplit('.')[-1]
        
        ## Generate Device Metadata
        localhost = {}
        device_metadata_gen = {}
        startup_conf["DEVICE_METADATA"]["localhost"]["hostname"] = "SONiC-" + last_ip_tupel
        startup_conf["DEVICE_METADATA"]["localhost"]["frr_mgmt_framework_config"] = "true"
        startup_conf["DEVICE_METADATA"]["localhost"]["mgmt_ip"] = host
        startup_conf["DEVICE_METADATA"]["localhost"]["bgp_asn"] = "64020"
        device_metadata_gen["localhost"] = localhost

        ## MGMT Interface
        mgmt_interface_gen = {}
        mgmt_interface_gen["eth0"] = {}
        mgmt_interface_gen["eth0|"+host] = {}

        ## Generate Loopback
        loopback_ip = "10.0.3." + last_ip_tupel
        loopback_gen = {"Loopback0": {}}
        loopback_int_gen = {"Loopback0": {}, "Loopback0|" + loopback_ip + "/32": {}}

        ## Generate Transferlink w Subnets
        interface_gen = {}
        for i in range(len(df.index)):
            if int(last_ip_tupel) == int(df.at[i, 'peer1']):
                id = str(int(df.at[i, 'port1'])*4)
                ip = links[i]
                ip = ip.get("ip1")
                interface_gen["Ethernet" + id] = {}
                interface_gen["Ethernet" + id + "|" + ip] = {}

        for i in range(len(df.index)):
            if int(last_ip_tupel) == int(df.at[i, 'peer2']):
                id = str(int(df.at[i, 'port2'])*4)
                ip = links[i]
                ip = ip.get("ip2")
                interface_gen["Ethernet" + id] = {}
                interface_gen["Ethernet" + id + "|" + ip] = {}

        ## Generate OSPF Configuration
        ospfv2_router_gen = {}
        default = {}
        default["enable"] = "true"
        default["router-id"] = loopback_ip
        ospfv2_router_gen['default'] = default
        ospfv2_router_area_gen = {}
        ospfv2_router_area_gen["default|0.0.0.0"] = {}
        ospfv2_router_area_network_gen = {}
        ospfv2_router_area_network_gen["default|0.0.0.0|" + loopback_ip + "/32"] = {}
        for i in interface_gen:
            if '|' in i:
                ip = i.rsplit('|')[-1]
                ospfv2_router_area_network_gen["default|0.0.0.0|" + ip] = {}

        ## Generate BGP Configuration
        bgp_globals_gen = {}
        default = {}
#        default["always_compare_med"] = "false"
#        default["ebgp_requires_policy"] = "false"
#        default["external_compare_router_id"] = "false"
#        default["fast_external_failover"] = "true"
#        default["holdtime"] = "180"
#        default["ignore_as_path_length"] = "false"
#        default["keepalive"] = "60"
#        default["load_balance_mp_relax"] = "false"
        default["local_asn"] = "64020"
#        default["log_nbr_state_changes"] = "true"
#        default["network_import_check"] = "true"
#        default["router-id"] = loopback_ip
        bgp_globals_gen["default"] = default

        bgp_globals_af_gen = {}
        default_l2 = {}
        default_l2["advertise-all-vni"] = "true"
#        default_l2["dad-enabled"] = "true"
        bgp_globals_af_gen["default|l2vpn_evpn"] = default_l2

        bgp_neighbor_gen = {}
        for ip in sonic_mgmt_ips:
            rem_last_ip_tupel = ip.split('.')[-1]
            rem_loopback_ip = "10.0.3." + rem_last_ip_tupel
            if rem_loopback_ip == loopback_ip:
                continue
            default = {}
            default["admin_status"] = "true"
            default["peer_type"] = "internal"
            default["local_addr"] = loopback_ip
            default["name"] = "SONiC" + rem_last_ip_tupel
            bgp_neighbor_gen["default|"+rem_loopback_ip] = default 

        bgp_neighbor_af_gen = {}
        for ip in sonic_mgmt_ips:
            rem_last_ip_tupel = ip.split('.')[-1]
            rem_loopback_ip = "10.0.3." + rem_last_ip_tupel
            if rem_loopback_ip == loopback_ip:
                continue
            default = {}
            bgp_neighbor_af_gen["default|"+rem_loopback_ip+"|l2vpn_evpn"] = {"admin_status": "true"}

        ## Configure EVPN and VXLAN
        vxlan_tunnel_gen = {}
        vtep_gen = {}
        vtep_gen["src_ip"] = loopback_ip
        vxlan_tunnel_gen["vtep"] = vtep_gen        
        vxlan_evpn_nvo_gen = {}
        nvo_hsrm_gen = {}
        nvo_hsrm_gen["source_vtep"] = "vtep"
        vxlan_evpn_nvo_gen["nvo-hsrm"] = nvo_hsrm_gen 

        ## Write to Config Files
        print('Write to JSON')
        path_out = './json-up-part/' + ip + '.json'
        generated_config = {}
        generated_config['DEVICE_METADATA'] = startup_conf['DEVICE_METADATA']
        generated_config['PORT'] = startup_conf['PORT']
        generated_config['INTERFACE'] = interface_gen
        generated_config['MGMT_INTERFACE'] = mgmt_interface_gen
        generated_config['LOOPBACK'] = loopback_gen
        generated_config['LOOPBACK_INTERFACE'] = loopback_int_gen
        generated_config['OSPFV2_ROUTER'] = ospfv2_router_gen
        generated_config['OSPFV2_ROUTER_AREA'] = ospfv2_router_area_gen
        generated_config['OSPFV2_ROUTER_AREA_NETWORK'] = ospfv2_router_area_network_gen
        generated_config['BGP_GLOBALS'] = bgp_globals_gen
        generated_config['BGP_GLOBALS_AF'] = bgp_globals_af_gen
        generated_config['BGP_NEIGHBOR'] = bgp_neighbor_gen
        generated_config['BGP_NEIGHBOR_AF'] = bgp_neighbor_af_gen
        generated_config['VXLAN_EVPN_NVO'] = vxlan_evpn_nvo_gen
        generated_config['VXLAN_TUNNEL'] = vxlan_tunnel_gen

        generated_configs.append(generated_config)

    return generated_configs





    



