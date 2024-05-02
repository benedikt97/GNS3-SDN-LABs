!
frr version 8.5.1
frr defaults traditional
hostname SONiC-45
log syslog informational
log facility local4
no zebra nexthop kernel enable
fpm address 127.0.0.1
no fpm use-next-hop-groups
agentx
no service integrated-vtysh-config
!
password zebra
enable password zebra
!
router bgp 64020 vrf Vrf01
 no bgp default ipv4-unicast
 !
 address-family ipv4 unicast
  redistribute connected
  maximum-paths 1
  maximum-paths ibgp 1
 exit-address-family
exit
!
router bgp 64020
 no bgp default ipv4-unicast
 neighbor 10.0.3.41 remote-as internal
 neighbor 10.0.3.41 description SONiC41
 neighbor 10.0.3.41 update-source 10.0.3.45
 neighbor 10.0.3.42 remote-as internal
 neighbor 10.0.3.42 description SONiC42
 neighbor 10.0.3.42 update-source 10.0.3.45
 neighbor 10.0.3.43 remote-as internal
 neighbor 10.0.3.43 description SONiC43
 neighbor 10.0.3.43 update-source 10.0.3.45
 neighbor 10.0.3.44 remote-as internal
 neighbor 10.0.3.44 description SONiC44
 neighbor 10.0.3.44 update-source 10.0.3.45
 !
 address-family l2vpn evpn
  neighbor 10.0.3.41 activate
  neighbor 10.0.3.42 activate
  neighbor 10.0.3.43 activate
  neighbor 10.0.3.44 activate
  advertise-all-vni
 exit-address-family
exit
!
router ospf
 ospf router-id 10.0.3.45
 network 10.0.3.45/32 area 0.0.0.0
 network 192.168.5.12/30 area 0.0.0.0
 network 192.168.5.20/30 area 0.0.0.0
exit
!
ip nht resolve-via-default
!
ipv6 nht resolve-via-default
!
end