BGP-EVPN: Verteilter und Broadcast-optimierter Ansatz mit SONiC
===============================================================

Architektur und Technologien
----------------------------

Bei diesem Ansatz wird ein virtuelles Overlay-Netzwerk mit VXLAN
zwischen den Switchen gespannt. Mittels BGP-EVPN werden MAC-Adressen
zwischen Tunnel-Endpunkten durch BGP propagiert. Während die lokale
Weiterleitung zwischen den Schnittstellen eines Switches weiterhin wie
bei einer klassischen Bridge funktioniert, werden zur Weiterleitung von
Paketen zwischen zwei Switchen VXLAN Tunnel eingesetzt. Diese Tunnel
terminieren auf den jeweiligen Switchen mit User-Frontports. Auf
Broadcasts kann zu großen Teilen verzichtet werden, da
Erreichbarkeitsinformationen zwischen den VTEPs synchronisiert werden
und damit [arp]{acronym-label="arp" acronym-form="singular+short"} und
Unknown Unicast Pakete nicht zwischen den VTEPs geflutet werden muss.
Zusätzlich baut BGP-EVPN automatisch benötigte Tunnel auf, was durch die
Notwendigkeit eines Full-Meshes Komplexität der Konfiguration reduziert.
Full-Meshed bedeutet das ein Tunnel zwischen jedem der
Kommunikationspartner errichtet ist.

![BGP-EVPN Architektur](media/vxlan-arch.png){width="100%"}

Für diesen Ansatz werden mehrere Schichten konfiguriert.

### Underlay Netzwerk

Die Aufgabe dieser Schicht ist die Kommunikation zwischen den
Loopback-Interfaces der Switche herzustellen. Diese Loopback-Interfaces
werden weiterhin als Tunnel-Endpunkte verwendet und müssen Daten
untereinander austauschen. Diese Schicht ist damit auch verantwortlich
für die Redundanz, die Konvergenz sowie potentielles Load-Sharing für
die Verbindungen zwischen den Switchen. Aus diesem Grund ist die
Verwendung eines Routingprotokolls wie OSPF sinnvoll.

### Overlay Netzwerk

Als Overlay-Technologie wird VXLAN eingesetzt. Auf den Switchen mit
[uni]{acronym-label="uni" acronym-form="singular+short"}s werden dafür
VXLAN-[vtep]{acronym-label="vtep" acronym-form="singular+short"}s
konfiguriert, sowie Mappings zwischen angelegten lokalen VLANs und
global eindeutigen VXLAN Network Identifiern (VNI) erstellt. Der weitere
Schritt, die Konfiguration von Tunnel-Gegenstellen wird durch BGP-EVPN
erledigt.

### Overlay Controlplane

Zuletzt wird BGP-EVPN konfiguriert. Hierfür wird eine BGP Instanz
erstellt, in der alle teilnehmenden weiteren Switche als Nachbarn
eingetragen werden müssen. Da durch Nutzung von OSPF eine direkte
Erreichbarkeit alle Nachbarn gegeben ist, kann internal BGP verwendet
werden, was bedeutet das jede teilnehmende BGP-Instanz die identische
AS-Nummer erhält. Abschließend folgt die Konfiguration der EVPN
Adressfamilie auf der BGP-Instanz, die dafür sorgt das entsprechende
Erreichbarkeitsinformationen ausgetauscht werden.

Virtueller Switch: SONiC
------------------------

Als [sos]{acronym-label="sos" acronym-form="singular+short"} für die
Simulation wird eine virtuelle Variante von SONiC eingesetzt, welche per
QEMU virtualisiert wird.

SONiC ist mittels der Container-Technologie Docker modular aufgebaut.
Die einzelnen Komponenten in Form von Containern lassen sich wie folgt
ausgeben:

    $ docker ps

![SONiC Containerarchitektur](media/sonic-docker.png){#fig:sondock
width="100%"}

