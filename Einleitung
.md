Einleitung
==========

Die Hochschule Rhein-Main betreibt einen GNS3-Server mit einer
Nutzerverwaltung sowie einer Template-Funktion zur Durchführung von
Praktikas im Netzwerbereich. Es sollen Switching- und Routingplattformen
sowie [sdn]{acronym-label="sdn" acronym-form="singular+short"}
Architekturen gefunden werden, die sich auf dieser Plattform
virtualisieren lassen. Ziel ist es hiermit verschiedene
[sdn]{acronym-label="sdn" acronym-form="singular+short"} Technologien im
Rahmen der Lehre auf der Plattform demonstrieren zu können.

Die erste Aufgabe ist hiermit die Suche nach SDN-Architekturen. Für die
Suche nach entsprechenden Architekturen wird zu Beginn der Begriff SDN
definiert. Der Begriff SDN ist zwar eng an die Technologie OpenFlow
geknüpft, ist aber mehr eine grundlegende Idee Netzwerke zu
implementieren und zu Betreiben. Zu diesem Zwecke wird eine Marktanalyse
durchgeführt um Technologien auszumachen die bei am Markt erhältlichen
Lösungen eingesetzt werden und diese Technologien auf Relevanz und
Implementierungsreife bewerten zu können.

Die zweite Aufgabe besteht darin gefundene Technologien und
Architekturen auf der Plattform der Hochschule zu simulieren. Dafür
müssen virtualisierbare Switchbetriebsysteme gefunden werden die zu
demonstrierende Protokolle und Technologien unterstützen. Nach
Möglichkeit werden quelloffene Lösungen eingesetzt, da bei diesen
gezeigtes Verhalten Anhand des Quellcodes nachvollzogen werden kann.

*Software-deﬁned networking (SDN) is obsolete, \...* - das zumindest
behauptet das Beratungsunternehmen Gartner in Ihrem Hype Cycle for
Enterprise Networking, 2023. Dies mag zwar für einzelne Technologien
stimmen, trifft aber nicht allgemein auf die Idee
[sdn]{acronym-label="sdn" acronym-form="singular+short"} zu. Eine
Differenzierung des Begriffes SDN sowie Gründe für die heutige Relevanz
von [sdn]{acronym-label="sdn" acronym-form="singular+short"} und dessen
Paradigmen wird zu Beginn der Thesis gegeben.[@ghc]

Abschließend wird in einem kurzen jeweiligem Fazit die Vorteile der
Architektur gegenüber einem traditionellem Ansatz sowie der Reifegrad
der Implementation bewertet. SDN Architekturen eignen sich insbesondere
Routing und Switching Funktionsweisen zu verdeutlichen, da eingesetzte
Mechaniken zur Weiterleitung von Daten Anhand der in der Regel
quelloffenen Software beziehungsweise durch Auswertung von einsehbaren
Regeltabellen gut nachvollziehbar sind.

Motivation
----------

Ich arbeite selbst in einem kleinem Unternehmer als Berater und
Architekt für Computer-Netzwerke. Kunden sind in der Regel
mittelständige Unternehmen und Behörden. Nachdem ich im Rahmen der
Master-Vorlesungen Prof. Dr.-Ing. Bernhard Gross in Kontakt mit
[sdn]{acronym-label="sdn" acronym-form="singular+short"} Konzepten auf
Basis von OpenFlow kam, ist mir aufgefallen das diese Technologie mir im
Rahmen meiner Berufstätigkeit noch nicht untergekommen ist. Während
OpenFlow Implementierungen schwinden, etabliert sich Underlay/Overlay
Netzwerke bei vielen Herstellern als gängiges Lösungsdesign.
Gleichzeitig stellt die [onf]{acronym-label="onf"
acronym-form="singular+short"} einen Nachfolger von OpenFlow vor, die
P4Runtime. In dieser Thesis möchte ich den aktuellen SDN-Konzepte für
Campusnetzwerke erörtern und diese auf der GNS3-Plattform des NLABs
simulieren sowie entsprechende Templates dokumentieren und zur Verfügung
stellen.

