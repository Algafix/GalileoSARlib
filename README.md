GalileoSARlib
========

GalileoSARlib is an open-source Python library that can be used for research purposes on the Search and Rescue return link provided by Galileo in the E1-B signal.

The Galileo E1-B Return Link contemplates 2 types of service:

* Short-RLM: `Acknowledgment Service Type-1`
* Short-RLM: `Test Service`

Then, the Beacon-ID for each of these services contains partial data of a Cospas-Sarsat protocol. Currently, the following are supported:

* Orbitography Protocol -> Transmitted in the `Test Service`
* RLS Location Protocol -> Transmitted in the `Acknowledgment Service Type-1` and `Test Service`

If more protocols are seen in the future, we will implement them.

Currently, we only support SBF files as input, but this will be extended.
The parsed output of the library is displayed to console and saved into a json file.

Documentation
---

You may be interested in the presentation given at the European Conference of Navigation 2025 on the analysis of 90 days of the Galileo Return Link Service.

* Paper: [local](ENC25_DATA/ENC25_SAR_paper.pdf) - [online](https://www.mdpi.com/2673-4591/126/1/13)
* Slides: [local](ENC25_DATA/ENC25_SAR_presentation.pdf)

Usage
---

```[shell]
usage: extract_sar.py [-h] [-s] [in_file] [out_file]

Parse the Galileo I/NAV message for E1-B to extract and parse the SAR information.

positional arguments:
  in_file
  out_file

options:
  -h, --help       show this help message and exit
  -s, --skip-test  don't show the Test Service messages
```

Example console output:

```[shell]
2024/05/08 01:03:55 - 2313 263053 - SVID 09
        RLM Identifier: SHORT_RLM (0)
        Beacon ID: 2ddb2de67f3fdff
        Message Code: ACK_SERVICE (0001)
        SRL Parameters: 1000000000000001
                Protocol Type: Standard or national location protocols (0)
                Country Code: United States of America (366)
                Protocol Code: RLS Location Protocol (1101)
                Beacon Type: PLB (10)
                C/S RLS TAC (trunc): 367 (0101101111)
                C/S RLS TAC: 3367
                        Manufacturer: Ocean Signal Ltd.
                        Model: PLB-450
                        Last rev. Date: 2023-06-23
                        Nav Info: Int
                Serial Number: 3326 (00110011111110)
                Lat: N 255 (0 11111111)
                Lon: E 511 (0 111111111)

2024/05/29 14:20:55 - 2316 310873 - SVID 09
        RLM Identifier: SHORT_RLM (0)
        Beacon ID: 21fa783aa23fdff
        Message Code: ACK_SERVICE (0001)
        SRL Parameters: 1000000000000000
                Protocol Type: Standard or national location protocols (0)
                Country Code: Republic of Türkiye (271)
                Protocol Code: RLS Location Protocol (1101)
                Beacon Type: First EPIRB on Vessel (00)
                6-digit MMSI: 30020 (00000111010101000100)
                Lat: N 255 (0 11111111)
                Lon: E 511 (0 111111111)

2024/05/29 12:06:11 - 2316 302789 - SVID 10
        RLM Identifier: SHORT_RLM (0)
        Beacon ID: 9a22be29630f010
        Message Code: TEST_SERVICE (1111)
        SRL Parameters: 0011101100000010
                Protocol Type: User or user-location protocols (1)
                Country Code: Cyprus (Republic of) (209)
                Protocol Code: Orbitography Protocol (000)
                Orbitography Beacon ID: GAL-EU5 (101011111000101001011000110000111100000001)
                Four Zeros: 0000
```
