OpenFlow Lab I - Broadcastbasiertes Forwarding mit FAUCET
=========================================================

Architektur und Technologien {#sec:of1}
----------------------------

In diesem erstem Lab wird die in Abschnitt
[4.1](#sec:ref){reference-type="ref" reference="sec:ref"} gezeigte
Referenztopologie sowie die beschriebenen Netzwerkservices mittels eines
zentralen Controller der als zentralisierte Controlplane agiert
abzubilden. Als Kommunikationsprotokoll zwischen Control- und Dataplane
wird OpenFlow verwendet. In diesem ersten OpenFlow-Lab kommt der
Controller Faucet zum Einsatz. Dieser arbeitet im Gegensatz zu den
meisten anderen OpenFlow-basierten Controllern nicht Pfad-basiert.

![Faucet Netzwerktopologie](media/faucet-top.png){#fig:fauarch
width="100%"}

Es wird die im Abschnitt [4.1](#sec:ref){reference-type="ref"
reference="sec:ref"} gezeigte Topologie umgesetzt. Es werden insgesamt
vier simulierte Endgeräte an das Netzwerk angeschlossen, welche sich in
zwei verschiedenen Subnetzen befinden. Dies erfordert einen Layer-2 und
einen Layer-3 Service, damit alle Endgeräte untereinander kommunizieren
können.

### Faucet

Faucet ist ein quelloffenes Projekt, welches auf dem ebenfalls
quelloffenem Python-Framework für OpenFlow Ryu basiert. Faucet bietet
die Konfiguration von VLANs sowie ein dezentrales Routing. Mit dem
Projekt chewie, welches ebenfalls von Faucet betrieben wird, gibt es
einen integrierten Authentifizierungsdienst, der Endgeräte an einem Port
authentifizieren kann [@chewie]. Faucet bietet ein fertiges Konzept
Metriken in dem Netzwerk zu erheben und über Grafana zu visualisieren.

Faucet bietet die Möglichkeit mehrere Switche zu stacken um das
Verhalten eines einzelnen großen Switches zu simulieren. Primärer Grund
hierin liegt in der möglichen redundanten Vernetzung der Switche
untereinander, sprich einer vermaschten Topologie. Faucet berechnet
ähnlich wie Spanning-Tree einen Baum hin zu einem wählbaren Switch
entlang dessen Broadcasts weitergeleitet werden. Als Root-Bridge wird
der Switch mit der numerisch kleinsten ID gewählt. Damit der Controller
eine Baumstruktur erstellen kann, muss dieser die Topologie des
Netzwerkes kennen. Faucet setzt dafür eine statische Konfiguration der
Topologie voraus. In der Konfigurationsdatei wird neben der Topologie
auch die [uni]{acronym-label="uni" acronym-form="singular+short"}, die
VLANs, das Layer-3 Routing sowie alle weiteren Eigenschaften des
Netzwerkes konfiguriert. Die Konfiguration liegt im YAML-Format ab.

    $ /etc/faucet/faucet.yaml

Diese zentrale Art der Konfiguration erlaubt automatisierte und
dynamische Änderungen an dem Netzwerk an einer zentralen Stelle.

### OpenFlow

[of]{acronym-label="of" acronym-form="singular+short"} ist ein Protokoll
zur Kommunikation zwischen einer [cp]{acronym-label="cp"
acronym-form="singular+short"} und [dp]{acronym-label="dp"
acronym-form="singular+short"} um diese physikalisch und logisch
voneinander trennen zu können. Das Protokoll spezifiziert die
Nachrichten, die zwischen den Einheiten ausgetauscht werden. Durch diese
Nachrichten werden von dem Controller generierte Flow-Regeln auf die
jeweilige Dataplane programmiert. OpenFlow kann vielseitig eingesetzt
werden, so kann mittels des Protokoll die Controlplane eines Netzwerkes
vollständig zentralisiert werden. OpenFlow kann auch dafür genutzt
werden nur bestimme Flows umzuleiten, beispielsweise für die
Realisierung eines Traffic-Engineerings oder zur Durchsetzung von
Regelwerken [@ofs].

![OpenFlow Architektur Quelle: Aria Zhu -
medium.com](media/openflow-medium.png){#fig:evpncli width="80%"}

Auf einem Interface eingehende Pakete werden auf Basis der
implementierten Flow-Regeln weitergeleitet.

Flow-Regeln können auf verschiedene Header eines Ethernet-Pakets greifen
wie MAC-Adresse, IP-Adresse oder ein VLAN Tag. Zusätzlich wird eine
Aktion definiert. Diese Aktion kann das versenden des Ethernet-Paketes
auf einem bestimmten Interface oder das Überschreiben eines weiteren
Headers durch einen neuen Wert sein.

![Openflow Tabellen - Quelle:
fs.com](media/openflow-fs.jpg){#fig:evpncli width="70%"}

Die Regeln können in mehrere untereinander verkette Tabellen geschrieben
werden. Die Tabellen werden mittels eine ID identifiziert. Die Pakete
durchlaufen nicht automatisch alle Tabellen, die Pakete werden den
Tabellen mittels Regeln zugewiesen [@ofs].

Das Protokoll basiert auf einer Menge von definierten Nachrichten,
welche über den normalen TCP/IP Stack übertragen werden:

-   HELLO - Herstellen einer Verbindung.

-   FEATURE REQUEST/ REPLY - Controller fragt damit Informationen vom
    Switch wie OpenFlow Version ab.

-   GET CONFIG REQUEST/ REPLY - Controller fragt Konfigurationen vom
    Switch an

-   PACKET-In - Erhällt ein Switch ein Paket auf das keine Nachricht
    passt, kann er das Paket an den Controller senden.

-   FLOW MOD - Damit sendet der Controller Flow-Regeln an den Switch.

-   BARRIER - Abfrage des Controllers ob alle vorher gesendeten
    Anweisungen umgesetzt worden sind.

OpenFlow ist kein abgeschlossener Standard. Das Protokoll ist unter
stetiger Weiterentwicklung. Seit dem initialen Release mit Version 1.1
im Jahr 2011 ist eine Vielzahl von Versionen erschienen. Aktuell
veröffentlicht ist die version 1.6. Hinzu kam zum Beispiel die
Möglichkeit mehrere Tabellen zu definieren oder die Möglichkeit auf neue
Header zu matchen. Seit Version 1.5.0 ist es zum Beispiel möglich Regeln
auf TCP-Flags anzuwenden. Diese stetige Weiterentwicklung stellt
Netzwerk-Ausrüster vor die Herausforderung, diese Funktionen
kontinuierlich zu implementieren. Teilweise treffen sie hier auf durch
die Hardware gegeben Limitationen, so dass Funktionen modifiziert
implementiert werden oder weggelassen werden.

### Virtueller Switch: OpenvSwitch

Der OpenvSwitch (abgekürzt OvS) ist ein quelloffener Software-Switch.
OpenvSwitch wird in Virtualisierungsumgebungen und Cloud-Umgebungen
verwendet um virtuelle Maschinen an ein Netzwerk anzuschließen. Der
OpenvSwitch verbindert hierbei physikalische Interfaces eines Servers
mit virtuellen Interface von zum Beispiel virtuellen Maschinen. Der
Switch implementiert Layer-2 Funktionen wie VLANs,
[stp]{acronym-label="stp" acronym-form="singular+short"} sowie
komplexere Technologien wie VXLAN.

![OpenvSwitch Architektur - Quelle:
hustcat.github.io](media/ovs_architecture_01.png){width="100%"}

OpenvSwitch nutzt unter Linux ein eigenes Kernel-Modul für die
Weiterleitung von Paketen. Die Weiterleitungsregeln werden durch den
Dienst vswitchd programmiert, der als Controlplane fungiert und im Falle
von OpenFlow die Regeln entsprechend konvertiert und abstrahiert. Die
Netlink Kommunikation erfolgt mittels Flow Keys, welche Regeln zur
Weiterleitung von Paketen definieren [@ovsdp].

![OpenvSwitch Datapath Regeln](media/ovs-dp.png){#fig:ovsdp
width="100%"}

Über den in der Abbildung [5.4](#fig:ovsdp){reference-type="ref"
reference="fig:ovsdp"} gezeigten Befehl lassen sich die in das
Kernel-Modul implementierten Regeln ausgeben. In diesem Fall sind zwei
Hosts an den Switch angebunden, die untereinander Kommunizieren. Es
existiert für jeweils jede Richtung eine Regel, welche auf die Pakete
greift und als entsprechende Aktion an den entsprechenden Port
weiterleitet.

Alternativ kann Data Plane Development Kit, kurz DPDK, als Controlplane
genutzt werden, welches im Linux-Userspace ausgeführt wird und aufgrund
einer anderen Architektur höhere Übertragungsraten als das OpenvSwitch
Kernel-Modul erreicht [@ovsdpdk]. DPDK unterstützt weiterhin die
Auslagerung von Funktionen auf die physikalische Netzwerkkarte um
weitere Performance-Optimierungen zu erreichen. Ein detaillierter
Vergleich zwischen der Performance verschiedener Technologien unter dem
OpenvSwitch findet sich unter [@ovsdpperf].

OpenFlow Regelwerk I - Statisch
-------------------------------

In diesem Abschnitt soll die Funktionsweise der Paketweiterleitung mit
Faucet an Beispielhaften Regeln generisch erläutert werden. Als Beispiel
werden die ausgelesenen Regeln aus dem Switch OpenvSwitch-5 betrachtet.
Zuerst werden die relevanten Regeln nach der Initialisierung von Faucet
betrachtet. Die Regeln sind im mehreren Tabellen kaskadiert. Nachfolgend
steht UNI für User-Network-Interface und NNI für
Network-Network-Interface. Um die weiteren Regeln einordnen zu können
werden folgende Informationen gegeben:

-   **eth1** - Link zu dem Switch 2

-   **eth2** - Link zu dem Switch 3

-   **eth5** - Client-Interface mit VLAN-Tag 100

-   **eth6** - Client-Interface mit VLAN-Tag 200

-   **VLAN 100** - 192.168.0.1/24 / 00:00:00:00:00:11 virtuelle MAC

-   **VLAN 200** - 192.168.1.1/24 / 00:00:00:00:00:22 virtuelle MAC

![Faucet Regeln Initial - Switch 5 Table
1](media/faucet-rule-5-1.png){width="100%"}

-   **Regel 0-1**: Weiterleitung von LLDP-Paketen an den Controller.

-   **Regel 2-3**: Pakete ohne VLAN-Tag werden auf den NNIs zwischen den
    Switchen verworfen.

-   **Regel 5-6**: Eingehende Pakete auf den UNIs werden der
    Konfiguration entsprechend mit VLAN-IDs markiert und an Tabelle 1
    weitergeleitet.

-   **Regel 6-7**: Eingehende Pakete auf den NNIs werden an die Tabelle
    1 weitergeleitet.

Die LLDP Pakete nutzt Faucet um Ausfälle von Network-Network Strecken zu
detektieren. Sobald keine LLDP-Pakete auf einem Interface mehr ankommen,
wird die Baumstruktur neu berechnet damit Broadcasts wieder alle Teile
des Netzwerkes erreichen. Alle Pakete auf die bis hier keine Regel
zugetroffen hat werden verworfen.

![Faucet Regeln Initial - Switch 5 Table
5](media/faucet-rule-5-5.png){width="100%"}

-   **Regel 58+60**: Broadcasts die aus Richtung der Root-Bridge kommen
    werden an alle UNIs weitergeleitet.

-   **Regel 59+61**: Broadcasts von NNIs werden auf allen auf dem
    Baumpfad liegenden NNIs weitergeleitet

-   **Regel 62+63**: Broadcasts von UNIs werden auf allen auf dem
    Baumpfad liegenden NNIs weitergeleitet

In dieser Tabelle wird die Behandlung von Broadcasts ersichtlich.
Broadcasts werden nur an [uni]{acronym-label="uni"
acronym-form="singular+short"}s sowie über Interfaces die Teil eins
durch Faucet berechneten Baumes sind weitergeleitet. Dies verhindert die
Bildung von Schleifen und den daraus resultierenden Broadcast-Storms.

![Faucet Regeln Initial - Switch 1 Table
5](media/faucet-rule-1-5.png){width="100%"}

Im Gegensatz dazu leitet die Root-Bridge, in diesem Fall OpenvSwitch-1
Broadcast-Pakete an alle aktiven Interfaces weiter.

![Faucet Tree-Topologie](media/faucet-root.png){width="60%"}

In der Abbildung ist die in diesem Labor konfigurierte Baumstruktur
dargestellt. Als Root-Bridge nutzt Faucet die Bridge mit der kleinsten
ID. Es ist sinnvoll, diese anders als in diesem Lab zentral in einem
Netzwerk zu positionieren. Die Root-Bridge wurde mit Absicht dezentral
platziert um hieraus entstehend Nachteile hervorzuheben.

OpenFlow Regelwerk II - Dynamisch
---------------------------------

Für die Entstehung von dynamischen Regeln werden zwei Endgeräte an die
UNIs angeschlossen und ein Ping zwischen diesen beiden durchgeführt.

![Wireshark Capture Link: Switch3-eth3 \<-\>
Switch5-eth1](media/faucet-ping-ws.png){width="100%"}

Der Wireshark-Mitschnitt zeigt zwei Besonderheiten dieser
Netzwerkarchitektur. Mit Paket 7 in der Abbildung sieht man die
ARP-Antwort für Host-2 für sein Routed-Gateway. Es ist lediglich die
Antwort und nicht die Anfrage ersichtlich, da die Anfrage vom
eingehenden Switch an den Controller gesendet wurde. Die Antwort
wiederum wird als Broadcast im gesamten Netzwerk ersichtlich. Gleiches
Verhalten zeigt sich bei der ARP-Auflösung des zweiten Endgerätes durch
den Router. Während die Anfrage in diesem Fall durch den Controller
durch das Netzwerk geflutet wird, wird die Antwort des Hosts direkt vom
eingehenden Switch an den Controller gesendet.

Weitere Besonderheit ist der Austausch der Ping-Nachrichten auf direktem
zwischen den Hosts, obwohl ein Routing zwischen den beiden VLANs mit der
ID 100 und 200 stattfindet. Dieses dezentrale Routing wird im folgenden
Erläutert.

![Faucet Regeln Routing - Switch 5 Table
2](media/faucet-rule-5-2-routing.png){width="100%"}

-   **Regel 45**: Pakete aus dem VLAN 100 mit der Zieladresse des Hosts
    im VLAN 200 werden hier geroutet. Zu diesem Zweck wird die
    Quell-Macadresse durch die des virtuellen Router-Interfaces im VLAN
    200 ausgetauscht und die Ziel-Macadresse durch die des jeweiligen
    Zieles ausgetauscht. Anschließend werden die Pakete in Tabelle 4
    weiter behandelt. Das Routing geschieht immer jeweils auf dem Switch
    auf dem das Paket eingeht, wodurch ein dezentrales Routing
    realisiert wird.

![Faucet Regeln Routing - Switch 5 Table
4](media/faucet-rule-5-4-routing.png){width="100%"}

-   **Regel 66**: Das eben geroutete Paket wird durch diese Regel über
    das Interface eth1 an den jeweiligen Switch mit dem zu erreichenden
    Host gesendet.

![Wireshark Capture Link (Detailliert): Switch3-eth3 \<-\>
Switch5-eth1](media/faucet-ping-ws-mac.png){width="100%"}

Eine Betrachtung der MAC-Adressen auf den Paketen verdeutlicht die
soeben erläuterte Mechanik. Die Pakete haben als Quell-Macadressen
jeweils die Adressen der virtuellen Gateways, und als Ziel-Macadresse
bereits die des zu erreichenden Hosts. Das Routing findet also jeweils
auf dem Switch statt, auf dem das Paket eingegangen ist.

Simulation
----------

Für die Simulation kann das vorbereitete Template OpenFlow-Lab auf dem
GNS3-Server-Manager der Hochschule genutzt werden. In diesem sind die
Docker-Container für Faucet und den OpenvSwitch bereits vorbereitet.
Zusätzlich ist bereits ein Projekt erstellt, in dem die
Referenztopologie angelegt ist.

Der **OpenvSwitch** wird als Docker-Container in die
Simulations-Umgebung implementiert. Es wird ein fertiger Container aus
dem öffentlichen Dockerhub Repository verwendet -
gns3/openvswitch:latest. Der OpenvSwitch ist vorgefertigt in dem
GNS3-Markplatz verfügbar.

Für **Faucet** wird ein eigener Container erstellt, der im
Container-Repository der Hochschule abgelegt ist unter nlab4hsrm/faucet.
Die notwendigen Konfigurationen liegen im Container ab. Diese
Konfigurationsdateien und das entsprechende Dockerfile liegen im
Versuchsordner ab.

### Konfiguration OpenvSwitche

Die IP-Adresse für die Verbindung zum Controller kann über Edit Config
im GNS3-Kontextmenü der jeweiligen Switche gesetzt werden. Auf den
OpenvSwitchen muss über das Terminal eine OpenFlow-Bridge erstellt,
konfiguriert sowie Ports zu dieser hinzugefügt werden.

``` {caption="Faucet OpenvSwitch Konfiguration 1"}
# Configure OpenFlow Bridge
ovs-vsctl add-br of
ovs-vsctl set bridge of protocols=OpenFlow13
ovs-vsctl set bridge of fail_mode=secure
ovs-vsctl set bridge of other-config:datapath-id=0000000000000001
ovs-vsctl set-controller of tcp:10.0.0.250:6653
```

Es wird das verwendete Protokoll, OpenFlow in der Version 1.3,
festgelegt. Der fail\_mode=secure sorgt dafür das der OpenvSwitch keine
Pakete weiterleitet, wenn er keine Verbindung zum Controller hat. Die
Datapath-ID identifiziert die einzelnen OpenvSwitch-Instanz eindeutig
gegenüber dem Faucet Controller. Die OpenFlow-Kommunikation wird aktiv
durch den Switch aufgebaut. Dafür wird die IP-Adresse des Controllers an
dieser Stelle konfiguriert.

Im Anschluss werden die genutzten Interfaces von der Standard-Bridge
entfernt und der OpenFlow-Bridge hinzugefügt.

``` {caption="Faucet OpenvSwitch Konfiguration 2"}
ovs-vsctl del-port eth1
ovs-vsctl add-port of eth1
ovs-vsctl set Interface eth1 ofport_request=1
ovs-vsctl del-port eth2
ovs-vsctl add-port of eth2
ovs-vsctl set Interface eth2 ofport_request=2
ovs-vsctl del-port eth3
ovs-vsctl add-port of eth3
ovs-vsctl set Interface eth3 ofport_request=3
ovs-vsctl del-port eth4
ovs-vsctl add-port of eth4
ovs-vsctl set Interface eth4 ofport_request=4
ovs-vsctl del-port eth5
ovs-vsctl add-port of eth5
ovs-vsctl set Interface eth5 ofport_request=5
ovs-vsctl del-port eth6
ovs-vsctl add-port of eth6
ovs-vsctl set Interface eth6 ofport_request=6
ovs-vsctl del-port eth7
ovs-vsctl add-port of eth7
ovs-vsctl set Interface eth7 ofport_request=7
ovs-vsctl del-port eth8
ovs-vsctl add-port of eth8
ovs-vsctl set Interface eth8 ofport_request=8
```

Mittels dem ofport\_request wird den Schnittstellen eine feste
OpenFlow-ID zugewiesen. Wird dieser Befehl nicht gesetzt, kann der
OpenFlow-ID von der Interface-ID abweichen, was prinzipiell nicht
problematisch ist, aber die Komplexität unnötig erhöht.

Die Konfiguration lässt sich wie folgt überprüfen:

``` {caption="Faucet OpenvSwitch Konfiguration überprüfen"}
/ # ovs-vsctl show
{...}
    Bridge of
        Controller "tcp:10.0.0.250:6653"
            is_connected: true
        fail_mode: secure
        Port eth4
            Interface eth4
        Port eth1
            Interface eth1
        Port eth7
            Interface eth7
        Port eth8
            Interface eth8
        Port of
            Interface of
                type: internal
        Port eth3
            Interface eth3
        Port eth2
            Interface eth2
        Port eth6
            Interface eth6
        Port eth5
            Interface eth5
    Bridge br1
        datapath_type: netdev
        Port br1
            Interface br1
                type: internal
```

Es sollte die eben angelegte Bridge mit entsprechenden Eigenschaften und
den zugewiesenen Schnittstellen angezeigt werden. Der is\_connected
Eintrag sollte erscheinen sobald Faucet konfiguriert und gestartet ist.

Das Mapping zwischen den Schnittstellen und der OpenFlow-ID lässt sich
mit folgendem Befehl überprüfen:

    / # ovs-vsctl -- --columns=name,ofport list Interface
    {...}
    name                : eth5
    ofport              : 5
    {...}
    name                : eth2
    ofport              : 2
    {...}

### Konfiguration Faucet

Faucet wird über eine YAML-Konfigurationsdatei im Pfad
/etc/faucet/faucet.yaml Konfiguriert. Im Wurzelverzeichnis von Faucet
liegen bereits die Konfiguration für ein Layer-2 und ein Layer-3
Netzwerk für die entsprechende Topologie ab. Diese können an
entsprechende Stelle kopiert werden mittels

    $ cp /faucet-L2.yaml /etc/faucet/faucet.yaml

Die Konfiguration faucet-L2.yaml implementiert zwei VLANs innerhalb
deren die jeweiligen Hosts kommunizieren können. In der erweiterten
Konfiguration faucet-L3.yaml ist zusätzlich ein Routing zwischen den
beiden VLANs implementiert.

Die Konfiguration faucet-L3-yaml untergliedert sich in die drei
Teilbereiche *vlans*, *routers* und *dps*.

In der Sektion *vlans* werden VLANs spezifiziert.

``` {caption="Faucet: VLAN Konfiguration"}
vlans:
    office:
        vid: 100
        description: "office network"
        faucet_mac: "00:00:00:00:00:11"
        faucet_vips: ["192.168.0.1/24"]
```

Den VLANs wird eine Beschreibung sowie optional eine IP-Adresse
zugeordnet. Die IP-Adresse ist für das Routing notwendig und dient dabei
als Default-GW. Es muss zusätzlich hierfür eine virtuelle MAC-Adresse
konfiguriert wird, welche Faucet nutzt um diese der Router-IP
zuzuordnen.

Für ein Routing zwischen den VLANs müssen Router-Instanzen konfiguriert
werden und die jeweiligen VLANs, zwischen denen geroutet werden soll,
spezifiziert werden.

``` {caption="Faucet: Routing Konfiguration"}
routers:
    router-hosts-servers:
        vlans: [office, server]
```

Unter *dps* werden den Schnittstellen der einzelnen Switche VLANs und
optional Beschreibungen zugeordnet. Weiterhin wird in dieser Sektion das
Stacking konfiguriert und die Topologie definiert.

``` {caption="Faucet: Dataplane Konfiguration"}
dps:
    sw1:
        dp_id: 0x0000000000000001
        hardware: "Open vSwitch"
        stack:
            priority: 1
        interfaces:
            1:
                description: "sw1 isl to sw4"
                stack:
                    dp: sw4
                    port: 1
{...}
            6:
                name: "h3"
                description: "netlab 3"
                native_vlan: server
 {...}
```

Die einzelnen Switche und zugehörigen Schnittstellen werden über ihre
OpenFlow-ID identifiziert. Dem Switch wird eine Priorität im Stack
zugewiesen. Der Switch mit der geringsten Priorität wird Root-Bridge.
Das Interface ist in diesem Beispiel als ein NNI Konfiguriert. Es wird
die jeweils der gegenüberliegende Switch und der dort genutzte Port
angegeben. Interface zeigt die Konfiguration eines UNIs, in diesem
Beispiel wird das VLAN server als VLAN zugeordnet.

### Start des Netzwerkes

Zum Start des Netzwerkes wird nun der Faucet-Dienst gestartet. Dafür
wird in der Konsole für Faucet folgender Befehl abgesetzt um den Prozess
im Hintergrund zu starten:

    $ faucet &

Faucet legt einen Log unter /var/log/faucet/faucet.log ab, der genutzt
werden kann um die erfolgreiche Initialisierung des Netzwerkes zu
überprüfen.

    $ cat /var/log/faucet/faucet.log
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 Stack node sw1 UNHEALTHY (running 0s ago, stack ports [Port 1, Port 2] (100%) not up)
    Mar 12 14:49:17 faucet INFO     Stack root sw1 (previous None)
    Mar 12 14:49:17 faucet INFO     Reconfiguring existing datapath DPID 1 (0x1)
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 no ACL changes
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 no VLAN changes
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 no METERS changes
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 no port changes
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 Stack topology change detected, restarting stack ports
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 Port 1 (sw1 isl to sw4) down
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 Port 2 (sw1 isl to sw3) down
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 Using stacking root flood reflection
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 IPv4 routing is active on VLAN office vid:100 untagged: Port 5 with VIPs ['192.168.0.1/24']
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 IPv4 routing is active on VLAN server vid:200 untagged: Port 6 with VIPs ['192.168.1.1/24']
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 Port 1 (sw1 isl to sw4) up
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 Port 2 (sw1 isl to sw3) up
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 Configuring VLAN server vid:200 untagged: Port 6
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 Configuring VLAN office vid:100 untagged: Port 5
    Mar 12 14:49:17 faucet.valve INFO     DPID 1 (0x1) sw1 warm starting

Faucet sollte für jeden Switch, identifizierbar an der Datapath-ID,
einen ähnlich aussehenden Log produzieren. Ist dies für alle
konfigurierten Switche der Fall, kann die Konnektivität zwischen den
Endgeräten mittels Ping und Iperf3 überprüft werden.

### Hilfreiche Befehle

Die in einem OpenvSwitch programmierten Flow-Regeln können über das
Terminal des jeweiligen Switches mit folgendem Befehl ausgegeben werden:

``` {caption="OpenvSwitch: Flows ausgeben"}
ovs-ofctl -O OpenFlow13 dump-flows br0
```

Die Logs von Faucet lassen sich mit folgendem Befehl anzeigen:

``` {caption="Faucet: Logs anzeigen"}
cat /var/log/faucet/faucet.log
```

Nach Konfigurationsänderungen muss der Dienst von Faucet neu gestartet
werden. Dazu wird im ersten Schritt die Job-ID des Dienstes über
folgenden Befehl gefunden:

    jobs

Anschließend kann unter Angabe der Job-ID der Prozess beendet wird, um
ihn im Anschluss wieder starten zu können.

    kill %<job-id>

Fazit
-----

Faucet ist eine solide OpenFlow-basierte Controller-Lösung, welche ein
Netzwerk mit Layer-2 und Layer-3 Services bereitstellen kann. Faucet
zeigt die Vorteile eines zentral konfigurierbaren Netzwerkes mit dem
Potential zur einfachen Automatisierung, macht sich aber mögliche
Vorteile durch eine zentrale Controlplane nicht zu nutze. Zwar wird
Spanning-Tree ersetzt durch eine eigene Mechanik, Pfade in dem
vermaschten Netzwerk verlaufen aber dennoch entlang einer Baumstruktur
und sind damit nicht in jedem Fall optimal. Faucet bietet keine direkten
Möglichkeiten für Traffic-Engineering.

OpenFlow Lab II - Pfadbasiertes Forwarding mit ONOS