Tradionelles Netzwerk {#sec:tn}
---------------------

Da im weiteren Verlauf öfter ein Vergleich zu einem traditionellen
Netzwerkgezogen wird, soll an dieser Stelle die Eigenschaften erläutert
werden, die [sdn]{acronym-label="sdn" acronym-form="singular+short"}
besser machen möchte.

Die Aufgabe eines Netzwerkes ist es Endgeräten untereinander
Kommunikation zu ermöglichen. Betrachtet werden Netzwerke deren
Kommunikation auf IP über Ethernet basiert. Ethernet ist eine
Technologie die bereits in den 1970er Jahren von Xerox entwickelt worden
ist. An einem Ethernet-Netzwerk konnten mehrere Teilnehmer angeschlossen
werden. Ähnlich einer Bus-Topologie haben alle Teilnehmer sich das selbe
physikalische Medium geteilt, was eine Kollisionsdetektion in Form von
CSMA/CD notwendig machte. Eine Belastung des Netzwerkes von über 60
Prozent führte zu vielen Kollisionen, so dass das Netzwerk ineffizient
wurde. Als weiteren Entwicklungsschritt wurden Bridges eingeführt,
welche Pakete auf Basis Ihrer MAC-Adresse nur an den dedizierten
Ziel-Host weiterleiten. Diese Bridges sind heute allgemein als Switche
bekannt. Diese segmentieren damit Ethernet-Netzwerke und verringern
Kollisionen durch Dämpfung von Datenverkehr zu Hosts die nicht an den
Daten interessiert sind. IP-Netzwerke werden unterteilt in Subnetze,
definiert durch einen IP-Adressbereich und einer dazugehörigen
Subnetzmaske. Innerhalb eines Subnetzes kommunizieren Hosts über
Ethernet direkt miteinander. Zwischen Subnetzen kommunizieren sie über
Router, welche in mehreren Subnetzen gleichzeitig eine Schnittstelle
besitzen. Der Host schickt sein Paket um einen Host in einem anderen
Subnetz zu erreichen an den Router, der das Paket entsprechend
weiterleitet - oder auch routet. Der Host kennt das Router unter dem
Synonym Default-Gateway.

Die IP-Kommunikation basiert auf dem [arp]{acronym-label="arp"
acronym-form="singular+short"}-Protokoll. Das Protokoll dient dazu, zu
einer IP-Adresse die zugehörige MAC-Adresse aufzulösen. Dazu sendet er
einen Broadcast an alle Teilnehmer des Netzwerkes woraufhin der gesuchte
Host mit seiner MAC-Adresse antwortet. Unter Kenntnis der MAC-Adresse
adressiert er seine Nachricht mit dieser MAC-Adresse und schickt sie in
Richtung des Switches. Der Switch hat eine Tabelle mit MAC-Adressen und
den zugehörigen Schnittstellen und leitet das Paket analog dazu weiter.
Hat er keinen entsprechenden Eintrag schickt er das Paket über alle
Interfaces heraus. Befindet sich ein Host in einem anderen Netzwerk,
entscheidet der Host das Paket nicht direkt, sondern über sein
Default-Gateway zu versenden. Dies ist in der Regel ein Router mit eine
IP-Adresse im selben Subnetz.

Sowohl das ARP-Protokoll als auch die Layer-2 Paketweiterleitung
benötigen Broadcasts, also das fluten (engl. flooding) von Paketen um zu
funktionieren. Genau dieser Mechanismus führt bei traditioneller
Netzwerke in Hinsicht aus Skalierbarkeit und Ausgestaltung der Topologie
zu Einschränkungen.

Um diesen Herausforderungen in Ethernet-Netzwerk zu begegnen wurden
Protokolle wie [stp]{acronym-label="stp" acronym-form="singular+short"}
oder später [spb]{acronym-label="spb" acronym-form="singular+short"}
eingeführt.

Durch die dezentrale Konfiguration haben Protokolle und Mechanismen eine
gewisse Komplexität. Eine Layer-2 Verbindung durch ein Netzwerk hindurch
muss unter Nutzung von VLANs auf jedem Hopim Datenpfad konfiguriert
werden. Zusätzlich ist dieser Datenpfad statisch und reagiert nicht auf
Überlast oder Ausfall von einzelnen Links. Redundante Datenpfade lassen
sich über Layer-3 Verbindungen auf Basis von Routingprotokollen, dem
dynamischen blockieren von Ports mit Spanning-Tree,
[spb]{acronym-label="spb" acronym-form="singular+short"} oder auch
[mlag]{acronym-label="mlag" acronym-form="singular+short"} Konstrukten
herstellen.

Gründe für SDN
--------------

Durch Entkopplung der [cp]{acronym-label="cp"
acronym-form="singular+short"} von der [dp]{acronym-label="dp"
acronym-form="singular+short"} versucht man die vorig genannten
Einschränkungen sowie administrativen Herausforderungen zu begegnen.
Netzwerke sollen programmierbar sein und redundante sowie vermaschte
Topologien ermöglicht werden. Primär geschieht dies durch die
Optimierung von Netzwerkbroadcasts und der geregelten Steuerung von
Datenpfaden. Die Controlplane benötigt dafür einen globalen Blick auf
das Netzwerk, muss die verschiedenen Datenpfade sowie den Ort der
einzelnen Hosts kennen. Die Controlplane eines einzelnen Switches kennt
bei einfachem Layer-2 Switching und Layer-3 Routing in der Regeln nur
den nächsten Hop für das Paket. Sie hat keine Kenntnis über die
Topologie sowie dem genauen Ort eines Ziel-Hosts. Bei
[sdn]{acronym-label="sdn" acronym-form="singular+short"} soll wird eine
abgesetzte [cp]{acronym-label="cp" acronym-form="singular+short"}
implementiert die das Verhalten des Netzwerk im gesamtem kennt und
entsprechend programmieren kann.

Der Begriff SDN
---------------

In diesem Kapitel wird eine Differenzierung des Begriffes
Software-Defined-Networking versucht.

Der Begriff [sdn]{acronym-label="sdn" acronym-form="singular+short"}
wird oft als Marketingbegriff eingesetzt. Der Begriff kam in
Zusammenhang mit Entwicklungen der Stanford Universität auf, die mit
Hilfe von [of]{acronym-label="of" acronym-form="singular+short"} die
[dp]{acronym-label="dp" acronym-form="singular+short"} eines Switches
programmieren konnten. Damit ließen sich Controller-basierte
Netzwerkkonzepte realisieren. Allgemeiner betrachtet wird die
Bezeichnung Software-Definedfür Geräte verwendet, deren Funktionen und
deren Funktionsweise programmiert und damit per Software definiert
werden kann. Ein Beispiel sind Software-Defined-Radios. Diese Geräten
verfügen über eine Antenne welche in verschiedenen Frequenzen Signale
modulieren können. Über eine entsprechende Software lassen sich diese
Geräte dann zum Beispiel für Bluetooth, WLAN oder Zigbee einsetzen. Die
eigentliche Funktion der Geräte ist also durch Software definiert. Oft
verschwimmt der Begriff auch mit dem Begriff Virtualisierung. So werden
Systeme im Storage-Bereich, welche auf Grundlage von mehreren Servern
einen gemeinsamen Speicher virtualisiert darstellen auch gerne als
Software-Defined-Storage bezeichnet. Gleiches gilt für
Netzwerkvirtualisierungskonzepte auf Basis von Software-Switchen oder
VXLAN, welche auch gerne unter der Kategorie [sdn]{acronym-label="sdn"
acronym-form="singular+short"} geführt werden.

Im Netzwerk-Bereich beschreibt der Begriff primär die Entkopplung der
[cp]{acronym-label="cp" acronym-form="singular+short"} von der
[dp]{acronym-label="dp" acronym-form="singular+short"}, was die
Notwendigkeit einer programmierbaren [dp]{acronym-label="dp"
acronym-form="singular+short"} sowie Protokolle zur Kommunikation dieser
beiden untereinander bedingt. Dies ermöglicht nicht nur die im vorigen
Kapitel erwähnten Optimierungen, sondern ermöglicht auch eine zentrale
Konfiguration von Netzwerken. Oberflächen-basierte Administrationstools
sind hierbei wesentlich einfache umzusetzen, da die Komplexität des
Netzwerkes nicht in der Konfiguration abgebildet wird.

### Unterscheidungsmerkmale SDN

#### Asymmetrisch vs Symmetrisch

[sdn]{acronym-label="sdn" acronym-form="singular+short"} Architekturen
lassen sich unterscheiden in Asymmetrisch und Symmetrisch. Bei
Asymmetrischen Modellen wird die [cp]{acronym-label="cp"
acronym-form="singular+short"} zentralisiert und in der Regel als eine
Software-Anwendung implementiert. Bei symmetrischen Modellen wird die
[cp]{acronym-label="cp" acronym-form="singular+short"} verteilt direkt
auf den einzelnen Netzwerkgeräten implementiert. Die Vorteile
asymmetrischer Modelle sind die zentrale Konfiguration und die
Verzichtbarkeit von Protokollen zur Verteilung von Informationen.
Nachteile ist das dieser Controller eine Single Point of Failure
darstellt. Zusätzlich können zentrale Controller nicht unbegrenzt mit
dem Netzwerk mit skalieren. Vorteile symmetrischer Modelle ist die
Architektur-bedinge Redundanz und Skalierung bei wachsender
Netzwerkgröße.

#### Floodless vs Floodbased

Wie Eingangs beschrieben basieren wichtige Mechaniken von Ethernet/IP
Netzwerken auf Broadcasts. Diese Broadcasts sind in allgemein in großen
Netzwerken und vermaschten Topologien problematisch. Daher versuchen
einige Ansätze diese Broadcasts zu unterdrücken und durch andere
Mechaniken zu ersetzen. Gesendete Broadcasts zur Auflösung von Adressen
werden abgefangen und direkt aus einer Datenbank heraus beantwortet.
Architekturen deren Verbreitung von Erreichbarkeits-Informationen nicht
auf Broadcasts basiert werden daher allgemein als Floodless bezeichnet.
Broadcasts werden allerdings auch gerne von Anwendungen auf der
Applikationsebene eingesetzt um zum Beispiel alle Drucker in einem
Netzwerk zu finden, was eine entsprechende Implementierung von
intelligenten Broadcasts oft notwendig macht.

#### Hostbased vs Netbased

Traditionellerweise ist das Netzwerk vollständig auf Netzwerkhardware
implementiert. Ein Host ist über ein einfaches Layer-2 Interface ohne
VLAN-Tag mit dem Netzwerk verbunden. Durch das Aufkommen von
Virtualisierungsplattformen und anderen Applikationsplattformen wie
Kubernetes welche innere Netzwerkarchitekturen haben, wurde begonnen
Netzwerkfunktionalität auf die Server zu ziehen. Prominentes Beispiel
ist der OpenvSwitch, welche zum Beispiel dafür verwendet wird Netzwerk
an Virtuelle Maschinen zu provisionieren. Diese virtuellen Switche sind
mittlerweile weit entwickelt und unterstützen Routing-Protokolle und
Virtualisierungsprotokolle wie VXLAN. Dies macht es naheliegend ein
VXLAN Overlay direkt auf dem Server zu terminieren, und die
konfigurative Komplexität in der Virtualisierungsanwendung zu
implementieren. Das physikalische Netzwerk stellt in diesen
Architekturen lediglich einfache IP Konnektivität her. Prominente
Beispiele sind OpenStacks Neutron, VMwares NSX und Flow von Nutanix.
Diese Produkte erlauben die Provisionierung von Netzwerkdiensten auf der
Anwendungsschicht.

### Erwartungen an SDN

Wie festgestellt gibt es keine scharfe Definition des Begriffes SDN.
Weiterhin wird versucht die auf SDN-Netzwerke projizierten Erwartungen
zu Beschreiben.

#### Erwartung 1: Controllerbasiert - Programmierbarkeit und Zentrales Management

Die abgekoppelte [cp]{acronym-label="cp" acronym-form="singular+short"}
ist häufig in Form einer zentralen Anwendung implementiert. Durch diese
Architektur ist die Konfiguration des gesamten Netzwerkes an eine
zentralen Stelle naheliegend. Dies wird als komfortabel empfunden und
stellt damit eine Anforderungen an solche Konzepte da. Weiterhin wird
das Netzwerk dadurch durch das anbieten von APIs durch den Controller
programmierbar. Dies ist auch mit einen klassischen Netzwerkansatz
möglich, allerdings ungleich komplexer.

#### Erwartung 2: Redundanz, Skalierfähigkeit und Weiterleitungsoptimierungen

Durch eine globale Controlplane lassen sich die
Paketweiterleitungsmechanismen optimieren und Redundant und die
Skalierfähigkeit eines Netzwerkes erhöhen. Weiterhin ist eine
intelligente Steuerung von Datenflüssen möglich, da dem Controller die
vollständige Topologie und im besten Fall auch die Auslastung einzelner
Links bekannt ist. Dieser kann entsprechend Pfade modifizieren.

#### Erwartung 3: Disaggregation Funktion/Software von Hardware

Die Software auf Switchen ist in der Regel eng an die jeweilige
Hardwareplattform gekoppelt und in seiner Bedienung und Funktionalität
sehr Herstellerspezifisch. Das Mischen von Plattformen verschiedener
Hersteller sollte in der Regel getestet werden und muss nicht unbedingt
funktionieren. Das liegt nicht nur an abweichenden Implementierungen von
Standards, sondern auch Mechanismen die Herstellerproprietär sind. Ein
gutes Beispiel sind [mlag]{acronym-label="mlag"
acronym-form="singular+short"} Protokolle, welche nicht standardisiert
sind und zwischen zwei unterschiedlichen Herstellerplattformen nicht
funktionieren. Der Einsatz einer Softwareplattform in einem Netzwerk auf
Hardwareplattformen verschiedener Hersteller kann dies entgegen wirken.
Der Vendor-Lockin kann damit erheblich minimiert werden.

#### Erwartung 4: Traffic Engineering

Traffic Engineering ist vorallem bei der Nutzung mehrerer
Netzwerk-Strecken mit verschiedenen Eigenschaften zur Verbindung
verschiedener Standorte. In diesem Bereich haben derzeit
Software-Defined-Lösungen eine relevante Verbreitung. Diese Lösungen
werden im allgemeinen mit SD-WAN bezeichnet. Ein Controller erfasst hier
verschiedene Metriken der Strecken wie Durchsatz und Paketverzögerung
und weißt auf Basis dessen Datenverkehr einen optimierten Pfad zu. Damit
können geschlossene Regelkreise zur idealen Nutzung von Netzwerkstrecken
und Überwachung von Mindestanforderungen für zum Beispiel
Videotelefonie.

### WCMP

In traditionellen vermaschten IP-Netzwerken wird der Datenpfad in der
Regel durch Routing-Protokolle bestimmt. Da es in einem vermaschten
Netzwerk mehrere Wege zwischen zwei Routern gibt, nutzen
Routing-Protokolle in der Regel Algorithmen die die Pfadkosten der
verschiedenen Wege bestimmen um den optimalen Pfad zu bestimmen. Dies
führt dementsprechend dazu, dass die Daten unabhängig der Auslastung der
Strecke, immer den selben Pfad nutzen. Eine Erweiterung dessen bieten
manche Protokolle mit ECMP - Equal Cost Multipathing. Hierbei werden auf
Basis eines konfigurierbaren Load-Sharing Algorithmuses die Daten auf
Pfade mit gleichen Kosten aufgeteilt. Eine konsequente Erweiterung davon
ist WCMP - Weighted Cost Multipathing. Hierbei werden die verschiedenen
Links dynamisch auf Basis der aktuellen Auslastung ider anderen
messbaren Metriken wie Jitter gewichtet. Die Implementierung dessen
erfordert allerdings eine Instanz die dynamisch die Strecken bewertet
und eben entsprechend gewichtet. Cisco hat WCMP auch schonmal in ihrem
Routing-Protokoll EIGRP implementiert, hierbei wurden Metriken zu
einzelnen Links zwischen den Routern verteilt und zur Gewichtung von
Pfaden genutzt.

### Kontext zum Begriff Netzwerkvirtualisierung

Der Begriff der Netzwerkvirtualisierung beschreibt die Abbildung einer
Netzwerkinfrastruktur unabhängig der darunter liegenden physikalischen
Topologie. Ein einfaches Beispiel sind VLANs.Im komplexeren Fall lassen
sich Netzwerke auf Basis von Enkapsulierungsprotokollen wie zum Beispiel
VXLAN auch über geroutete Strecken wie das Internet hinweg abbilden. Der
Begriff wird ebenfalls für den Einsatz virtueller Switche auf
Virtualisierungsplattformen genutzt. An diesen virtuellen Switch werden
Anwendungen in Form von Virtuellen Maschinen angeschlossen. Dieser
Switch kann nach außen auch als Router oder Tunnel-Endpunkt fungieren,
und Komplexität vom Netzwerk in die Anwendungsebene ziehen.

### Kontext zum Begriff Fabric

Im Netzwerkbereich wird der Begriff Fabric üblicherweise für Konzepte
genutzt, bei denen die Switche in einem vermaschten Topologie vernetzt
sind. Die Beschränkungen herkömmlicher Strukturen, in denen ein Netzwerk
Sternförmig aufgebaut werden muss was Konzepte mit mehreren Stufen wie
Core, Aggregation und Edge erfordert gelten hier nicht. Weiterhin ist es
Anspruch an eine Fabric diese beliebig erweitern zu können sowie eine
Konfiguration eines Services nur am Rand oder per Controller durchführen
zu können. Um eben diese Freiheiten zu erreichen sind Techniken aus dem
vermeintlichen SDN-Bereich notwendig.

Netzwerksimulation
------------------

Ähnlich wie in anderen Technologiesektoren entwickeln sich die Ansätze
und Technologien im Netzwerkbereich mit steigender Geschwindigkeit
weiter. Netzwerke nachzubauen kann hilfreich zum evaluieren von
Konzepten, zur Validierung von Änderungen an bestehenden Netzwerken und
zur Schulung und Lehre sein. Die Fähigkeit ein Netzwerk zu simulieren
ist nicht nur erheblich kostengünstiger, sondern ermöglicht auch den
Aufbau komplexer Topologien mit weniger zeitlichen und
arbeitstechnischen Aufwand. Herausforderung ist die Implementierung von
hardwarenahen Funktionen, welche bei den physikalischen Geräten direkt
im Chip implementiert sind.

Die Vorteile und Notwendigkeiten der Netzwerksimulation haben auch viele
Hersteller erkannt und bieten eigene Simulationsplattformen an. Gerne
genutzter Marketingbegriff hierfür ist Digital Twin, zu Deutsch
Digitaler Zwilling.

Ein Überblick über derzeit von Herstellern vertriebene
Simulationslösungen:

-   Cisco Modeling Labs

-   H3C Cloud Lab

-   ExtremeCloud IQ Co-Pilot: Digital Twin

-   Aruba AOS-CX Switch Simulator

Diese sind teilweise Cloud-basiert wie die Lösung von Cisco, und
teilweise in Grundlage ein GNS3 mit modifizierter Oberfläche wie die
Lösung von H3C.

Einige Hersteller bieten stattdessen oder simultan auch eine virtuelle
Variante ihres Switch-OS an, um dieses in eigenen Simulationsumgebungen
einzusetzen. Beispiele sind:

-   **DELL OS10** - Dell bietet auf seiner Homepage ein GNS-3 Bundle von
    DELL-OS10 an.

-   **Extreme EXOS** - Extreme bietet im Marktplatz von GNS-3 eine
    virtuelle Variante ihres Switch-Betriebsystemes an.

-   **vEOS** - Arista bietet eine allgemeine virtuelle Variante ihres
    Betriebsystemes an, welche dadurch auch in GNS-3 lauffähig ist.

-   **SONiC** - Die Entwickler von SONiC bieten eine virtuelle Variante
    SONIC-VSin Repository an.

´

Referenztopologie {#sec:ref}
-----------------

Um den weiteren Evaluationen und Bewertungen ein Rahmen zu geben soll
ein imaginären Campus-Netzwerk als Referenz definiert werden.

![Referenzkunde](media/customer.png){width="100%"}

Das Unternehmen erstreckt sich über 5 Standorte. In den Standorten 1 und
4 sind Rechenzentren mit Business-Anwendungen wie ERP-Systeme und
ähnlichem angesiedelt. Weiterhin gibt es in Gebäude 3 Produktionsanlagen
die einen hochverfügbaren Zugang zu den Business-Anwendungen benötigen,
da sie bei Abbruch der Verbindung nicht produzieren können. Weiterhin
gibt es ein abgelegenes Büro (2) sowie ein Training-Zentrum zur Schulung
von Kunden (5).

![Referenz Netzwerktopologie](media/customer2.png){#fig:reftop
width="100%"}

Die Gebäude befinden sich verteilt in einem Gewerbegebiet und einer
Stadt, Glasfaserleitungen wurden wir in Abbildung
[1.1](#fig:reftop){reference-type="ref" reference="fig:reftop"} verlegt.
Eine Änderung dieser Topologie ist nur mit baulischen Maßnahmen mit
immensen Kosten möglich.

Die Anforderungen aus dem Netzwerk ergeben sich aus den angeschlossenen
Geräten sowie den Nutzern. So wird für Stechterminals eine Layer-2
Verbindung von allen Standorten hin zu einem der Rechenzentren benötigt.
Zusätzlich benötigt die Trainingsabteilung oft Layer-2 und Layer-3
Testnetzwerke hin zu einem der Rechenzentren.

Da die Mitarbeiter durch Port-Authentifizierung dynamisch und
standortunabhängig einem VLAN zugewiesen werden, müssen auch
Client-VLANs überall verfügbar sein. Es soll ein Routing zwischen den
Netzwerken abseits einer Firewall nötig sein, da einzelne Schutzzonen
wie die von Anlagensteuerungen die sinnvolle Größe von Subnetzen
überschreiten, aber durch einen hohes Datenaufkommen nicht über die
Firewall geschoben werden sollen.

Die Topologie wird vereinfacht mit einem einzelnen Switch pro Standort
betrachtet. Nicht in der Betrachtung sind Access-Technologien wie
Dual-Homing Technologien zum redundanten Anschluss von Servern.

Grundlagen