Durch diese Architektur kann das System durch weitere Module in Form von
Containern erweitert werden. Wie in der Abbildung
[3.7](#fig:sonarch){reference-type="ref" reference="fig:sonarch"}
gezeigt, bildet Mittelpunkt der Architektur eine Redis-Datenbank. Diese
wird unter anderem als zentrale Stelle für Konfigurationen genutzt. Es
gibt mehrere Methoden diese Konfiguration zu modifizieren.

-   Direkte Manipulation mittels REDIS-CLI oder ähnlichen Tools

-   Laden von Konfigurationsartefakten aus YAML-Dateien mittels config
    load \*.yaml

-   Click-CLI - Eine Python-basierte CLI welche eine gewohnte
    CLI-Semantik direkt in der Linux-Shell verfügbar macht

-   SONIC-CLI - Ein Management-Framework welches an die Semantik eines
    DELL-OS 10 angelehnt ist

-   Standardisierte Konfigurationsschnittstellen wie gNMI oder Restconf

Die REDIS-Datenbank lädt ihren Inhalt bei Initialisierung nach
Systemstart aus der Datei etc/sonic/config\_db.json. Durch die Befehle
config save beziehungsweiße config load lässt sich der Inhalt der
Datenbank in die Datei schreiben beziehungsweise laden.

Ein Sonderfall stellt die Konfiguration des eingesetzten
Routingframeworks FRR dar. SONiC hat dafür drei konfigurierbare Modi
implementiert.

-   **sonic-bgpcdfd** - Dieser Modus ist aktueller Standard, welcher
    ohne einen entsprechenden Eintrag konfiguriert ist. Die
    Konfiguration von FRR wird durch SONiC aus der REDIS-Datenbank
    generiert. Die Datenbank bleibt damit zentrales
    Konfigurationselement. Die Click-CLI hat lediglich wenige Show
    Befehle, kann BGP aber nicht konfigurieren. Die Konfiguration über
    das in der REDIS-Datenbank implementierte YANG-Modell ist wenig
    dokumentiert und muss hauptsächlich durch lesen des Codes
    nachvollzogen werden.

-   **sonic-frrcfgd** - Dieser Konfigurationsdienst funktioniert gleich
    dem älteren bgpcfgd und kann als dessen Nachfolger betrachtet
    werden. Der Dienst setzt teilweise andere Konfigurationssemantiken
    in der REDIS-DB ein. Verbessert soll vor allem die dynamische
    Konfigurationsänderung zur Laufzeit sein.

-   **Split-Mode** - In diesem Modus wird frr nicht von SONiC
    konfiguriert. FRR kann nun über die vtysh Shell konfiguriert werden.
    Diese Konfiguration wird in eigenen Strukturen gespeichert und
    bleibt Persistent. Der Hersteller Edge-Core nutzt in seiner
    Enterprise-Distribution diesen Modus und dokumentiert diesen in den
    eigenen Dokumenten.

Die REDIS-DB wird außerdem als Schnittstelle zwischen den einzelnen
Prozessen genutzt und bildet zentrales Element des
Switch-Abstraction-Interfaces. Diese ist in Form einer Datenbank-Tabelle
realisiert, in welche durch die Controlplane innerhalb der SAI
definierte Schlüssel eingetragen werden. Diese Tabelle wird durch ein
Plattform-spezifischen Prozess ausgelesen und die darunter liegende
Hardware entsprechend programmiert. Im Beispiel des virtuellen SONiCS
heißt der Container des containerisierten Prozesses syncd-vs, bei einer
Broadcom Plattform heißt dieser syncd-brcm.

Im folgenden wird der Inhalt und die Struktur der ASIC DB erläutert.
Dafür werden mittels der REDIS-CLI, ein Kommandozeilentool für
REDIS-Datenbanken, verschiedene Schlüssel aus der Datenbank ausgelesen.
Als Datentyp werden allgemein Hashes eingesetzt, welche pro Schlüssel
mehrere untergeordnete Schlüssel-Werte Paare erlauben. Diese lassen sich
mittels dem Befehl hgetall anzeigen.

``` {caption="ASIC-DB - Physical Port"}
127.0.0.1:6379[1]> hgetall "ASIC_STATE:SAI_OBJECT_TYPE_PORT:oid:0x1000000000002"
 1) "NULL"
 2) "NULL"
 3) "SAI_PORT_ATTR_ADMIN_STATE"
 4) "true"
 5) "SAI_PORT_ATTR_SPEED"
 6) "40000"
 7) "SAI_PORT_ATTR_MTU"
 8) "9122"
 9) "SAI_PORT_ATTR_PORT_VLAN_ID"
10) "20"
```

Jeder physikalische Port hat eine eigene ID. Folgende Informationen
werden hier abgelegt:

-   **Admin State** - Administrativer Status des Interfaces

-   **Speed** - Interface-Geschwindigkeit in Mbit/s

-   **MTU** - Maximale größe eines Ethernet Frames - dieser Wer
    entspricht einem Jumbo-Frame

-   **VLAN-ID** - Dem Interface zugeordnetem PVID

``` {caption="ASIC-DB - Bridge Port"}
127.0.0.1:6379[1]> hgetall "ASIC_STATE:SAI_OBJECT_TYPE_BRIDGE_PORT:oid:0x3a000000000b6b"
1) "SAI_BRIDGE_PORT_ATTR_TYPE"
2) "SAI_BRIDGE_PORT_TYPE_PORT"
3) "SAI_BRIDGE_PORT_ATTR_PORT_ID"
4) "oid:0x1000000000002"
5) "SAI_BRIDGE_PORT_ATTR_ADMIN_STATE"
6) "true"
7) "SAI_BRIDGE_PORT_ATTR_FDB_LEARNING_MODE"
8) "SAI_BRIDGE_PORT_FDB_LEARNING_MODE_HW"
```

Interfaces die eine Bridge zugeordnet werden und damit Ethernet-Frames
weiterleiten bekommen weiterhin eine Bridge-Port-ID zugeordnet.

``` {caption="ASIC-DB FDB Eintrag"}
127.0.0.1:6379[1]> hgetall "ASIC_STATE:SAI_OBJECT_TYPE_FDB_ENTRY:{\"bvid\":\"oid:0x26000000000b6a\",\"mac\":\"F2:DB:FB:66:CC:B2\",\"switch_id\":\"oid:0x21000000000000\"}"
1) "SAI_FDB_ENTRY_ATTR_TYPE"
2) "SAI_FDB_ENTRY_TYPE_DYNAMIC"
3) "SAI_FDB_ENTRY_ATTR_BRIDGE_PORT_ID"
4) "oid:0x3a000000000b6b"
```

Die vorig genannte Bridge-Port-ID wird unter anderem für
[fdb]{acronym-label="fdb" acronym-form="singular+short"}-Einträge
verwendet, in dem damit das Interface spezifiziert wird auf dem eine
MAC-Adresse gelernt wurde. Durch die bvid wird der Eintrag einem VLAN
zugeordnet.

``` {caption="ASIC-DB VLAN"}
127.0.0.1:6379[1]> hgetall "ASIC_STATE:SAI_OBJECT_TYPE_VLAN:oid:0x26000000000b6a"
1) "SAI_VLAN_ATTR_VLAN_ID"
2) "20"
```

Jedes VLAN erhällt einen eigenen Eintrag, in dem einer bvid eine VLAN-ID
zugeordnet wird.

``` {caption="ASIC-DB VLAN-Member"}
127.0.0.1:6379[1]> hgetall "ASIC_STATE:SAI_OBJECT_TYPE_VLAN_MEMBER:oid:0x27000000000b6c"
1) "SAI_VLAN_MEMBER_ATTR_VLAN_ID"
2) "oid:0x26000000000b6a"
3) "SAI_VLAN_MEMBER_ATTR_BRIDGE_PORT_ID"
4) "oid:0x3a000000000b6b"
5) "SAI_VLAN_MEMBER_ATTR_VLAN_TAGGING_MODE"
6) "SAI_VLAN_TAGGING_MODE_UNTAGGED"
```

Jede Mitgliedschaft eines Interface zu einem VLAN wird durch einen
eigenen Schlüssel repräsentiert., in welchem VLAN-ID, PORT-ID sowie der
Tagging-Mode spezifiziert wird.

``` {caption="ASIC-DB Trap"}
127.0.0.1:6379[1]> hgetall "ASIC_STATE:SAI_OBJECT_TYPE_HOSTIF_TRAP:oid:0x22000000000b75"
1) "SAI_HOSTIF_TRAP_ATTR_TRAP_TYPE"
2) "SAI_HOSTIF_TRAP_TYPE_BGP"
3) "SAI_HOSTIF_TRAP_ATTR_TRAP_GROUP"
4) "oid:0x11000000000b73"
5) "SAI_HOSTIF_TRAP_ATTR_PACKET_ACTION"
6) "SAI_PACKET_ACTION_TRAP"
7) "SAI_HOSTIF_TRAP_ATTR_TRAP_PRIORITY"
8) "4"
```

Durch Traps werden der [dp]{acronym-label="dp"
acronym-form="singular+short"} mitgeteilt, welche Pakete an die
[cp]{acronym-label="cp" acronym-form="singular+short"} beziehungsweise
der CPU weitergeleitet werden sollen. In diesem Fall werden Pakete die
Teil des Routingprotokoll [bgp]{acronym-label="bgp"
acronym-form="singular+short"} sind an die CPU und damit an den
Routingprozess weitergeleitet.

SONiC implementiert vergleichsweise viele Layer-2 Funktionen in ihrer
virtuellen Variante von SONiC mittels einem speziellen Version von
syncd.

Simulation
----------

Zur Simulation wurde ein GNS3-Server-Manager Template mit dem Namen
BGP-EVPN-Lab vorbereitet. In diesem sind die als Appliances SONiC, ein
Versuchs-PC Netlab sowie ein Management-PC vorbereitet. Der Versuchs-PC
wird an das BGP-EVPN Netzwerk angeschlossen um die Konnektiviät durch
das Netzwerk zu testen. Der Management-PC wird zur zentralen
Konfiguration der SONiC-Komponenten genutzt. Zu diesem Zweck wurde ein
kleines interaktives und CLI-basiertes Python-Programm beschrieben
welches a) Konfiguration von den SONiC-Switchen laden sowie aufspielen
kann, b) die notwendige Grundkonfiguration sowie
[uni]{acronym-label="uni" acronym-form="singular+short"}-Konfigurationen
generieren und c) diverse Show-Befehle auf allen Switchen ausführen
kann.

