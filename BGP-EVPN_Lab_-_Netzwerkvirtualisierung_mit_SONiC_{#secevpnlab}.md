BGP-EVPN Lab - Netzwerkvirtualisierung mit SONiC {#sec:evpnlab}
================================================

Architektur und Technologien {#architektur-und-technologien-1}
----------------------------

In diesem Lab wird eine Netzwerkvirtualisierung auf Basis von VXLAN und
BGP-EVPN gezeigt. Es sollen Layer-2 und Layer-3 Services wie in Kapitel
[2.3](#sec:services){reference-type="ref" reference="sec:services"}
beschrieben provisioniert werden können. VXLAN wird dabei als
Enkapsulierungsprotokoll verwendet um Datenpakete über Tunnel durch ein
Transportnetzwerk zu übertragen. Als Controlplane zwischen den VXLAN
Tunnelendpunkten (kurz VTEPs) wird BGP-EVPN eingesetzt. BGP-EVPN nimmt
hierbei mehrere Funktionen war. Es macht die VTEPs untereinander bekannt
um baut damit automatisch alle notwendigen Tunnel auf. Weiterhin werden
Layer-2 Erreichbarkeitsinformationen zwischen den VTEPs signalisiert
damit die Anzahl der Broadcasts reduziert werden. Für die
provisionierung von Layer-3 Services werden ebenfalls lokal verfügbare
IP-Prefixes an die anderen Teilnehmer des Netzwerkes signalisiert.

![BGP-EVPN Architektur](media/vxlan-arch.png){width="100%"}

Die Netzwerkarchitektur erfordert hierfür die Konfiguration dreier
voneinander größtenteils unabhängiger Schichten. Während die Schichten
zwar voneinander unabhängig agieren bauen sie funktional aufeinander auf
und bedingen sich gegenseitig.

### Underlay Netzwerk

Als Underlay-Netzwerk wird ein IP-Netzwerk verwendet. Jeder Switch
erhält eine eindeutige Loopback-Adresse und jedes NNI -
Network-Network-Interface - eine IP-Adresse in einem Transfernetzwerk.
Ziel dieses Netzwerk ist alle Loopback-Adressen untereinander erreichbar
zu machen. Da eine statische Konfiguration von Routen hier komplex wäre
und nicht auf Änderungen im Netwerk reagiert, wird ein Routing-Protokoll
eingesetzt. In diesem Lab wird OSPF verwendet, das Routing-Protokoll ist
beliebig ersetzbar durch andere IGPs - Interior-Gateway-Protocoll - wie
ISIS oder EIGRP.

Die im Overlay-Netzwerk gespannten Tunnel terminieren auf den
Loopback-Adressen im Underlay-Netzwerk. Ein VXLAN-Tunnel hat keine
Kenntnis über die zugrunde liegende Paketweiterleitung. Der VXLAN Tunnel
benötigt lediglich eine per IP erreichbare Gegenstelle. Das
Transport-Netzwerk sollte Jumbo-Frames unterstützen, da durch die
VXLAN-Enkapsulierung ein Overhead entsteht und die Pakete größer als die
normalen 1500-Bytes werden können.

### Overlay Netzwerk

VXLAN ist eine Technologie um Ethernet-Tunnel über ein geroutetes
Layer-3 Netz zu spannen. VXLAN steht dabei für Virtual Extensible LAN
und ist in dem RFC 7348 standardisiert[@vxlan]. VXLAN unterscheidet
zwischen 16 Millionen Netzwerken und erlaubt in großen Umgebungen die
doppelte Nutzung von VLAN-IDs. VXLAN kombiniert die Fähigkeit Layer-2
Tunnel über geroutete Strecken zu ziehen mit der Fähigkeit VLANs doppelt
zu nutzen, um eine ganzheitliche Netzwerkvirtualisierung zu schaffen.
Die ist entscheidender Vorteil von Technologien wie IEEE 802.1ad QinQ
oder GRE, welche nur jeweils eine der beiden Problem lösen.

![VXLAN Header, Quelle:
Researchgate](media/VXLAN-Packet-Encapsulation.png){width="70%"}

VXLAN Pakete werden mittels eines zusätzlichen VXLAN-Headers realisiert.
VXLAN-Pakete werden mittels UDP versendet, um ein doppeltes TCP mit
seinen negativen Effekten durch Slow-Congestion und Retransmission zu
vermeiden.

![VXLAN Beispiel](media/vxlan-basis.png){#fig:vxlan1 width="100%"}

In Abbildung [8.1](#fig:vxlan1){reference-type="ref"
reference="fig:vxlan1"} ist ein Beispiel für einen einfachen
VXLAN-Tunnel gegeben. VXLAN ermöglicht es, einen Layer-2 Netzwerk über
eine geroutete Verbindungsstrecke zu ziehen. Dafür werden auf den beiden
gezeigten Switchen jeweils ein VTEP benötigt, welche die Pakete
verpacken und an den jeweiligen anderen VTEP senden.

Ein Trace auf dem Verbindungsstrecke zwischen den beiden Switchen zeigt
bei einem Ping zwischen den beiden Hosts folgende Pakete:

![VXLAN Paket](media/vxlan-packet.png){#fig:vxlan2 width="100%"}

In der Abbildung [8.2](#fig:vxlan2){reference-type="ref"
reference="fig:vxlan2"} ist der äußere Header des VXLAN-Pakets mit der
markiert. Dieses UDP Paket wird von der Loopback-Adressen des einen
Switches zu dem anderen gesendet. Die VTEPs liegen jeweils auf den
Loopback-Adressen der beiden Switche.

![VXLAN Beispiel 2](media/vxlan-basis2.png){#fig:vxlan3 width="100%"}

Eigentlich relevante Vorteile eines VXLAN-Overlays werden in der
Abbildung [8.3](#fig:vxlan3){reference-type="ref"
reference="fig:vxlan3"} ersichtlich. Physikalisch wird eine
Dreiecks-Topologie genutzt. Für das virtueller Ethernet-Netzwerk verhält
sich diese Topologie allerdings Sternförmig. Es muss zur Vermeidung von
Broadcast-Storms keiner der Verbindungen geblockt werden. Dies wird
dadurch möglich, das ein Switch ein aus einem VXLAN-Tunnel kommendes
Paket niemals wieder in einen VXLAN-Tunnel hinein sendet. Diese Logik
macht es allerdings ebenfalls notwendig VXLAN-Tunnel immer Full meshed
anzulegen. Es muss zwischen jedem VTEP ein Tunnel jedem weiteren VTEP
gespannt werden, wenn ein gemeinsamen Layer-2 Netz anliegt.

Damit die VTEPs die Pakete entsprechend weiterleiten können, haben sie
eigene Tabellen welche MAC-Adressen zu gegenüberliegenden VTEPs
zuordnen. Zum lernen dieser Zuordnungen gibt es mehrere Methoden.

#### Head End Replication

Bei dieser Methode wird [bum]{acronym-label="bum"
acronym-form="singular+short"}-Traffic der von den Hosts ausgeht an alle
eingetragenen Remote-VTEPs über Unicasts weitergeleitet. Der VTEPs
lernen die MAC-Adressen durch die gleichen Broadcast-Mechanischem wie
normale Switche. Jedem VTEP müssen alle anderen VTEPs in dem Netzwerk
statisch bekannt gemacht werde.

#### IP-Multicast

Diese Methode basiert ebenso wie die vorherige auf den bekannten
Broadcast-Mechanismen. Im Unterschied werden die entfernten VTEPs nicht
einzeln eingetragen sondern der [bum]{acronym-label="bum"
acronym-form="singular+short"}-Traffic wird an eine Multicast-Adresse
geschickt die die anderen VTEPs abonnieren.

#### OVSDB Controller

Ein Controller synchronisiert über das OVSDB-Protokoll die
MAC-Adresstabellen zwischen den einzelnen VTEPs. Damit kann der
[bum]{acronym-label="bum" acronym-form="singular+short"}-Traffic
reduziert werden und das Verhalten des Netzwerken beeinflusst werden.

#### BGP-EVPN

BGP-EVPN ist eine Erweiterung des Routing-Protokolls
[bgp]{acronym-label="bgp" acronym-form="singular+short"} und eine
weitere Variante eine Controlplane-Funktionalität für ein
VXLAN-Overlay-Netzwerk zu implementieren. Erreichbarkeitsinformationen
werden zwischen VTEPs über BGP ausgetauscht. EVPN, eine
BGP-Adressfamilie, steht dabei für Ethernet Virtual Private Network.
EVPN ist standardisiert in mehreren RFCs wie in RFC 7209, RFC 7432, RFC
8365 und RFC 8317[@evpn]. EVPN implementiert zusätzlich weitere Features
wie EVPN Multihoming, was es ermöglicht LAGs auf beliebige Endgeräte in
der EVPN-Fabric zu ziehen.

### Overlay Controlplane

Als Controlplane für das Overlay wird BGP-EVPN eingesetzt. Hierfür wird
auf jedem Switch BGP konfiguriert sowie alle anderen Teilnehme des
Netzwerkes eingetragen. Durch das IP-Underlay sind alle weiteren
BGP-Instanzen direkt erreichbar, weswegen iBGP und eine einheitliche
AS-Nummer verwendet werden kann.

Zu den EVPN-Routen, die zwischen den BGP-Instanzen ausgetauscht werden
gehören:

-   **Type 1 - Ethernet Auto-Discovery Route** - Diese Route wird hier
    für EVPN Multihoming eingesetzt. Es wird die Erreichbarkeit einer
    bestimmen MAC-Adresse ausgetauscht für eine Konvergenz bei Ausfall
    eines Links.

-   **Type 2 - MAC/IP Route** - Diese Route wird verwendet um
    Informationen über lokal gelernte MAC-Adressen an die Partner zu
    übertragen. Die IP-Adresse wird übertragen um ARP-Anfragen direkt
    vom eingehenden VTEP beantworten zu können und diese nicht durch das
    Netzwerk fluten zu müssen. Die Adressfamilie wird für Layer-2
    Services verwendet.

-   **Type 3 - Inclusive Multicast Route** - Diese Route wird eingesetzt
    um [vtep]{acronym-label="vtep" acronym-form="singular+short"}s im
    Netzwerk bekannt zu machen um benötigte VXLAN-Tunnel automatisch
    aufbauen zu können.

-   **Type 4 - Ethernet Segment Route** - Notwendig für EVPN Multihoming

-   **Type 5 - IP Prefix Route** - IP Prefixe werden für Layer-3
    Services im Netzwerk benötigt.

[@evpn]

### Virtueller Switch: SONiC

SONiC steht für Software for Open Networking in the Cloud. Ursprünglich
von Microsoft für die Azure Cloud entwickelt steht dieses Projekt nun
unter der Linux Foundation. SONiC hat durch seinen Einsatz in der Azure
Cloud sowie den Enterprise-Versionen von DELL oder Edge-Core eine große
Marktdurchdringung. Die hieraus resultierende Marktmacht ist zuträglich
für eine üppige Liste von kompatibler Hardware, einer der relevantesten
Faktoren für den Erfolg von offenen Betriebssystemen für Switche.

![SONiC Architektur - [@sonarch]](media/sonarch.png){#fig:sonarch
width="100%"}

In Abbildung [8.4](#fig:sonarch){reference-type="ref"
reference="fig:sonarch"} ist die Architektur von SONiC dargestellt.
Relevanter Vorteil gegenüber früherer offener Betriebssysteme ist die
Art und Weise der Integration von Forwarding-Hardware. Während bei
früheren offenen Plattformen wie *Cumulus Linux* die einzelnen ASICs von
oben durch das Betriebssystem integriert wurden, erfordert SAI eine
Integration der Forwarding Hardware von unten durch die jeweiligen
Lieferanten. *Hardware vendors are expected to provide a SAI-friendly
implementation of the SDK required to drive their ASICs.[@saiasic]*. Für
ein breites Angebot SAI-Kompatibler Hardware am Markt ist eine große
Marktdurchdringung dieser offenen Schnittstellung Voraussetzung.
Anderenfalls ist die Integration dieser Schnittstellen für
Hardware-Lieferanten wie Broadcom uninteressant.

SONiC bietet eine virtuelle Variante welche auf einem speziellem
*syncd*-Modul basiert. Dieser Prozess der in der regulären Variante für
die Programmierung der Hardware zuständig ist bildet die Dataplane im
Linux-Netzwerkstack ab. Es werden virtuelle Interfaces im Linux-Kernel
(tun/tap) verwendet. Die Pakete werden durch den *syncd*-Prozess
zwischen den virtuellen und den virtualisierten physikalischen
Front-Ports transferiert. Während im originalen SONiC-Wiki keinen
erläuterten Eintrag zu Implementierten Features listet, benennt Broadcom
zu der von ihnen Angebotenen virtuellen Enterprise-Variante folgende
Features:

    Features Supported with SONiC-VS Image:
        eBGP / iBGP - (underlay and overlay)
        MC-LAG
        OSPF underlay with BGP / EVPN as overlay
        Numbered and un-numbered interfaces
        BGP un-numbered
        Route leaking
        Multi-VRF (Multi-tenants)
        BFD

Die hier gelisteten Funktionen konnten in der offenen virtuellen
SONiC-Variante erfolgreich getestet werden. Nicht implementiert und hier
ebenfalls nicht gelistet sind die EVPN-Features Anycast-Gateways und
Multihoming. Weiterhin schreibt Broadcom: *SONiC-VS image provides users
the ability to verify the control plane functions (for example. BGP,
MC-LAG) on a typical data center switch. The data plane functionality
(for example ACL, QOS, PBR) is not supported by SONiC-VS as it does not
have underlying physical platform.* [@broadcomsonic]. Die hier genannten
nicht verfügbaren Features wurden in diesem Lab nicht verwendet und
wurden daher nicht getestet. Es ist nicht davon auszugehen das die
Features in der offenen virtuellen SONiC-Variante implementiert sind.

SONiC selbst ist auf Basis der Container-Technologie Docker modular
aufgebaut.

    $ docker ps

Über bekannte Docker-Befehle lassen sich die einzelnen Module
betrachten:

![SONiC Containerarchitektur](media/sonic-docker.png){#fig:sondock
width="100%"}

Durch diese Architektur kann das System durch weitere Module erweitert
werden. Wie in der Abbildung [8.4](#fig:sonarch){reference-type="ref"
reference="fig:sonarch"} gezeigt, ist zentraler Bestandteil der
Architektur eine REDIS-Datenbank. Diese wird unter anderem als zentrale
Ablage für Informationen, Konfigurationen und als Message-Broker
genutzt.

Es stehen mehrere Methoden zur Verfügung die in der REDIS-Datenbank
abgelegten Konfiguration zu modifizieren:

-   Direkte Manipulation mittels REDIS-CLI oder anderen
    REDIS-Schnittstellen.

-   Laden von Konfigurationsartefakten aus YAML-Dateien mittels config
    load \*.yaml

-   Click-CLI - Eine Python-basierte CLI welche eine gewohnte
    CLI-Semantik direkt in der Linux-Shell verfügbar macht

-   SONIC-CLI - Ein Management-Framework welches an die Semantik eines
    DELL-OS 10 angelehnt ist

-   Standardisierte Konfigurationsschnittstellen wie gNMI oder Restconf
    auf Basis installierter Agenten

Die REDIS-Datenbank lädt ihren Inhalt bei Initialisierung nach
Systemstart aus der Datei etc/sonic/config\_db.json. Durch die Befehle
config save und config load lässt sich der Inhalt der Datenbank in die
Datei schreiben beziehungsweise laden.

Ein Sonderfall stellt die Konfiguration des eingesetzten
Routingframeworks FRR dar. SONiC hat dafür drei konfigurierbare Modi
implementiert.

-   **sonic-bgpcfgd** - Dieser Modus ist aktueller Standard, welcher
    ohne einen entsprechenden Eintrag konfiguriert ist. Die
    Konfiguration von FRR wird durch SONiC aus der REDIS-Datenbank
    generiert. Die Datenbank bleibt damit zentrales
    Konfigurationselement. Die Click-CLI hat lediglich wenige Show
    Befehle, kann BGP aber nicht konfigurieren. Die Konfiguration über
    das in der REDIS-Datenbank implementierte YANG-Modell ist kaum
    dokumentiert und muss hauptsächlich durch lesen des Codes
    nachvollzogen werden.

-   **sonic-frrcfgd** - Dieser Konfigurationsdienst funktioniert gleich
    dem älteren bgpcfgd und kann als dessen Nachfolger betrachtet
    werden. Zentraler Vorteil ist eine bessere Unterstützung dynamischer
    Konfigurationsänderungen. Bei dem älteren bgpcfgd muss in der Regel
    der Service neu gestartet werden, was für eine Unterbrechung im
    Netzwerk sorgen kann.

-   **Split-Mode** - In diesem Modus wird FRR nicht von SONiC-Diensten
    konfiguriert. FRR wird über die vtysh Shell konfiguriert. Diese
    Konfiguration wird in eigenen Strukturen gespeichert und bleibt
    Persistent. Der Hersteller Edge-Core nutzt in seiner
    Enterprise-Distribution diesen Modus und dokumentiert diesen in den
    eigenen Dokumenten.

Die REDIS-DB wird außerdem als Schnittstelle zwischen den einzelnen
Prozessen genutzt und bildet zentrales Element des
Switch-Abstraction-Interfaces. Diese ist in Form einer Datenbank-Tabelle
realisiert, in welche durch die Controlplane durch die SAI definierte
Schlüssel eingetragen werden. Diese Tabelle wird durch ein
Plattform-spezifischen Prozess ausgelesen und die darunter liegende
Hardware entsprechend programmiert. Im Beispiel des virtuellen SONiC
heißt der Container des containerisierten Prozesses syncd-vs, bei einer
Broadcom Plattform heißt dieser syncd-brcm.

Im folgenden wird der Inhalt und die Struktur der ASIC\_DB erläutert.
Dafür werden über die REDIS-CLI, ein Kommandozeilentool für
REDIS-Datenbanken, verschiedene Schlüssel aus der Datenbank ausgelesen.
Als Datentyp werden allgemein Hashes eingesetzt, welche pro Schlüssel
mehrere untergeordnete Schlüssel Paare erlauben. Der jeweilig notwendige
Befehl wird in den folgenden Listings gegeben.

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

Jede physikalische Schnittstelle - Front-Port - hat eine eigene
eindeutige ID. Folgende Informationen werden hier abgelegt:

-   **Admin State** - Administrativer Status des Interfaces.

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

Interfaces die eine Bridge zugeordnet werden bekommen weiterhin eine
Bridge-Port-ID zugeordnet.

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

Jedes VLAN wird in einem eigenem Eintrag definiert, in dem einer bvid
eine VLAN-ID zugeordnet wird.

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
eigenen Schlüssel repräsentiert, in dem VLAN-ID, PORT-ID sowie der
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

Durch Traps wird der [dp]{acronym-label="dp"
acronym-form="singular+short"} mitgeteilt, welche Pakete an die
[cp]{acronym-label="cp" acronym-form="singular+short"} beziehungsweise
der CPU weitergeleitet werden sollen. In diesem Fall werden Pakete die
Teil des Routing-Protokoll [bgp]{acronym-label="bgp"
acronym-form="singular+short"} sind an die CPU weitergeleitet.

#### Virtuelle Performance {#sec:sonicperf}

SONiC basiert auf der Linux-Distribution Debian. Dem Kernel sind für
jeden Front-Port ein virtualisierter Physical Interface und ein
entsprechendes Virtual Network Interface bekannt. Das physikalische
Interface wird mittels QEMU virtualisiert.

``` {caption="SONiC: Linux Interfaces"}
root@SONiC-41:/home/admin# ip link
{...}
3: eth1: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP> mtu 9122 qdisc fq_codel state UP mode DEFAULT group default qlen 1000
    link/ether 0c:ce:c4:57:00:01 brd ff:ff:ff:ff:ff:ff
{...}
17: Ethernet4: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9100 qdisc mq state UNKNOWN mode DEFAULT group default qlen 1000
    link/ether 0c:ce:c4:57:00:00 brd ff:ff:ff:ff:ff:ff
```

Das Interface *eth1* ist hier das physikalische Interface, das Interface
*Ethernet4* das zugehörige virtuelle Interface. Die virtuellen
Interfaces werden durch den Dienst *syncd* angelegt sowie die Pakete
zwischen diesen Interface jeweilig weitergeleitet.

Das eigentliche Paketweiterleitung zwischen den virtuellen
Schnittstellen basiert auf Linux-Bridges, die entsprechend MAC-Adressen
lernen.

``` {caption="SONiC: Virtuelle Interfaces in Linux VLANs"}
root@SONiC-41:/home/admin# bridge vlan
port              vlan-id
docker0           1 PVID Egress Untagged
Ethernet12        30 PVID Egress Untagged
Ethernet16        40 PVID Egress Untagged
Bridge            30
                  40
                  1000
dummy             1 PVID Egress Untagged
vtep-1000         1000 PVID Egress Untagged
vtep-30           30 PVID Egress Untagged
vtep-40           40 PVID Egress Untagged
```

Die [vtep]{acronym-label="vtep" acronym-form="singular+short"}s werden
als virtuelle Linux-Interfaces angelegt um entsprechend Pakete in den
VLANs anzunehmen beziehungsweise in diesen zu versenden. Auf diesen
virtuellen Interfaces werden die über EVPN signalisierten MAC-Adressen
statisch gelernt.

``` {caption="SONiC: Switchting Performance Iperf3 - GRO on"}
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-9.23   sec  3.35 MBytes  3.04 Mbits/sec  960             sender
[  5]   0.00-9.23   sec  0.00 Bytes  0.00 bits/sec                  receiver
```

Eine einfache Eingangsmessung auf der Plattform der Hochschule mit
Iperf3 zwischen zwei Interfaces auf einem virtuellen SONiC ohne Routing
ergab eine Performance von circa **3Mbit/s**.

    admin@SONiC-41:~$ lspci
    00:00.0 Host bridge: Intel Corporation 440FX - 82441FX PMC [Natoma] (rev 02)
    00:01.0 ISA bridge: Intel Corporation 82371SB PIIX3 ISA [Natoma/Triton II]
    00:01.1 IDE interface: Intel Corporation 82371SB PIIX3 IDE [Natoma/Triton II]
    00:01.3 Bridge: Intel Corporation 82371AB/EB/MB PIIX4 ACPI (rev 03)
    00:02.0 VGA compatible controller: Device 1234:1111 (rev 02)
    00:03.0 Ethernet controller: Intel Corporation 82540EM Gigabit Ethernet Controller 
    00:04.0 Ethernet controller: Intel Corporation 82540EM Gigabit Ethernet Controller 
    00:05.0 Ethernet controller: Intel Corporation 82540EM Gigabit Ethernet Controller
    00:06.0 Ethernet controller: Intel Corporation 82540EM Gigabit Ethernet Controller
    00:07.0 Ethernet controller: Intel Corporation 82540EM Gigabit Ethernet Controller 
    00:08.0 Ethernet controller: Intel Corporation 82540EM Gigabit Ethernet Controller 
    00:09.0 Ethernet controller: Intel Corporation 82540EM Gigabit Ethernet Controller 
    00:0a.0 Ethernet controller: Intel Corporation 82540EM Gigabit Ethernet Controller 
    00:0b.0 Ethernet controller: Intel Corporation 82540EM Gigabit Ethernet Controller 
    00:0c.0 Ethernet controller: Intel Corporation 82540EM Gigabit Ethernet Controller
    00:0d.0 SCSI storage controller: Red Hat, Inc. Virtio block device

In der virtuellen SONiC-Version wird als Netzwerkadapter ein *Intel
82549EM Gigabit Ethernet* Adapter virtualisiert. Dieser ist theoretisch
in der Lage 1 Gbit/s zu übertragen.

Um den Durchsatzes zu optimieren wurde mit *ethtool* die aktivierten
Features auf dem virtuellen Netzwerkadapter ausgelesen:

    admin@SONiC-41:~$ ethtool -k eth4 | grep ' on'
    tx-checksumming: on
            tx-checksum-ip-generic: on
    scatter-gather: on
            tx-scatter-gather: on
    tcp-segmentation-offload: on
            tx-tcp-segmentation: on
    generic-segmentation-offload: on
    generic-receive-offload: on
    rx-vlan-offload: on
    tx-vlan-offload: on [fixed]
    rx-vlan-filter: on [fixed]

Die beiden Features *tcp-segmentation-offload* und
*generic-receive-offload* sind derzeit aktiviert.
*generic-receive-offload* schreibt eingehende Ethernet Pakete eines
Streams in einen Puffer und verpackt diese anschließend in einen
größeren Frame, der an die CPU weitergegeben wird. Dadurch wird eine
Entlastung der CPU durch eine geringe Anzahl von Interrupts durch die
Netzwerkkarte erreicht. Bei Netzwerkkomponenten ist dieses Verhalten
nicht erwünscht, Pakete sollen ohne Veränderung weitergeleitet werden.
Deshalb wird das Feature abgeschaltet.

Nach Abschaltung des Features *generic-receive-offload* erreicht die
Iperf3-Messung ein deutlich besseres Ergebnis:

``` {caption="SONiC: Switching Performance Iperf3 - GRO off"}
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-10.00  sec   258 MBytes   217 Mbits/sec  1302             sender
[  5]   0.00-10.04  sec   255 MBytes   213 Mbits/sec                  receiver
```

Die Abschaltung der Funktion *tcp-segmentation-offload* erbrachte
hingegen keine Messbaren Verbesserungen.

``` {caption="SONiC: CPU Auslastung Switch"}
admin@SONiC-41:~$ top
top - 08:36:22 up  1:37,  1 user,  load average: 2.52, 1.49, 1.23
Tasks: 231 total,   1 running, 226 sleeping,   0 stopped,   4 zombie
%Cpu(s): 13.5 us, 56.2 sy,  0.0 ni,  6.1 id,  0.0 wa,  0.0 hi, 24.2 si,  0.0 st
MiB Mem :   3846.7 total,   1024.9 free,   2021.0 used,   1033.2 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.   1825.7 avail Mem

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
   2547 root      20   0 1354936  28920  13344 S 167.2   0.7   1:48.18 syncd
     21 root      20   0       0      0      0 S   2.0   0.0   0:01.00 ksoftir+
  22075 root      20   0       0      0      0 Z   1.7   0.0   0:00.32 python3
```

Eine Betrachtung der CPU Auslastung des Switches während einer Messung
mit Iperf3 zeigt eine hohe Auslastung der CPU durch den *syncd* Prozess.
In diesem läuft die Funktion die Pakete von dem physikalischem Interface
an das virtuelle Interface zu übertragen. Es wäre prinzipiell möglich
die Leistung des Switches durch die Provisionierung von mehr
Rechenleistung zu steigern. Relevante Erkenntnis ist, dass die
Netzwerkperformance nun maßgeblich durch die bereitstehende
CPU-Performance des GNS3-Servers abhängt. Diese kann je nach Nutzung
durch andere Studenten beziehungsweise Prozesse variieren, was
Performance-Vergleiche auf Grundlage dieser Plattform schwer
nachvollziehbar und kaum aussagekräftig macht.

Simulation
----------

Zur Simulation ist ein GNS3-Server-Manager Template BGP-EVPN-Lab
vorbereitet. In diesem sind die als Appliances SONiC, ein Versuchs-PC
Netlab sowie ein Management-Container vorbereitet. Der Versuchs-PC wird
an das BGP-EVPN Netzwerk angeschlossen um die Konnektivität durch das
Netzwerk zu testen. Der Management-Container wird zur zentralen
Konfiguration der SONiC-Komponenten genutzt. Zu diesem Zweck wurde ein
kleines interaktives CLI-Tool entwickelt welches die Konfiguration von
den SONiC-Switchen vornimmt und diverse Informationen aus den Switchen
ziehen und kompakt darstellen kann.

### Topologie

![EVPN-CLI Tool](media/bgp-evpn-top.png){width="100%"}

Es wird die in dem Kapitel [4.1](#fig:reftop){reference-type="ref"
reference="fig:reftop"} gezeigte Topologie simuliert. Die lilafarbenen
Verbindungen verbinden die Management-Interfaces mit dem Cloud-Knoten
sowie dem Management Controller. Werden für die Management-Interfaces
IP-Adressen im Subnetz des GNS3-Server verwendet, was bei der Plattform
der Hochschule 172.30.0.0/16 entspricht, können die Netzwerkkomponente
über die OpenVPN-Verbindung erreicht werden. Über das Transport-Netzwerk
werden Layer-2 und Layer-3 Gastnetzwerke gespannt. Dafür werden jeweils
zwei Teilnehmer in zwei verschiedenen Subnetzen angeschlossen, um eben
die Services testen zu können.

Der Versuchsordner BGP-EVPN-Network-Virtualization-Lab baut sich dabei
wie folgt auf:

``` {caption="BGP-EVPN Versuchsorder"}
|-- evpn-management-controller
|   |-- BGP_EVPN_LAB
|   |   |-- evpn
{...}
|   |   |-- evpn-cli.py
|   |   |-- files
|   |   |   |-- vtysh-fix.cmd
|   |   |   `-- vtysh-template.cmd
|   |   |-- hosts
|   |   |-- temp.json
|   |   `-- topology.csv
|   `-- Dockerfile
|-- Konfigurationen
|   |-- SONiC-41.json
|   |-- SONiC-42.json
|   |-- SONiC-43.json
|   |-- SONiC-44.json
|   |-- SONiC-45.json
|   |-- vtysh-41.cmd
|   |-- vtysh-42.cmd
|   |-- vtysh-43.cmd
|   |-- vtysh-44.cmd
|   `-- vtysh-45.cmd
`-- sonic-switch
    `-- sonic-gns3a.sh
```

Alle weiter genutzten und generierten Konfigurationen sind in dem Ordner
*Konfigurationen* abgelegt, werden aber für die Versuchsdurchführung
nicht benötigt. Die Konfigurationen werden durch die im weiteren
erläuterte *evpn-cli* im Ordner *evpn-management-controller* generiert.

### SONiC

Verwendete Scripte und Konfigurationen liegen im Versuchsordner ab.
Fertige SONiC-Builds für verschiedene Softwarestände werden auf der
Webseite <https://sonic.software/> zum Download angeboten.

Nach Download eines aktuellen SONIC-VS Images kann mittels dem Script
sonic-gns3a.sh eine entsprechende GNS3-Appliance Datei für den Upload in
GNS3 erstellt werden. Das Script basiert auf einer Vorlage aus dem
originalen SONiC-Repository. Angepasst wurden der zugewiesene
Arbeitsspeicher sowie die Anzahl der virtuellen CPUs. Die im original
spezifizierten 2 Gigabyte haben sich in Versuchen als zu wenig erwiesen
und für Prozessabstürze gesorgt.

Das Script wird wie folgt aufgerufen:

    $ ./sonic-gns3a.sh -f <image-filename>

### NLAB Management Controller

Der Management Container kann über das im Versuchsordner abgelegte
Dockerfile über folgenden Aufruf erzeugt werden:

    $ docker build . -t nlab4hsrm/netlab-mgmt:<tag>

Es wird ein Ubuntu-Image genutzt, Python mit verschiedenen Bibliotheken
installiert sowie die im Repository abgelegten Scripte und
Konfigurationsdateien in den Container kopiert.

Die Dateihierarchie des Lab Ordners BGP\_EVPN\_LAB ist wie folgt
aufgebaut:

    |-- evpn
    |   |-- generate_l3.py
    |   |-- generate.py
    |   |-- sonictoolset.py
    |-- hosts
    |-- run-cli.py
    |-- topology.csv

In der *hosts* Datei werden die Management-IP-Adressen der SONiC Switche
eingetragen. In der *topology.csv* ist die Verbindung der Switche
untereinander definiert, wobei eine Zeile der Tabelle für einen Link
steht und die Switche über ihr letztes IP-Tupel der Management-IP
spezifiziert werden. Gestartet werden kann das Tool mit dem Befehl

    $ ./run-cli.py

![EVPN-CLI Tool](media/evpn-cli.png){#fig:evpncli width="100%"}

Das Tool führt über SSH Befehle auf den SONiC-Switchen aus und überträgt
per SCP Konfigurationsdateien im JSON Format. Die Konfigurationen
speichert das Tool in lokalen temporären Python-Dictionarys. Diese
können initial mit bestehenden Konigurationen aus den Switchen befüllt
werden. Auf Grundlage dieser initialen Konfigurationsdatei sowie der
Topologie-Beschreibung im CSV Format kann das Tool jeweils
Konfigurationen für BGP-EVPN erstellen und diese anschließend wieder auf
die SONiC-Switche aufspielen. Weiterhin sind einige
Konfigurationsvorgänge wie das Anlagen von VLANs und entsprechenden
VXLAN-Mappings als Funktionen implementiert.

### Konfiguration SONiC

#### Grundlegende Einrichtung

Nachdem die SONiC-Switche gestartet sind, kann in der GNS3-GUI ein
Telnet-Terminal zu den einzelnen Switchen gestartet werden und mit den
Zugangsdaten [admin/YourPaSsWoRd]{.smallcaps} sich angemeldet werden. Im
ersten Schritt wird die Management-IP-Adresse konfiguriert, was mit
Linux-Tool iproute2 möglich ist:

    $ sudo ip addr add 172.30.240.41/16 dev eth0

Es wird eine IP-Adresse innerhalb des Subnetzes der GNS3-Umgebung der
Hochschule verwendet. Damit lässt sich später der Switch auch von
außerhalb erreichbar machen.

Im Anschluss kann optional noch *generic-receive-offload* auf allen
Interfaces deaktiviert werden, wie in Kapitel
[8.1.4.1](#sec:sonicperf){reference-type="ref"
reference="sec:sonicperf"} beschrieben, um die Performance zu
verbessern. Die EVPN-CLI bietet eine entsprechende Option um
*generic-receive-offload* später auf allen Interfaces zu deaktivieren.

Im nächsten Schritt werden alle Management-IP Adressen die im vorherigen
Schritt gesetzt worden sind in die *hosts*-Datei eingetragen.

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
zweite Vorkommen das zweite Interface, weitere Vorkommen der Logik
entsprechend.

Bevor die EVPN-CLI genutzt werden kann, muss auch diesem eine
IP-Adressen zugewiesen werden. Da es sich um einen Docker-Container
handelt, funktioniert dies am komfortabelsten über den Menüpunkt Edit
configim GNS3-Kontextmenü. Im Anschluss kann dieser gestartet werden und
mittels Ping die Erreichbarkeit der Management-Interfaces der
SONiC-Switche überprüft werden. Dies ist Voraussetzung für die weiteren
Schritte.

Ist der Ping-Versuch erfolgreich, kann nun das Konfigurationstool im
Management-Container gestartet werden über:

    python3 /BGP_EVPN_LAB/evpn_cli.py

Die grundlegende Konfiguration der SONiC-Switche für BGP-EVPN erfolgt
über folgende Schritte:

-   Option **\[0\]** - Herunterladen der aktuellen Konfigurationen von
    den Switchen. Hier sind Informationen enthalten, die für die
    Generierung neuer Konfigurationen notwendig sind. Sobald dies
    abgeschlossen ist, sollte unter Loaded configs fünfmal der Begriff
    sonic auftauchen.

-   Option **\[6\]** - Dadurch werden die geladenen Konfigurationen
    durch neu generierte Konfigurationen ersetzt. Darin enthalten sind
    Konfigurationen für die Transfer-Links, das OSPF-Routing, die VXLAN
    Virtualisierung sowie BGP-EVPN.

-   Option **\[5\]** - Hierdurch werden die soeben generierten
    Konfigurationen auf die Switche übertragen sowie entsprechende
    Dienste auf den Switchen neu gestartet.

#### Erläuterung Konfiguration

Die erstellte und hochgeladene Konfiguration lässt sich unter Option im
EVPN-CLI Tool oder direkt auf dem Switch betrachten. Die Konfigurationen
liegen auf dem Switch im JSON Format ab. Ein hilfreiches Werkzeug um
diese zu analysieren ist das Linux-Tool jq, welches im weiteren
verwendet wird.

Um die Konfiguration zu betrachten wird eine SSH-Session zu dem 41-er
SONiC Switch gestartet. Mit folgendem Befehl werden die einzelnen
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

Relevante Konfigurationselement die deren Schlüssel BGP, INTERFACE,
OSPFV2 sowie VXLAN enthalten. Diese werden der Reihenfolge nach
Erläutert.

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

In dieser Sektion wird für die Adressfamilie l2vpn\_evpn festgelegt,
dass alle lokalen VTEPs per BGP an die Nachbarn propagiert werden
sollen.

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
peer\_types auf internal wird iBGP verwendet. Dies setzt identisch
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
als Transfernetzwerke auf den NNIs (Network-Network-Interfaces). Eine
Überschneidung der Subnetze mit Nutzdaten ist unproblematisch, da diese
in eigenen VRFs geroutet werden.

``` {caption="SONiC-Konfig: LOOPBACK\\_INTERFACES"}
admin@SONiC-42:~$ cat /etc/sonic/config_db.json | jq '.LOOPBACK_INTERFACE'
{
  "Loopback0": {},
  "Loopback0|10.0.3.42/32": {}
}
```

Loopback-Interface haben die technische Besonderheit gegenüber normalen
Interfaces, dass sie jederzeit aktiv sind. Bei vielen Netzwerkgeräten
werden reguläre IP-Interfaces oft erst aktiv, wenn das jeweilige VLAN
oder das Interface aktiv ist. Dies wiederum kann einen aktiven Port in
dem entsprechenden VLAN voraussetzen. Das hier konfigurierte Interface
wird für die BGP-Session und für das [vtep]{acronym-label="vtep"
acronym-form="singular+short"} verwendet.

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
der verwendeten Loopback-Adresse gilt als gängige Konvention.

``` {caption="SONiC-Konfig: OSPFV2\\_ROUTER\\_AREA"}
admin@SONiC-42:~$ cat /etc/sonic/config_db.json | jq '.OSPFV2_ROUTER_AREA'
{
  "default|0.0.0.0": {}
}
```

Um OSPF skalierbarer zu machen, kann das Netzwerk in mehrere Bereiche -
Areas - unterteilt werden. Da dies bei der gegeben Größe nicht notwendig
ist, wird lediglich die Area .0.0 verwendet.

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
beiden direkt angeschlossenen Transfernetzwerke.

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
diesem ein vorhandenes IP-Interface zugewiesen. Verkapselte Pakete
werden von dieser Adresse aus versendet. Es wird die jeweilige
Loopback-Adresse verwendet.

``` {caption="SONiC-Konfig: VXLAN\\_EVPN\\_NVO"}
admin@SONiC-42:~$ cat /etc/sonic/config_db.json | jq '.VXLAN_EVPN_NVO'
{
  "nvo-hsrm": {
    "source_vtep": "vtep"
  }
}
```

Das im vorherigem Segment erzeugte [vtep]{acronym-label="vtep"
acronym-form="singular+short"} muss abschließend der hier konfigurierten
Netzwerkvirtualisierung zugeordnet werden. nvo steht hier für network
virtualization overlay. Der Name für dieses Overlay kann frei gewählt
werden, nvo-hsrm hat keine relevante Bedeutung.

### Validierung der Basis-Konfiguration

#### Validierung Underlay-Netzwerk

Zur Validierung des Transportnetzwerkes kann das EVPN-CLI Tool verwendet
werden. Der Test wird über Option gestartet. Im Anschluss wird von jedem
Switch ein Ping zu jeder benachbarten IP-Adresse und ein Ping zu jeder
weiteren Loopback-Adresse im Netzwerk versucht.

#### Validierung BGP-Konfiguration

Sollte alle Ping-Tests erfolgreich sein, können die BGP-Instanzen
überprüft werden. Dafür wird ein Show-Kommando auf den SONiC Switchen
ausgeführt. Das EVPN-CLI Tool bietet die Möglichkeit dieses
Show-Kommando auf allen Switchen auszuführen und anzuzeigen.

![EVPN-CLI Tool: BGP Show Ausgabe](media/show-bgp.png){width="100%"}

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

Über die Routen vom Typ-3 werden VTEPs signalisiert. In der Ausgabe
lässt sich erkennen, dass jeder BGP-Nachbar seinen lokalen
[vtep]{acronym-label="vtep" acronym-form="singular+short"} bekannt
gegeben hat. Dies entspricht dem erwarteten Verhalten.

### EVPN Layer-2 Fabric

Nachdem die Grundkonfiguration durchgeführt und getestet wurde können
Layer-2 Services in Form von Gäste-VLANs provisioniert werden. Im ersten
Schritt werden die VLANs auf den jeweiligen Geräten lokal erstellt und
auf UNIs (User-Network-Interfaces) gelegt. Dies lässt sich zentral mit
der EVPN-CLI für alle Switche durchführen. Es wird nach Nutzereingaben
ein Konfigurationssegment erzeugt, welches nach Kontrolle und
Bestätigung durch den Anwender auf die Switche geladen wird.

Durch Auswahl von Option **\[10\] - Configure User-Interfaces** wird der
Prozess gestartet:

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

Im Anschluss muss dem VLAN eine VXLAN-ID zugewiesen werden. Das ist
ebenfalls über die EVPN-CLI möglich.

``` {caption="EVPN-CLI: (11) Configure VLAN-VXLAN-Mappings"}
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
und 45er SONiC-Switch am Interface mit der ID 12 angeschlossen sind
möglich sein. Die dadurch gelernten auf VTEPs gelernten entfernetn
MAC-Adressen lassen sich für alle Switche im EVPN-CLI Tool anzeigen:

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
{...}
```

Die Ausgabe des 42er Switches zeigt, dass auch unbeteiligte Switche an
denen aber das entsprechende VLAN anliegt die beide MAC-Adressen lernen.

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
{...}
 *> [2]:[0]:[48]:[12:ef:1d:46:00:44]
                    10.0.3.41                          32768 i
                    ET:8 RT:64020:1030
{...}
Route Distinguisher: 192.168.5.22:2
{...}
 *>i[2]:[0]:[48]:[06:c8:38:33:39:36]
                    10.0.3.45                     100      0 i
                    RT:64020:1030 ET:8
{...}


Displayed 7 out of 7 total prefixes
```

Die MAC-Adressen wurden zwischen den BGP-Instanzen über Routen vom Typ 2
bekannt gemacht. Diese Routen lassen sich über die auf den Switchen mit
dem Show-Kommando vtysh -c 'show bgp l2vpn evpn' betrachten.

### EVPN Layer-3 Fabric

EVPN kann neben den gezeigten Layer-2 Services auch Layer-3 Services
anbieten. Die Informationen werden in diesem Fall nicht zwischen
[vtep]{acronym-label="vtep" acronym-form="singular+short"}s verteilt,
sondern zwischen [vrf]{acronym-label="vrf"
acronym-form="singular+short"}-Instanzen. Diese Router-Instanzen können
beliebig im Netzwerk platziert werden. Die Daten werden zwischen den
VRFs über ein eigenes Transfer-Netzwerk übertragen, welches durch eine
eigene VXLAN-VNI definiert wird. Dafür ist eine Erweiterung der
Basiskonfiguration notwendig. Für ein verteiltes Routing wären
Anycast-Gateways notwendig, welche im virtuellen SONiC derzeit nicht
unterstützt werden.

Die erweiterte Basis-Konfiguration für Layer-3 Services lassen sich über
die EVPN-CLI mit der Option generieren und laden.

``` {caption="SONiC: VRF01 Basic Config"}
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

Grundlegend wird auf jedem Switch ein virtueller Router angelegt und die
Signalisierung lokaler Prefixe zu den BGP-Nachbarn eingerichtet. Folgend
werden die Konfigurationssegmente aus dem vorherigen Listing erläutert:

-   **Vrf01** - Es wird ein VRF angelegt und diesem eine VNI zugewiesen.

-   **VLAN** - Für ein symmetrisches Routing über ein dediziertes
    Transfernetzwerk wird ein eigenes VLAN mit entsprechender VXLAN-VNI
    benötigt. Dies muss auf allen Switchen identisch konfiguriert
    werden. Das VLAN wird dem VRF zugewiesen.

-   **ROUTE\_REDISTRIBUTE** - Die lokalen Routen des Switches müssen in
    die Tabellen der BGP-Instanz redistributiert werden.

-   **ROUTE\_ADVERTISE** - Die Adressfamilie IPV4\_UNICAST wird für EVPN
    aktiviert.

Im Gegensatz zu der Enterprise Version von DELL, werden in dem aktuellen
Version der offenen Variante derzeit noch nicht alle hier gezeigten
Konfigurationsartefakte in eine entsprechende FRR-Konfigurationen
umgesetzt. Folgende Konfigurationszeilen werden nicht aus der
REDIS-Datenbank in die FRR-Konfiguration übernommen.

    router bgp 65100 vrf Vrf01 
        address-family l2vpn evpn                                          
            advertise ipv4 unicast                                              
            end

Als aktueller Workaround ist die Funktion **\[15\]** im EVPN-CLI Tool
implementiert, welche die Konfiguration auf allen Switchen nachholt. Da
die FRR-Konfigurationen allerdings bei Konfigurationsvorgängen durch den
frrcfgd überschrieben werden bleibt die Konfiguration nicht persistent
und muss entsprechend gelegentlich erneut eingefügt werden.

Im Anschluss können über die EVPN-CLI VLAN-Interfaces erstellt werden,
zwischen denen geroutet wird. Es können sowohl lokale VLANs als auch
globale verfügbare VLANs mit zugeordneter VXLAN-ID geroutet werden.

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
werden muss, bevor die IP-Adresse konfiguriert wird.

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

Die Prefixes der einzelnen VRFs werden über Routen vom Typ 5
ausgetauscht. In der Ausgabe ist zu erkennen, dass jeweils der Host 41
und 42 ein Netzwerk propagieren. Im Anschluss sollte ein Ping zwischen
allen vier Netlab PCs möglich sein.

Fazit
-----

In diesem Versuch wurde eine Netzwerk für die Provisionierung von
Layer-2 und Layer-3 Services mittels Netzwervirtualisierung gezeigt. Als
virtuelle Switch-Plattform kam SONiC zum Einsatz. Durch die
Standardisierung und Verbreitungsgrad verwendeter Protokolle sowie der
vergleichsweise einfachen Konfiguration ist der Ansatz derzeit sehr
beliebt und verbreitet. Die Art und Weiße der Konfiguration bietet sich
für Automatisierungsansätze an da zum Beispiel Port-Konfigurationen
generisch erstellt werden können und keine Abhängigkeiten im Netzwerk
wie die Verfügbarkeit eines VLANs durch ein Netzwerk hindurch beachtet
werden muss. Ein Beispiel für ein kaufbares Konfigurations- und
Managementtool ist Racksnet. Viele Hersteller nutzen BGP-EVPN in ihren
Fabric-Lösungen wie zum Beispiel Aruba Central oder Juniper Apstra.

Netzwerkvirtualisierung ist eine wichtige Komponente für programmierbare
und möglichst autonome Netzwerke, da die Komplexität der Provisionierung
von Netzwerkdiensten in die zugrunde liegende Architektur abgebildet
wird und die tägliche Administration wie die Bereitstellung eines neuen
VLANs an zwei Stellen des Campus trivial wird.

MPLS-SR Lab - Traffic-Engineering
