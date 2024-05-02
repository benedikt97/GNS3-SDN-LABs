import sys
import paramiko
import json
from scp import SCPClient
import pandas as pd
from tabulate import tabulate

### SSH-TOOLS ###
def sshcmd(ip, cmd, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip , username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read()
    stdin.close()
    ssh.close()
    return output

def scpcmd_get(ip, src, dst, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip , username=username, password=password)
    scp = SCPClient(ssh.get_transport())
    output = scp.get(src, dst)
    ssh.close()
    return(output)

def scpcmd_put(ip, src, dst, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip , username=username, password=password)
    scp = SCPClient(ssh.get_transport())
    output = scp.put(src, dst)
    ssh.close()
    return(output)

### CONFIG-MANAGEMENT ###
def save_config(username, password, sonic_mgmt_ips):
    print("Reload Config on all Hosts")
    for ip in sonic_mgmt_ips:
        print('Saving: '+str(ip))
        sh_cmd = "sudo config save -y"
        print(sshcmd(ip, sh_cmd, username, password))

def reload_config(username, password, sonic_mgmt_ips):
    print("Reload Config on all Hosts")
    for ip in sonic_mgmt_ips:
        print('Reload: '+str(ip))
        sh_cmd = "sudo config reload -y"
        print(sshcmd(ip, sh_cmd, username, password))

def reset_config(username, password, sonic_mgmt_ips):
    print("Reset Config on all Hosts")
    for ip in sonic_mgmt_ips:
        cmd = "sudo rm /etc/sonic/config_db.json"
        out = sshcmd(ip, cmd, username, password).decode('utf-8')
        cmd = "sudo config-setup factory"
        out = sshcmd(ip, cmd, username, password).decode('utf-8')
        scpcmd_get(ip, "/etc/sonic/config_db.json", "temp.json", username, password)
        conf = json.load(open('temp.json'))
        mgmt_interface_gen = {}
        mgmt_interface_gen["eth0"] = {}
        mgmt_interface_gen["eth0|"+ip] = {}
        conf["MGMT_INTERFACE"] = mgmt_interface_gen
        with open("temp.json", "w") as target:
            json.dump(conf, target, indent='    ')
        scpcmd_put(ip, "temp.json", "~/reset-conf.json", username, password)
        cmd = "sudo config reload reset-conf.json -f -y"
        out = sshcmd(ip, cmd, username, password).decode('utf-8')
        print(out)

def backup_config(configs, username, password):
    print("Backup Config from all Hosts")
    for config in configs:
        switch_id = config['DEVICE_METADATA']['localhost']['hostname']
        with open(switch_id+'.json', "w") as target:
            json.dump(config, target, indent='    ')

def get_config(username, password, sonic_mgmt_ips):
    print("Pull config from all Hosts")
    result = []
    for ip in sonic_mgmt_ips:
#        cmd = "sudo config save -y"
#        out = sshcmd(ip, cmd, username, password).decode('utf-8')
        cmd = "sudo chmod +rx /etc/sonic/config_db.json"
        out = sshcmd(ip, cmd, username, password).decode('utf-8')
        scpcmd_get(ip, "/etc/sonic/config_db.json", "temp.json", username, password)
        result.append(json.load(open("temp.json")))
        temp_json = json.load(open("temp.json"))
        print("Pulled " + ip)
    return(result)

def load_config(conf, sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        print("Push config on " + str(ip))
        with open("temp.json", "w") as target:
            json.dump(conf, target, indent='    ')
        scpcmd_put(ip, "temp.json", "~/temp.json", username, password)
        cmd = "sudo config load temp.json -y"
        out = sshcmd(ip, cmd, username, password).decode('utf-8')
        print(out)

def push_config(confs, sonic_mgmt_ips, username, password):
    i = 0
    for conf in confs:
        ip = conf['DEVICE_METADATA']["localhost"]['mgmt_ip']
        print("Push config on " + str(ip))
        with open("temp.json", "w") as target:
            json.dump(conf, target, indent='    ')
        scpcmd_put(ip, "temp.json", "~/temp.json", username, password)
        cmd = "sudo config reload -f temp.json -y"
        out = sshcmd(ip, cmd, username, password).decode('utf-8')
        print(out)
        i += 1
### CONFIG GENERATORS ###
def reset_tenant_ports(username, password, sonic_mgmt_ips):
    print("Reset Tenant-Port-Config on all Hosts")
    for ip in sonic_mgmt_ips:
        cmd = "sudo chmod +rx /etc/sonic/config_db.json"
        out = sshcmd(ip, cmd, username, password).decode('utf-8')
        scpcmd_get(ip, "/etc/sonic/config_db.json", "trash-conf.json", username, password)
        trash_conf = json.load(open('trash-conf.json'))
        trash_conf['VLAN'] = {}
        trash_conf['VLAN_MEMBER'] = {}
        trash_conf['VXLAN_TUNNEL_MAP'] = {}
        conf = trash_conf
        with open("temp.json", "w") as target:
            json.dump(conf, target, indent='    ')
        scpcmd_put(ip, "temp.json", "~/reset-conf.json", username, password)
        cmd = "sudo config reload reset-conf.json -y"
        out = sshcmd(ip, cmd, username, password).decode('utf-8')
        print(out)

def create_vlan_port_config(rangex, rangey, vlan):
    rangex = int(rangex)
    rangey = int(rangey)
    vlan_gen = {}
    vlanx_gen = {}
    suppress_vlan_neigh_gen = {}
    members = []
    vlan_member_gen = {}
    while rangex <= rangey:
        members.append("Ethernet"+str(rangex))
        vlan_member_gen["Vlan"+str(vlan)+"|Ethernet"+str(rangex)] = {"tagging_mode": "untagged"}
        rangex += 1
    vlanx_gen['members'] = members
    vlan_gen['Vlan'+str(vlan)] = vlanx_gen
    suppress_vlan_neigh_gen['Vlan'+str(vlan)] = {'suppress': 'on'}
    config = {}
    config['VLAN'] = vlan_gen
    config['VLAN_MEMBER'] = vlan_member_gen
    config['SUPPRESS_VLAN_NEIGH'] = suppress_vlan_neigh_gen
    return(config)

def create_vxlan_port_mapping(vlan, vxlan):
    config = {}
    vtep_gen = {}
    vtep_gen['vtep|map_'+str(vxlan)+'_Vlan'+str(vlan)] = {"vlan": "Vlan"+str(vlan), "vni": str(vxlan)}
    config['VXLAN_TUNNEL_MAP'] = vtep_gen
    return(config)

def temporary_vtysh_fix(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        print('# Fixing: ' + ip)
        scpcmd_put(ip, "files/vtysh-fix.cmd", "~/vtysh-fix.cmd", username, password)
        cmd = 'sudo mv ~/vtysh-fix.cmd /etc/ /etc/sonic/frr'
        out = sshcmd(ip, cmd, username, password).decode('utf-8')
        print(out)
        cmd = "vtysh -f '/etc/frr/vtysh-fix.cmd'"
        out = sshcmd(ip, cmd, username, password).decode('utf-8')
        print(out)
        cmd = "vtysh -c 'show running-config bgpd'"
        out = sshcmd(ip, cmd, username, password).decode('utf-8')
        print(out)
        sshcmd


### SHOW COMMANDS ###
def show_vxlan_port_mapping(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        print('#'+ip+'\r\n')
        cmd = 'show vxlan vlanvnimap'
        print(sshcmd(ip, cmd, username, password).decode('utf-8'))

def show_mac(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        print('#'+ip+'\r\n')
        cmd = 'show mac'
        print(sshcmd(ip, cmd, username, password).decode('utf-8'))

def show_iproute(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        cmd = 'show ip route vrf all'
        print('#'+ip+'\r\n')
        print(sshcmd(ip, cmd, username, password).decode('utf-8'))

def show_vlan(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        cmd = 'show vlan brief'
        print('#'+ip+'\r\n')
        print(sshcmd(ip, cmd, username, password).decode('utf-8'))

def show_bgp_partner(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        print('# BGP Peers for: ' + ip)
        cmd = 'vtysh -c "show bgp l2vpn evpn summary"'
        print(sshcmd(ip, cmd, username, password).decode('utf-8'))

def show_interface_status(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        cmd = 'show interface status'
        print(sshcmd(ip, cmd, username, password).decode('utf-8'))

def show_ip_interface(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        cmd = 'show ip interface '
        print(sshcmd(ip, cmd, username, password).decode('utf-8'))

def show_bgp(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        print('# BGP Peers for: ' + ip)
        cmd = "vtysh -c 'show bgp summary'"
        print(sshcmd(ip, cmd, username, password).decode('utf-8'))

def show_lldp(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        cmd = "sonic-cli -c 'show lldp neighbor'"
        print(sshcmd(ip, cmd, username, password).decode('utf-8'))

def show_vxlan_remotemac(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        cmd = "show vxlan remotemac all"
        print('# Device: ' + ip)
        print(cmd)
        print(sshcmd(ip, cmd, username, password).decode('utf-8'))

def show_evpn_table(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        cmd = "vtysh -c 'show bgp l2vpn evpn'"
        print('# Device: ' + ip)
        print(cmd)
        print(sshcmd(ip, cmd, username, password).decode('utf-8'))
   






def validate_underlay(configurations, username, password):
        all_ips =[]
        all_hosts = []
        loopback_ips = []
        ip = ''
        for data in configurations:
            for line in data['MGMT_INTERFACE']:
                if '|' in line:
                    ip = line.split('|')[1]
                    all_hosts.append(ip)
            print("Pinging from direct connected Interfaces" + str(ip))
            for i in data['INTERFACE']:
                if '|' in i:
                    pip =  i.rsplit('/',1)[0]
                    pip =  pip.rsplit('|',1)[1]
                    lastTupel = int(pip.rsplit('.',1)[1])
                    if (lastTupel%2) == 0:
                        lastTupel = lastTupel - 1
                    else:
                        lastTupel = lastTupel + 1
                    npip = pip.rsplit('.',1)[0] + '.' + str(lastTupel)
                    all_ips.append(npip)
                    cmd = 'ping -c1 ' + npip
                    out = sshcmd(ip, cmd, username, password).decode('utf-8').replace('\r', '').replace('\n', '')
                    prt = ip + ' to ' + npip + ' = ' + str(out)[:100]
                    print(prt)
            for i in data['LOOPBACK_INTERFACE']:
                if "|" in i:
                    lip = i.rsplit('/',1)[0]
                    lip =  lip.rsplit('|',1)[1]
                    loopback_ips.append(lip)
        for ip in all_hosts:
            print('Pinging all Loopbacks from ' + str(ip))
            for npip in loopback_ips:
                cmd = 'ping -c1 ' + npip
                out = sshcmd(ip, cmd, username, password).decode('utf-8').replace('\r', '').replace('\n', '')
                prt = ip + ' to ' + npip + ' = ' + str(out)[:100]
                print(prt)

def disable_gro(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        print('## Disabling GRO on: ' + ip)
        for dev in ['eth1', 'eth2', 'eth3', 'eth4', 'eth5', 'eth6', 'eth7', 'eth8', 'eth9']:
            cmd = 'sudo ethtool --offload ' + dev + ' gro off'
            out = sshcmd(ip, cmd, username, password).decode('utf-8')
            print(cmd)
            print(out)

def show_vtysh_config(sonic_mgmt_ips, username, password):
    for ip in sonic_mgmt_ips:
        print('## vtysh config for: ' + ip)
        cmd = 'vtysh -c "show running-config"'
        out = sshcmd(ip, cmd, username, password).decode('utf-8')
        print(cmd)
        print(out)