### SONiC {#sonic}

Verwendete Scripte und Dateien liegen im Hochschulrepository:\
<https://github.com/nlab4hsrm/gns3-Server-Manager/tree/main/custom-appliances/sonic/>

Fertige Builds für verschiedene Softwarestände werden auf der Webseite
<https://sonic.software/> zum Download angeboten.

Nach Download eines aktuellen SONIC-VS Images kann mittels dem Script
sonic-gns3a.sh eine entsprechende GNS3-Appliance Datei für den Upload in
GNS3 erstellt werden. Das Script basiert auf einer Vorlage aus dem
originalen SONiC-Repository. Angepasst wurden der zugewiesene
Arbeitsspeicher sowie die Anzahl der virtuellen CPUs. Die im original
spezifizierten 2 Gigabyte haben sich in Versuchen als zu wenig erwiesen
und haben für Prozessabstürze gesorgt.

Das Script wird wie folgt aufgerufen:

    $ ./sonic-gns3a.sh -f <image-filename>

### NLAB Management Controller

Verwendete Scripte und Dateien liegen im Hochschulrepository:\
<https://github.com/nlab4hsrm/gns3-Server-Manager/tree/main/custom-appliances/bgp-evpn-management/>

Durch ein abgelegtes Dockerfile kann der Management-Container mittels
dem Docker Builder erstellt werden. Der Aufruf dafür sieht wie folgt
aus:

    $ docker build . -t nlab4hsrm/netlab-mgmt:<tag>

Es wird ein Ubuntu Basis Image genutzt, Python mit verschiedenen
Bibliotheken installiert sowie die im Repository abgelegten Scripte und
Konfigurationsdateien in den Container kopiert. Nach dem Image in das
Docker-Repository der Hochschule gepusht wurde, kann es in GNS3 als
Appliance konfiguriert und genutzt werden.

Die Scripte und Konfigurationen für diesen Versuch liegen unter

    /BGP_EVPN_LAB

Die Dateihierarchie sieht wie folgt aus:

    |-- evpn
    |   |-- generate_l3.py
    |   |-- generate.py
    |   |-- sonictoolset.py
    |-- hosts
    |-- run-cli.py
    |-- topology.csv

In der **hosts** Datei werden die Management-IP-Adressen der SONiC
Switche eingetragen. In der **topology.csv** ist die Verbindung der
Switche untereinander definiert, wobei eine Zeile der Tabelle für einen
Link steht und die Switche über ihr letztes IP-Tupel der Management-IP
spezifiziert werden. Gestartet werden kann das Tool mit dem Befehl

    $ ./run-cli.py

