import pyeapi
import os
import sys


def show_running_config(host_ip, username, password):
    node = pyeapi.connect(transport='http', host=host_ip, username=username, password=password, return_node=True)
    return node.enable('show running-config', encoding='text')

def show_routes(host_ip, username, password):
    node = pyeapi.connect(transport='http', host=host_ip, username=username, password=password, return_node=True)

def check_connectivity(host_ip, username, password):
    node = pyeapi.connect(transport='http', host=host_ip, username=username, password=password, return_node=True)
    try:
        sys.stdout = open(os.devnull, 'w')
        n =  node.enable('show hostname', encoding='text')
        sys.stdout = sys.__stdout__
        return(n[0]['result']['output'] + 'Node reachable!')
    except:
        return('Node ' + host_ip + ' not reachable')
    
def reboot_nodes(host_ip, username, password):
    try:
        node = pyeapi.connect(transport='http', host=host_ip, username=username, password=password, return_node=True)
        sys.stdout = open(os.devnull, 'w')
        n =  node.enable('reload now', encoding='text')
        sys.stdout = sys.__stdout__
        return(n[0]['result']['output'] + 'Node shutting down')
    except:
        return('Node ' + host_ip + ' not reachable')
        

def enable(host_ip, cmd, username, password):
    node = pyeapi.connect(transport='http', host=host_ip, username=username, password=password, return_node=True)
    return node.enable(cmd , encoding='text')

def command(host_ip, cmd, username, password):
    node = pyeapi.connect(transport='http', host=host_ip, username=username, password=password, return_node=True, timeout=3)
    return node.run_commands(cmd , encoding='text',)

def configure(config, host_ip, username, password):
    node = pyeapi.connect(transport='http', host=host_ip, username=username, password=password, return_node=True)
    node.config(config)

def show_sr_tunnel(mgmt_ips, username, password):
    print('## Available Tunnel: ')
    for host_ip in mgmt_ips:
        node = pyeapi.connect(transport='http', host=host_ip, username=username, password=password, return_node=True)
        run_conf = node.running_config.splitlines()
        o = node.enable('show running-config section policy')
        hostname = 'unknown'
        for config_line in run_conf:
            if 'hostname ' in config_line and len(config_line.split()) == 2:
                hostname = config_line.split()[-1]
        print('### ' + hostname)
        print(o[0]['result']['output'])



        
    

