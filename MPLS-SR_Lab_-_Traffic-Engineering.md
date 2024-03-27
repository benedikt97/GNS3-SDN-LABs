MPLS-SR Lab - Traffic-Engineering
=================================

In dieser Simulation wird ein mehrschichtiges Netzwerk auf Basis von
MPLS aufgebaut. Als Controlplane-Protokoll wird für MPLS das Link-State
Routing-Protokoll ISIS eingesetzt. Als Routing-Technik wird Segment
Routing genutzt, welches mit OSPF und ISIS realisierbar ist. Das
Segment-Routing auf Basis von ISIS ersetzt die Notwendigkeit von LDP
sowie von RSVP-TE. Für die Virtualisierung von Kundennetzwerken über das
MPLS-Netzwerk wird EVPN eingesetzt. EVPN ersetzt an der Stelle die
klassisch eingesetzten Technologien MPLS L3VPN und VPLS. Der Vorteil von
EVPN ist die Kombinierung von Layer-2 und Layer-3 Services sowie die
optimierte Mechanik zum Lernen von MAC-Adressen gegenüber VPLS. Für das
EVPN wird auf den Switchen am Rand des Netzwerkes BGP konfiguriert.

Traffic-Engineering wird durch das Segment-Routing ermöglicht. Die dafür
notwendigen Policys werden auf dem eingehenden MPLS-Router konfiguriert.
Dies kann statisch über die CLI erfolgen, oder mittels einem Controller
der in diesem Zusammenhang PCE - Path Computation Element genannt wird.
Dieser verbindet sich zu den Routern über eine BGP-Session und sammelt
sowie verteilt Informationen über einen eignen BGP-Adresstyp.

Anhänge
