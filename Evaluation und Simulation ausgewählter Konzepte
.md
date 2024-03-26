Evaluation und Simulation ausgewählter Konzepte
===============================================

In den folgenden Kapiteln werden mehrere [sdn]{acronym-label="sdn"
acronym-form="singular+short"}-Konzepte erläutert sowie auf Basis
quelloffener Software in GNS3 simuliert. Für die Implementierung eines
Designs wird, wenn möglich, die Referenztopologie aus
[1.6](#sec:ref){reference-type="ref" reference="sec:ref"} genutzt.

Begonnen wird mir jeweils zwei Architekturen auf Basis von OpenFlow,
welche sich in Ihrer Mechanik zur Weiterleitung von Paketen
unterscheiden. Der erste Ansatz zeigt eine Netzwerkarchitektur die auf
traditionellen Ethernet-Mechaniken zur Weiterleitung von Paketen
basiert. Der Zweite Ansatz basiert auf einen Flow-basierten Ansatz.

P4Runtime ist der technologische Nachfolger von OpenFlow von der
[onf]{acronym-label="onf" acronym-form="singular+short"}. Während
OpenFlow nur ein Protokoll ist und die Switch-seitige Implementation in
Händen der Hersteller ist, wird bei P4Runtime auch die Switch-seitige
Implementation mittels eines P4-Programms durch den Netzwerkarchitekt
gegeben. Dies soll das Problem von nicht vollständigen und
unterschiedlich funktionierenden OpenFlow-Implementationen
architektonisch lösen. Es wird ein Software-basierter Switch gezeigt,
der sich per P4 programmieren lässt sowie eine P4Runtime Schnittstelle
hat. Zusätzlich soll die aktuelle [onf]{acronym-label="onf"
acronym-form="singular+short"} Referenzimplementation SD-Fabric
eingegangen werden, welche auf Segment Routing und MPLS basiert.

Zuletzt wird ein Ansatz auf BGP-EVPN gezeigt, welcher nicht unmittelbar
der [sdn]{acronym-label="sdn" acronym-form="singular+short"}-Definition
entspricht, da die Controlplane zwar zwischen den VTEPs durch ein
Routing-Protokoll implementiert wird, das Netzwerk hierdurch aber nicht
unmittelbar programmierbar wird. Die Martkanalyse zeigt allerdings eine
erhebliche Verbreitung solcher Underlay/Overlay Architekturen in
Lösungsdesigns sowie in Form von Protokollimplementationen.

Auswahl virtueller Switche
--------------------------

Für die Simulation der weiterhin genannten Konzepte wird jeweils ein
virtuelle Switch mit einer Implementierung von a) OpenFlow, b) BGP-EVPN
und c) P4Runtime benötigt. An dieser Stelle wird kurz die Auswahl der
entsprechend eingesetzten Plattformen begründet.

#### OpenFlow

Bei den getesteten virtuellen Hardware-Plattformen mit OpenFlow
Unterstützung, die durch Hersteller angeboten werden, kann OpenFlow zwar
konfiguriert werden, die Regeln werden aber nicht umgesetzt. Bei den
Hardware-Appliances geschieht dies in der Regel über Schnittstellen der
ASIC-Anbieter wie zum Beispiel Broadcoms OF-DPA [@broadcomofdpa]. Eine
Umsetzung in den virtuellen Versionen ist daher komplex und bedarf
Entwicklungsaufwand. Aus diesem Grund wird für die OpenFlow-basierten
Konzepte der OpenVSwitch eingesetzt. Dieser wird in OpenStack Umgebungen
eingesetzt. Da der OpenStack Netzwerk-Stack in Form von Neutron auf
OpenFlow basiert, ist die Implementierung von OpenFlow im OpenVSwitch
als vollständig anzunehmen.

#### BGP-EVPN

BGP-EVPN wird von SONiC in der virtuellen Variante unterstützt. Aktuell
in der virtuellen Variante nicht unterstützt werden Anycast-Gateways
sowie EVPN-Multihoming.

#### P4Runtime

Für P4Runtime wird die Referenzimplementierung Stratum auf Basis der
P4-Referenzimplementierung bmv2verwendet. Bei SONiC wird P4Runtime über
PINS implementiert, ist allerdings aktuell nicht in der virtuellen
Variante umgesetzt. Eine Umsetzung in der virtuellen Variante mittels
DPDK befindet sich im Backlog - SONiC with P4 DPDK (PNA architecture) --
Basic SoftSwitch with DPDK - Deferred from 202205 release der SONiC
Roadmap. [@sonicroadmap].

OpenFlow I: Controller- und Broadcastbasiert mit Faucet {#sec:of1}
