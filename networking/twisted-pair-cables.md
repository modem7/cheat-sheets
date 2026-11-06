# Twisted Pair Cables Cheat-Sheet
## Cable Types

### Unshielded Twisted Pair (UTP)

As the title states, a UTP cable has no shielding. This is the most used and most basic type of cable. The cable contains pairs of wires twisted together to help reduce and prevent electromagnetic interference.

### Shielded Twisted Pair (STP)

STP cables are similar to UTP cables, where the wires are twisted together and then wrapped with a shielding or screening material which consists of foil wrapping or a copper braid jacket.

### Foil Twisted Pair (FTP)

With FTP cables, each twisted pair of cables is wrapped in a shielding of foil to protect the cable from EMI and crosstalk.

### Shielded Foil Twisted Pair (S/FTP)

A cable that is classified as S/FTP or Shielded Foil Twisted Pair is a combination of both FTP and STP shielding. The wires inside the cable are twisted and then shielded with a foil wrapping, then the 4-pair grouping of foiled wires are shielded by a wrapping of either foil or a flexible braided screening. This provides the highest level of protection against EMI and crosstalk.

## Wiring

### TIA/EIA 568A Wiring
PIN | COLOR | COLOR-TEXT
---|---|---
1 | <span style="color:green">█</span>█<span style="color:green">█</span>█<span style="color:green">█</span>█ | White and Green
2 | <span style="color:green">██████</span> | Green
3 | <span style="color:orange">█</span>█<span style="color:orange">█</span>█<span style="color:orange">█</span>█ | White and Orange
4 | <span style="color:blue">██████</span> | Blue
5 | <span style="color:blue">█</span>█<span style="color:blue">█</span>█<span style="color:blue">█</span>█ | White and Blue
6 | <span style="color:orange">██████</span> | Orange
7 | <span style="color:brown">█</span>█<span style="color:brown">█</span>█<span style="color:brown">█</span>█ | White and Brown
8 | <span style="color:brown">██████</span> | Brown
### TIA/EIA 568B Wiring
PIN | COLOR | COLOR-TEXT
---|---|---
1 | <span style="color:orange">█</span>█<span style="color:orange">█</span>█<span style="color:orange">█</span>█ | White and Orange
2 | <span style="color:orange">██████</span> | Orange
3 | <span style="color:green">█</span>█<span style="color:green">█</span>█<span style="color:green">█</span>█ | White and Green
4 | <span style="color:blue">██████</span> | Blue
5 | <span style="color:blue">█</span>█<span style="color:blue">█</span>█<span style="color:blue">█</span>█ | White and Blue
6 | <span style="color:green">██████</span> | Green
7 | <span style="color:brown">█</span>█<span style="color:brown">█</span>█<span style="color:brown">█</span>█ | White and Brown
8 | <span style="color:brown">██████</span> | Brown

## Categories

CATEGORY | MHz | Speed
---|---|---
CAT 3 UTP | 16MHz | 10Mbps up to 100m
CAT 4 UTP | 20MHz | 16Mbps up to 100m
CAT 5 UTP | 100MHz | 100Mbps up to 100m
CAT 5e UTP | 100MHz | 1000Mbps up to 100m
CAT 5e STP | 100MHz | 1000Mbps up to 100m
CAT 6 UTP | 250MHz | 10Gbps up to 55m (37m in noisy conditions)
CAT 6a STP | 500MHz | 10Gbps over 100m
CAT 7 STP | 600MHz | 10Gbps over 100m
CAT 7a STP | 1000MHz | 10Gbps over 100m
CAT 8 STP | 2000MHz | 25/40Gbps up to 30m

CAT 6a is rated for 10 Gbps over the full 100 m, and Cat 7 and 7a are ISO/IEC standards that use GG45 or TERA connectors and are not recognised by TIA (in practice you will meet Cat 6a or Cat 8 with RJ45). Gigabit works on Cat 5e, and 2.5 and 5 Gbps (multi-gig) usually run on existing Cat 5e or Cat 6.

## Straight-Through and Crossover
- **Straight-through**: the same standard on both ends (both T568B is the most common). Used for PC to switch or router.
- **Crossover**: T568A on one end and T568B on the other. Rarely needed today, since modern ports use Auto-MDIX.
- Gigabit and faster use all four pairs. 10/100 uses only pins 1, 2, 3 and 6.

## Practical Notes
- Maximum run is 100 m (90 m permanent link plus patch leads).
- Use solid copper (not CCA, copper-clad aluminium) for PoE and long runs.
- Test with a cable tester and, for patch panel work, a certifier.
- PoE (802.3af/at/bt) delivers 15 to 90 W, and thicker cable heats less.
