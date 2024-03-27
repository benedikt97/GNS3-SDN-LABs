
# Python program to read
# json file
import os
import json
import pandas as pd

def generate_config_l3(vni_vlan_id):
        
        vrf_gen = {}
        vrf_01_gen = {}
        vrf_01_gen['fallback'] = "false"
        vrf_01_gen['vni'] = str(vni_vlan_id)
        vrf_gen["Vrf01"] = vrf_01_gen

        vlan_gen = {}
        vlan_gen['Vlan'+str(vni_vlan_id)] = {}

        vlan_interface_gen = {}
        vlan_interface_gen['Vlan'+str(vni_vlan_id)] = {"vrf_name": "Vrf01"}

        vxlan_tunnel_map_gen = {}
        vtep_gen = {}
        vtep_gen["vlan"] = "Vlan"+str(vni_vlan_id)
        vtep_gen["vni"] = str(vni_vlan_id)
        vxlan_tunnel_map_gen["vtep|map_"+str(vni_vlan_id)+"_Vlan"+str(vni_vlan_id)] = vtep_gen

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
        bgp_globals_gen["Vrf01"] = default

        bgp_globals_af_gen = {}
        vrf01_l2 = {}
        vrf01_l2["dad-enabled"] = "true"
        vrf01_ipv4 = {}
        vrf01_ipv4["max_ebgp_paths"] = "1"
        vrf01_ipv4["max_ibgp_paths"] = "1"
        vrf01_ipv4["route_flap_dampen"] = "false"

        bgp_globals_af_gen["Vrf01|l2vpn_evpn"] = vrf01_l2
        bgp_globals_af_gen["Vrf01|ipv4_unicast"] = vrf01_ipv4

        route_redistribute_gen = {}
        route_redistribute_gen["Vrf01|connected|bgp|ipv4"] = {}
        
        bgp_globals_route_advertise = {}
        bgp_globals_route_advertise["Vrf01|L2VPN_EVPN|IPV4_UNICAST"] = {}

        ## Write to Config Files
        generated_config = {}
        generated_config['VRF'] = vrf_gen
        generated_config['VLAN'] = vlan_gen
        generated_config['VLAN_INTERFACE'] = vlan_interface_gen
        generated_config['VXLAN_TUNNEL_MAP'] = vxlan_tunnel_map_gen
        generated_config['BGP_GLOBALS'] = bgp_globals_gen
        generated_config['BGP_GLOBALS_AF'] = bgp_globals_af_gen
        generated_config['BGP_GLOBALS_ROUTE_ADVERTISE'] = bgp_globals_route_advertise
        generated_config['ROUTE_REDISTRIBUTE'] = route_redistribute_gen
        return(generated_config)




def generate_routing_interfaces(vlan_id,ip_addr):
        config_list = []
        config = {}
        config['VLAN'] = {'Vlan'+vlan_id: {"vlanid": vlan_id}}
        config['VLAN_INTERFACE'] = {'Vlan'+vlan_id: {"vrf_name": "Vrf01"}}
        config_list.append(config)
        config = {}
        config['VLAN_INTERFACE'] = {'Vlan'+vlan_id: {}, 'Vlan'+vlan_id+'|' + ip_addr:  {}}
        config_list.append(config)
        return config_list
    