![EVPN-CLI Tool](media/evpn-cli.png){#fig:evpncli width="100%"}

Das Tool überträgt führt per SSH Befehle auf den SONiC-Switchen aus und
überträgt per SCP Konfigurationsdateien im JSON Format. Die
Konfigurationen speichert das Tool in lokalen temporären
Python-Dictionarys nachdem diese von den Switchen mittels dem ersten
Befehl geladen wurden. Auf Grundlage dieser initialen
Konfigurationsdatei sowie der Topologie-Beschreibung im CSV Format kann
das Tool jeweils Konfigurationen für BGP-EVPN erstellen und diese
anschließend wieder auf die SONiC-Switche aufspielen. Weiterhin sind
einige Konfigurationstasks wie das Anlagen von VLANs und VXLAN-Mappings
und verschiedene Show-Ausgaben implementiert.

### Topologie

![EVPN-CLI Tool](media/bgp-evpn-top.png){#fig:evpncli width="100%"}

Auch hier wird die in dem Kapitel
[1.1](#fig:reftop){reference-type="ref" reference="fig:reftop"} gezeigte
Topologie angelegt.

### Konfiguration SONiC

#### Grundlegende Einrichtung

Nachdem die SONiC-Switche gestartet sind, kann man per GNS3 ein
Telnet-Terminal zu den einzelnen Switchen starten und sich mit
[admin/YourPaSsWoRd]{.smallcaps} in dem Betriebsystem anmelden. Im
ersten Schritt wird die Management-IP-Adresse konfiguriert, was mit
Linux-Boardmitteln möglich ist:

    $ sudo ip addr add 172.30.240.41/16 dev eth0

Es wird eine IP-Adresse innerhalb des Subnetzes der GNS3-Umgebung der
Hochschule verwendet. Damit lässt sich später der Switch auch von
außerhalb erreichbar machen.

Die weiteren notwendigen Konfigurationen können mittels dem CLI-Tool aus
dem Management Container durchgeführt werden. Dafür müssen die soeben
gesetzten Management IP-Adressen in der **hosts**-Datei eingetragen
werden, was im hier gezeigten Beispiel wie folgt aussieht:

``` {caption="Hosts-Konfiguration im EVPN-CLI Tool"}
172.30.240.41
172.30.240.42
172.30.240.43
172.30.240.44
172.30.240.45
```

Zusätzlich muss die aufgebaute Topologie in der **topology.csv**
hinterlegt werden.

``` {caption="Topologie-Konfiguration im EVPN-CLI Tool"}
,peer1,peer2
0,41,44
1,41,43
2,43,44
3,43,45
4,42,44
5,42,45
```

Jede virtuelle Kabelverbindung ist durch eine Zeile repräsentiert und
wird durch jeweils zwei Geräte definiert, welche selbst durch ihr
letztes Tupel der Management-Adresse identifiziert werden. Die
Reihenfolge der Einträge ist dahingehende Entscheidend, das für das
erste vorkommen eines Switches das erste Interface genutzt wird, für das
zweite Vorkommen das zweite Interface, weiter Vorkommen der Logik
entsprechend.

Befor der Management-Container genutzt werden kann, muss auch diesem
eine IP-Adressen zugewiesen werden. Da es sich um einen Docker-Container
handelt, funktioniert dies am leichtesten über den Menüpunkt Edit
configim GNS3-Kontextmenü. Im Anschluss kann dieser gestartet werden und
mittels Ping die Erreichbarkeit der Management-Interfaces der
SONiC-Switche überprüft werden. Dies ist Voraussetzung für die weiteren
Schritte.

Klappt der Ping, funktionieren die weiteren Schritte wie folgt:

-   Option **\[0\]** - Herunterladen der aktuellen Konfigurationen von
    den Switchen. Hier sind Informationen enthalten, die für die
    Generierung neuer Konfigurationen notwendig sind. Sobald dies
    abgeschlossen ist, sollte unter Loaded configs fünfmal der Begriff
    sonic auftauchen.

-   Option **\[6\]** - Dadurch werden die geladenen Konfigurationen
    durch neu generierte Konfigurationen gesetzt. Darin enthalten sind
    Konfigurationen für die Transfer-Links, das OSPF-Routing, die VXLAN
    Virtualisierung sowie BGP-EVPN.

-   Option **\[5\]** - Hierdurch werden die soeben generierten
    Konfigurationen auf die Switche übertragen sowie entsprechende
    Dienste auf den Switchen neu gestartet.

#### Erläuterung Konfiguration

Die erstellte und hochgeladene Konfiguration lässt sich unter Option 1
im EVPN-CLI Tool oder direkt auf dem Switch betrachten. Die
Konfigurationen liegen auf dem Switch im JSON Format ab. Ein hilfreiches
Werkzeug um diese zu betrachten und zu modifizieren ist das Linux-Tool
jq, welches im weiteren verwendet wird.

Um die Konfiguration zu betrachten wird eine SSH-Session auf dem 41-er
SONiC Switch gestartet. Mit folgenden Befehl werden die einzelnen
Konfigurationselemente aus der JSON Datei ausgegeben:

    admin@SONiC-42:~$ cat /etc/sonic/config_db.json | jq 'keys'
    [
      "AUTO_TECHSUPPORT",
      "AUTO_TECHSUPPORT_FEATURE",
      "BGP_DEVICE_GLOBAL",
      "BGP_GLOBALS",
      "BGP_GLOBALS_AF",
      "BGP_NEIGHBOR",
      "CRM",
      "DEVICE_METADATA",
      "FEATURE",
      "FLEX_COUNTER_TABLE",
      "INTERFACE",
      "KDUMP",
      "LOGGER",
      "LOOPBACK",
      "LOOPBACK_INTERFACE",
      "MGMT_INTERFACE",
      "NTP",
      "OSPFV2_ROUTER",
      "OSPFV2_ROUTER_AREA",
      "OSPFV2_ROUTER_AREA_NETWORK",
      "PASSW_HARDENING",
      "PORT",
      "SNMP",
      "SNMP_COMMUNITY",
      "SYSLOG_CONFIG",
      "SYSLOG_CONFIG_FEATURE",
      "SYSTEM_DEFAULTS",
      "VERSIONS",
      "VXLAN_EVPN_NVO",
      "VXLAN_TUNNEL"
    ]

Relevante Konfigurationselement sind alle mit BGP,INTERFACE, OSPFV2
sowie VXLAN. Diese werden der Reihenfolge nach Erläutert.

``` {caption="SONiC-Konfig: BGP\\_GLOBALS"}
admin@SONiC-42:~$ cat /etc/sonic/config_db.json | jq '.BGP_GLOBALS'
{
  "default": {
    "local\_asn": "64020"
  }
}
```

In dieser Sektion wird die AS-Nummer für die BGP Session festgelegt.

``` {caption="SONiC-Konfig: BGP\\_GLOBALS\\_AF"}
admin@SONiC-42:~$ cat /etc/sonic/config_db.json | jq '.BGP_GLOBALS_AF'
{
  "default|l2vpn\_evpn": {
    "advertise-all-vni": "true"
  }
}
```

In dieser Sektion wird für die Adress-Familie l2vpn\_evpn festgelegt,
dass alle lokal erstellen VTEPs per BGP an die Nachbarn propagiert
werden sollen.

``` {caption="SONiC-Konfig: BGP\\_NEIGHBOR"}
admin@SONiC-42:~$ cat /etc/sonic/config\_db.json | jq '.BGP_NEIGHBOR'
{
  "default|10.0.3.41": {
    "admin\_status": "true",
    "local\_addr": "10.0.3.42",
    "name": "SONiC41",
    "peer\_type": "internal"
  },
  "default|10.0.3.43": {
    "admin\_status": "true",
    "local\_addr": "10.0.3.42",
    "name": "SONiC43",
    "peer\_type": "internal"
  },
  "default|10.0.3.44": {
    "admin_status": "true",
    "local_addr": "10.0.3.42",
    "name": "SONiC44",
    "peer_type": "internal"
  },
  "default|10.0.3.45": {
    "admin_status": "true",
    "local_addr": "10.0.3.42",
    "name": "SONiC45",
    "peer_type": "internal"
  }
}
```

Jeder BGP-Nachbarschaft muss explizit durch einen eigenen Eintrag
konfiguriert werden. Als lokale Adresse wird die dafür angelegte
Loopback-Adresse verwendet. Wird diese nicht spezifiziert wird die
IP-Adresse des jeweiligen ausgehenden Interfaces genutzt, wodurch eine
Nachbarschaft nicht erfolgreich aufgebaut werden kann. Durch setzen des
peer\_types auf internal, wird iBGP verwendet. Dies setzt identisch
konfigurierte AS-Nummern bei allen BGP-Nachbarn voraus.

``` {caption="SONiC-Konfig: INTERFACES"}
admin@SONiC-42:~$ cat /etc/sonic/config_db.json | jq '.INTERFACE'
{
  "Ethernet0": {},
  "Ethernet0|192.168.5.17/30": {},
  "Ethernet4": {},
  "Ethernet4|192.168.5.21/30": {}
}
```

IP-Adressen auf Interfaces werden durch Schlüssel in dieser Sektion
konfiguriert. Diese IP-Adressen liegen in kleinen 30er Netzen und dienen
als Transfernetzwerke zwischen den Switchen. Eine Überschneidung der
Subnetze mit Nutzdaten ist unproblematisch, da diese in eigenen VRFs
geroutet werden.

``` {caption="SONiC-Konfig: LOOPBACK\\_INTERFACES"}
admin@SONiC-42:~$ cat /etc/sonic/config_db.json | jq '.LOOPBACK_INTERFACE'
{
  "Loopback0": {},
  "Loopback0|10.0.3.42/32": {}
}
```

Loopback-Interface haben die technische Besonderheit gegenüber normalen
Interfaces, dass sie jederzeit aktiv sind. Bei vielen Netzwerkgeräten
werden reguläre IP-Interfaces oft erst aktiv, wenn das VLAN aktiv ist.
Dies wiederum kann einen aktiven Port in dem entsprechenden VLAN
voraussetzen. Das hier konfigurierte Interface wird für die BGP-Session
und für das [vtep]{acronym-label="vtep" acronym-form="singular+short"}
verwendet.

``` {caption="SONiC-Konfig: OSPFV2\\_ROUTER"}
admin@SONiC-42:~$ cat /etc/sonic/config_db.json | jq '.OSPFV2_ROUTER'
{
  "default": {
    "enable": "true",
    "router-id": "10.0.3.42"
  }
}
```

In diesem Segment wird eine OSPF-Instanz aktiviert und eine Router-ID
vergeben. Die Router-ID kann frei gewählt werden. Die ID entsprechend
der verwendeten Loopback-Adresse zu vergeben bietet sich in vielen
Fällen an.

``` {caption="SONiC-Konfig: OSPFV2\\_ROUTER\\_AREA"}
admin@SONiC-42:~$ cat /etc/sonic/config_db.json | jq '.OSPFV2_ROUTER_AREA'
{
  "default|0.0.0.0": {}
}
```

Um OSPF skalierbarer zu machen, kann das Netzwerk in mehrere Areas
eingeteilt werden. Da dies bei der gegeben Größe nicht notwendig ist,
wird lediglich die Standard-Area .0.0 verwendet.

``` {caption="SONiC-Konfig: OSPFV2\\_ROUTER\\_AREA\\_NETWORK"}
admin@SONiC-42:~$ cat /etc/sonic/config_db.json | jq '.OSPFV2_ROUTER_AREA_NETWORK'
{
  "default|0.0.0.0|10.0.3.42/32": {},
  "default|0.0.0.0|192.168.5.17/30": {},
  "default|0.0.0.0|192.168.5.21/30": {}
}
```

Weiterhin müssen der OSPF Instanz die angeschlossenen Netzwerke bekannt
gemacht werden. Eine dedizierte Aktivierung von OSPF auf den
entsprechenden Interfaces ist nicht notwendig. Konfiguriert wird die
Loopback-Adresse, damit diese nach außen propagiert wird, sowie die
beiden direkt angeschlossenen Transfernetzwerke, um hier entsprechend
auf dem Interface eine OSPF-Instanz laufen zu lassen.

``` {caption="SONiC-Konfig: VXLAN\\_TUNNEL"}
admin@SONiC-42:~$ cat /etc/sonic/config_db.json | jq '.VXLAN_TUNNEL'
{
  "vtep": {
    "src_ip": "10.0.3.42"
  }
}
```

Für die Konfiguration von VXLAN wird ein [vtep]{acronym-label="vtep"
acronym-form="singular+short"} für das VXLAN Protokoll angelegt und
diesem ein vorhandenes IP-Interface zugewießen. Verkapselte Pakete
werden von dieser Adresse aus versendet.

``` {caption="SONiC-Konfig: VXLAN\\_EVPN\\_NVO"}
admin@SONiC-42:~$ cat /etc/sonic/config_db.json | jq '.VXLAN_EVPN_NVO'
{
  "nvo-hsrm": {
    "source_vtep": "vtep"
  }
}
```

Das im vorigen Segment erzeugte [vtep]{acronym-label="vtep"
acronym-form="singular+short"} muss abschließend der hier erzeugten
EVPN-Instanz zugeordnet werden. nvo steht hier für network
virtualization overlay. Der Name für dieses Overlay kann frei gewählt
werden, nvo-hsrm hat keine relevante Bedeutung.

### Validierung der Basis-Konfiguration

#### Validierung Underlay-Netzwerk

Zur Validierung des Underlay-Netzwerkes kann das EVPN-CLI Tool verwendet
werden. Diese wird mittels Eingabe von gestartet. Im Anschluss wird von
jedem Switch ein Ping zu jeder benachbarten Transfer-Netz Adresse
versucht, sowie ein Ping zu jeder weiteren Loopback-Adresse im Netzwerk.

#### Validierung BGP-Konfiguration

Sollte alle PING-Tests funktionieren, können die BGP-Sessione überprüft
werden. Dafür wird ein Show-Kommando auf den SONiC-Switchen verwendet.
Das EVPN-CLI Tool bietet die Möglichkeit dieses Show-Kommando auf allen
Switchen auszuführen und anzuzeigen.

![EVPN-CLI Tool: BGP Show Ausgabe](media/show-bgp.png){#fig:evpncli
width="100%"}

Hier sollten bei jedem angezeigten Gerät alle weiteren Nachbarn
auftauchen sowie im Status UPsein.

Weiterhin können die bereits gelernten Routen der BGP-Instanz auf
Vollständigkeit untersucht werden.

    vtysh -c 'show bgp l2vpn evpn'
    BGP table version is 173, local router ID is 192.168.5.5
    Status codes: s suppressed, d damped, h history, * valid, > best, i - internal
    Origin codes: i - IGP, e - EGP, ? - incomplete
    EVPN type-1 prefix: [1]:[EthTag]:[ESI]:[IPlen]:[VTEP-IP]:[Frag-id]
    EVPN type-2 prefix: [2]:[EthTag]:[MAClen]:[MAC]:[IPlen]:[IP]
    EVPN type-3 prefix: [3]:[EthTag]:[IPlen]:[OrigIP]
    EVPN type-4 prefix: [4]:[ESI]:[IPlen]:[OrigIP]
    EVPN type-5 prefix: [5]:[EthTag]:[IPlen]:[IP]

       Network          Next Hop            Metric LocPrf Weight Path
    Route Distinguisher: 192.168.5.5:2
     *> [3]:[0]:[32]:[10.0.3.41]
                        10.0.3.41                          32768 i
                        ET:8 RT:64020:1030
    Route Distinguisher: 192.168.5.13:2
     *>i[3]:[0]:[32]:[10.0.3.43]
                        10.0.3.43                     100      0 i
                        RT:64020:1030 ET:8
    Route Distinguisher: 192.168.5.18:2
     *>i[3]:[0]:[32]:[10.0.3.44]
                        10.0.3.44                     100      0 i
                        RT:64020:1030 ET:8
    Route Distinguisher: 192.168.5.21:2
     *>i[3]:[0]:[32]:[10.0.3.42]
                        10.0.3.42                     100      0 i
                        RT:64020:1030 ET:8
    Route Distinguisher: 192.168.5.22:2
     *>i[3]:[0]:[32]:[10.0.3.45]
                        10.0.3.45                     100      0 i
                        RT:64020:1030 ET:8

Über die Routen Typ 3 werden den BGP-Nachbarn VTEPs bekannt gemacht. In
der Ausgabe lässt sich erkennen, das jeder BGP Nachbar seinen lokalen
[vtep]{acronym-label="vtep" acronym-form="singular+short"} bekannt gibt.
Dies entspricht dem erwarteten Verhalten.

### EVPN Layer-2 Fabric

Nachdem die Grundkonfiguration durchgeführt und getestet wurde können
VLANs für die eigentlichen Nutzer bereitgestellt und getestet werden.
Dafür werden im ersten Schritt auf allen Geräten VLANs angelegt und
anschließend Interfaces diesen zugeordnet. Dies lässt sich interaktiv
mit der EVPN-CLI konfigurieren. Es wird nach Nutzereingaben ein
Konfigurationssegment erzeugt, welches nach Kontrolle und Bestätigung
durch den Anwender auf die SONiC-Switche geladen wird.

Durch Auswahl von Option **\[10\] - Configure User-Interfaces**:

``` {caption="EVPN-CLI: (10) Configure User-Interfaces"}
Interface ID: 12
Access Vlan for Interface [12]: 30
{
   "VLAN": {
      "Vlan30": {
         "members": [
            "Ethernet12"
         ]
      }
   },
   "VLAN_MEMBER": {
      "Vlan30|Ethernet12": {
         "tagging_mode": "untagged"
      }
   },
   "SUPPRESS_VLAN_NEIGH": {
      "Vlan30": {
         "suppress": "on"
      }
   }
}
Write to all devices ?[y/n]
```

Weiterhin muss das soeben erstellte VLAN einem VTEP zugewiesen und einer
VXLAN-ID vergeben werden, auch diese ist über das EVPN-CLI Tool möglich.

``` {caption="EVPN-CLI: (11) Configure VLAN-VXLAN-Mappings"}
11
VLAN ID: 30
VXLAN VNI: 1030
{
   "VXLAN_TUNNEL_MAP": {
      "vtep|map_1030_Vlan30": {
         "vlan": "Vlan30",
         "vni": "1030"
      }
   }
}
Write to all devices ?[y/n]
```

Im Anschluss sollte ein Ping zwischen den beiden NLAB-PCs die am 41er
und 45er SONiC-Switch angeschlossen möglich sein. Die dadurch gelernten
auf VTEPs gelernten entfernetn MAC-Adressen lassen sich für alle Switche
im EVPN-CLI Tool anzeigen:

``` {caption="EVPN-CLI: Auf VTEPs gelernte MAC-Adressen"}
28
# Device: 172.30.240.41
show vxlan remotemac all
+--------+-------------------+--------------+-------+---------+
| VLAN   | MAC               | RemoteVTEP   |   VNI | Type    |
+========+===================+==============+=======+=========+
| Vlan30 | 9a:89:d8:b0:1f:16 | 10.0.3.45    |  1030 | dynamic |
+--------+-------------------+--------------+-------+---------+
Total count : 1


# Device: 172.30.240.42
show vxlan remotemac all
+--------+-------------------+--------------+-------+---------+
| VLAN   | MAC               | RemoteVTEP   |   VNI | Type    |
+========+===================+==============+=======+=========+
| Vlan30 | 9a:89:d8:b0:1f:16 | 10.0.3.45    |  1030 | dynamic |
+--------+-------------------+--------------+-------+---------+
| Vlan30 | ea:55:9d:f7:0f:7d | 10.0.3.41    |  1030 | dynamic |
+--------+-------------------+--------------+-------+---------+
```

Die Ausgabe des 42er Switches zeigt das auch unbeteiligte Hosts, an
denen aber entsprechendes VLAN konfiguriert ist, beide MAC-Adressen
lernen.

``` {caption="EVPN-CLI: BGP EVPN Layer 2 Routen"}
vtysh -c 'show bgp l2vpn evpn'
BGP table version is 2, local router ID is 192.168.5.5
Status codes: s suppressed, d damped, h history, * valid, > best, i - internal
Origin codes: i - IGP, e - EGP, ? - incomplete
EVPN type-1 prefix: [1]:[EthTag]:[ESI]:[IPlen]:[VTEP-IP]:[Frag-id]
EVPN type-2 prefix: [2]:[EthTag]:[MAClen]:[MAC]:[IPlen]:[IP]
EVPN type-3 prefix: [3]:[EthTag]:[IPlen]:[OrigIP]
EVPN type-4 prefix: [4]:[ESI]:[IPlen]:[OrigIP]
EVPN type-5 prefix: [5]:[EthTag]:[IPlen]:[IP]

   Network          Next Hop            Metric LocPrf Weight Path
Route Distinguisher: 192.168.5.5:2
 *> [2]:[0]:[48]:[12:ef:1d:46:00:44]
                    10.0.3.41                          32768 i
                    ET:8 RT:64020:1030
{...}
Route Distinguisher: 192.168.5.22:2
 *>i[2]:[0]:[48]:[06:c8:38:33:39:36]
                    10.0.3.45                     100      0 i
                    RT:64020:1030 ET:8
{...}


Displayed 7 out of 7 total prefixes
```

Die vorig gezeigten Routen Typ-3 wurden aus der Ausgabe entfernt. Die
MAC-Adressen wurden zwischen den BGP-Instanzen über Routen vom Typ 2
bekannt gemacht.

### EVPN Layer-3 Fabric

EVPN kann über die vorig gezeigten Layer-2 Services hinaus ein ein
geroutetes Netzwerk virtualisieren und Erreichbarkeitsinformationen
verteilen. Die Informationen werden in diesem Fall nicht zwischen
[vtep]{acronym-label="vtep" acronym-form="singular+short"}s verteilt,
sondern zwischen [vrf]{acronym-label="vrf"
acronym-form="singular+short"}-Instanzen. Diese können beliebig im
Netzwerk platziert werden, die Daten werden zwischen den VRFs über ein
eigenes Transfer-Netzwerk übertragen welches durch eine eigene VXLAN-VNI
definiert wird. Dafür ist eine Erweiterung der Basiskonfiguration
notwendig. Nachfolgend können mittels eines neuen Routentyps auch
Layer-3 Erreichbarkeitsinformationen für die virtualisierten
Gast-Netzwerke verteilt werden.

``` {caption="SONiC: VRF01 Basic Config"}
13
Transfer VNI/VLAN?:1000
{
   "VRF": {
      "Vrf01": {
         "fallback": "false",
         "vni": "1000"
      }
   },
   "VLAN": {
      "Vlan1000": {}
   },
   "VLAN_INTERFACE": {
      "Vlan1000": {
         "vrf_name": "Vrf01"
      }
   },
   "VXLAN_TUNNEL_MAP": {
      "vtep|map_1000_Vlan1000": {
         "vlan": "Vlan1000",
         "vni": "1000"
      }
   },
   "BGP_GLOBALS": {
      "Vrf01": {
         "local_asn": "64020"
      }
   },
   "BGP_GLOBALS_AF": {
      "Vrf01|l2vpn_evpn": {
         "dad-enabled": "true"
      },
      "Vrf01|ipv4_unicast": {
         "max_ebgp_paths": "1",
         "max_ibgp_paths": "1",
         "route_flap_dampen": "false"
      }
   },
   "BGP_GLOBALS_ROUTE_ADVERTISE": {
      "Vrf01|L2VPN_EVPN|IPV4_UNICAST": {}
   },
   "ROUTE_REDISTRIBUTE": {
      "Vrf01|connected|bgp|ipv4": {}
   }
}
```

Folgend werden die Konfigurationssegme im vorherigen Listing erläutert:

-   **Vrf01** - Es wird ein VRF angelegt und diesem eine VNI zugewiesen.

-   **VLAN** - Für ein symmetrisches Routing über ein dediziertes
    Transfernetzwerk wird ein eigenes VLAN mit entsprechender VXLAN-VNI
    benötigt. Dies muss auf allen Switchen identisch konfiguriert
    werden.

-   **Route Redistribute** - Die lokalen Routen des Switches, die sich
    durch die lokalen Interface ergeben, müssen in die Tabellen der
    BGP-Instanz übetragen werden

-   **Route Advertise** - Die lokalen BGP-Routen werden mittels die
    Konfiguration den benachbarten BGP-Instanzen bekannt gemacht

Im Gegensatz zu der Enterprise Version von DELL, werden in dem aktuellen
Zweig der offenen Variante derzeit noch nicht alle hier gezeigten
Konfigurationsartefakte in entsprechende FRR-Konfigurationen umgesetzt.
Folgende Konfigurationszeilen werden nicht aus der REDIS-Datenbank in
die FRR-Konfiguration übernommen.

    router bgp 65100 vrf Vrf01 
        address-family l2vpn evpn                                          
            advertise ipv4 unicast                                              
            end

Als aktueller Workaround ist die Funktion **\[15\]** im EVPN-CLI Tool
implementiert, welche die Konfiguration auf allen Switchen nachholt. Da
die FRR-Konfigurationen allerdings bei Konfigurationsvorgängen durch den
frrcfgd mittels Jinja2 neu erzeugt und überschrieben werden, bleibt
diese Konfiguration nicht persistent und muss entsprechend gelegentlich
erneut eingefügt werden.

Im Anschluss werden über das EVPN-CLI Tool mehrere VLAN-Interfaces
erstellt werden, zwischen denen geroutet werden können. Es können sowohl
lokale VLANs ohne eingehängte VTEPs, als auch globale VLANs mit
zugeordnetem VXLAN verwendet werden.

``` {caption="EVPN-CLI Tool"}
15
Specify Switch-Host IP Address: 172.30.240.41
Specifiy VLAN ID: 600
Specify CIDR Subnet for Interface: 192.168.60.1/24
{
  "VLAN": {
    "Vlan600": {
      "vlanid": "600"
    }
  },
  "VLAN_INTERFACE": {
    "Vlan600": {
      "vrf_name": "Vrf01"
    }
  }
}
{
  "VLAN_INTERFACE": {
    "Vlan600": {},
    "Vlan600|192.168.60.1/24": {}
  }
}
```

Das Konfigurationselement VLAN\_INTERFACE wird bewusst doppelt in diese
Reihenfolge erzeugt, da das VLAN unbedingt erst an ein VRF gebunden
werden muss, bevor die IP-Adresse konfiguriert wird. Der hier gezeigte
Schritt kann für weitere Netzwerke wiederholt werden.

``` {caption="EVPN-CLI: EVPN Layer-3 Routen"}
# Device: 172.30.240.45
vtysh -c 'show bgp l2vpn evpn'
BGP table version is 1, local router ID is 192.168.5.22
Status codes: s suppressed, d damped, h history, * valid, > best, i - internal
Origin codes: i - IGP, e - EGP, ? - incomplete
EVPN type-1 prefix: [1]:[EthTag]:[ESI]:[IPlen]:[VTEP-IP]:[Frag-id]
EVPN type-2 prefix: [2]:[EthTag]:[MAClen]:[MAC]:[IPlen]:[IP]
EVPN type-3 prefix: [3]:[EthTag]:[IPlen]:[OrigIP]
EVPN type-4 prefix: [4]:[ESI]:[IPlen]:[OrigIP]
EVPN type-5 prefix: [5]:[EthTag]:[IPlen]:[IP]

   Network          Next Hop            Metric LocPrf Weight Path
Route Distinguisher: 192.168.0.1:4
 *>i[5]:[0]:[1]:[128.0.0.0]
                    10.0.3.41                0    100      0 ?
                    RT:64020:1000 ET:8 Rmac:0c:ce:c4:57:00:00
Route Distinguisher: 192.168.1.1:4
 *>i[5]:[0]:[24]:[192.168.1.0]
                    10.0.3.42                0    100      0 ?
                    RT:64020:1000 ET:8 Rmac:0c:81:4c:79:00:00
```

Die Informationen werden über Routen vom Typ 5 ausgetauscht. In der
Ausgabe ist zu erkennen, dass jeweils der Host 41 und 42 ein Netzwerk
propagieren. Im Anschluss sollte ein Ping zwischen allen vier Netlab PCs
möglich sein.

Fazit
-----

In diesem Versuch wurde ein Netzwerk auf Basis von BGP-EVPN mittels der
virtuellen Variante von SONiC implementiert. Durch die Standardisierung
sämtlicher verwendeter Protokolle, einem hohen Implementierungsgrad bei
den verschiedenen Anbietern und der vergleichsweise einfachen
Konfiguration ist der Ansatz derzeit sehr beliebt und verbreitet. Das
Konzept kann manuell durch Konfiguration der einzelnen Devices oder
mittels selbst entwickelter oder eingekauften Konfigurations- und
Managementtools implementiert werden. Die Art und Weiße der
Konfiguration bietet sich für Automatisierungsansätze an da zum Beispiel
Port-Konfigurationen generisch erstellt werden können und keine
Abhängigkeiten im Netzwerk wie die Verfügbarkeit eines VLANs durch ein
Netzwerk hindurch beachtet werden muss. Ein Beispiel für ein kaufbares
Konfigurations- und Managementtool ist Racksnet. Ebenso machen sich
viele Hersteller-eigene Fabric-Lösungen BGP-EVPN zu Nutze. Der zentraler
SDN Aspekt Traffic Engineering kann allerdings nicht ohne weiteres
implementiert werden. Die Pfade des Netzwerkverkehrs werden durch das
verwendete Routingprotokoll bestimmt, welche kein geregeltes Loadsharing
anbieten.

MPLS Segment Routing (mit EVPN?\]
