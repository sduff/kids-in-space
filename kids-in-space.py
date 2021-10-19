#!/usr/local/bin/python3

import os, shutil, json, time, re
try:
    import RPi.GPIO as GPIO
    from board import SCL, SDA
    import busio
    from adafruit_pca9685 import PCA9685
except:
    print("WARNING: No GPIO module, is this running on a pi?")
    GPIO = None

try:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except:
    from http.server import BaseHTTPRequestHandler, HTTPServer

# listen on port 8000 of the localhost
addy = ('',8000)

web_dir = "web"

# Set LEDs via PCA9685
def set_leds(pattern):
        # pattern should be a 8 element array
        pca.channels[0].duty_cycle = pattern[0]
        pca.channels[1].duty_cycle = pattern[1]
        pca.channels[2].duty_cycle = pattern[2]
        pca.channels[3].duty_cycle = pattern[3]

        pca.channels[8].duty_cycle = pattern[4]
        pca.channels[9].duty_cycle = pattern[5]
        pca.channels[10].duty_cycle = pattern[6]
        pca.channels[11].duty_cycle = pattern[7]
        return

# Various LED Scan patterns
scan =  [
                #       0       1       2       3       4       5       6       7
                [       0xffff, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000  ],
                [       0x0000, 0xffff, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000  ],
                [       0x0000, 0x0000, 0xffff, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000  ],
                [       0x0000, 0x0000, 0x0000, 0xffff, 0x0000, 0x0000, 0x0000, 0x0000  ],
                [       0x0000, 0x0000, 0x0000, 0x0000, 0xffff, 0x0000, 0x0000, 0x0000  ],
                [       0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0xffff, 0x0000, 0x0000  ],
                [       0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0xffff, 0x0000  ],
                [       0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0xffff  ]
        ]

countdown = [
                #       0       1       2       3       4       5       6       7
                [       0xffff, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0xffff  ],      # 3
                [       0xffff, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0xffff  ],      # 3
                [       0xffff, 0xffff, 0x0000, 0x0000, 0x0000, 0x0000, 0xffff, 0xffff  ],      # 2
                [       0xffff, 0xffff, 0x0000, 0x0000, 0x0000, 0x0000, 0xffff, 0xffff  ],      # 2
                [       0xffff, 0xffff, 0xffff, 0x0000, 0x0000, 0xffff, 0xffff, 0xffff  ],      # 1
                [       0xffff, 0xffff, 0xffff, 0x0000, 0x0000, 0xffff, 0xffff, 0xffff  ],      # 1
                [       0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff  ]       # ignition
                [       0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff  ]       # ignition
                [       0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff  ]       # ignition
                [       0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff  ]       # ignition
        ]

lift_off = [
                #       0       1       2       3       4       5       6       7
                [       0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff  ],
                [       0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000  ],
                [       0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff  ],
                [       0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000  ],
                [       0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff  ],
                [       0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000  ],
                [       0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff  ],
                [       0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000  ],
                [       0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff  ],
                [       0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000  ]
        ]

warp = [
                #       0       1       2       3       4       5       6       7
                [       0x2000, 0x0000, 0x0000, 0xffff, 0xffff, 0x0000, 0x0000, 0x2000  ],
                [       0x0000, 0x0000, 0xffff, 0x2000, 0x2000, 0xffff, 0x0000, 0x0000  ],
                [       0x0000, 0xffff, 0x2000, 0x0000, 0x0000, 0x2000, 0xffff, 0x0000  ],
                [       0xffff, 0x2000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2000, 0xffff  ]
        ]

off =   [       0,      0,      0,      0,      0,      0,      0,      0       ]


# Servo config
SERVO_MIN   = 0x1000
SERVO_HALF  = 0x2000
SERVO_MAX   = 0x6000

# A global data structure for access between HTTP server and main code
config = {}

mime = {
    ".html": "text/html",
    ".png": "image/png",
    ".js": "text/javascript",
    ".json": "application/json",
    ".gif": "image/gif",
    ".jpg": "image/jpg"
    }

# define the http handler
class httpd_handler(BaseHTTPRequestHandler):
    def do_GET(self):

        # get the state
        if self.path == "/state":
            # return a json object of the current state
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config).encode())
            return

        # set various LED pattern modes
        if self.path == "/LEDs/off":
            config["leds"] = "off"
            config["led-step"] = 0
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config).encode())
            return

        if self.path == "/LEDs/scan":
            config["leds"] = "scan"
            config["led-step"] = 0
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config).encode())
            return

        if self.path == "/LEDs/countdown":
            config["leds"] = "countdown"
            config["led-step"] = 0
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config).encode())
            return

        if self.path == "/LEDs/liftoff":
            config["leds"] = "liftoff"
            config["led-step"] = 0
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config).encode())
            return

        if self.path == "/LEDs/warp":
            config["leds"] = "warp"
            config["led-step"] = 0
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config).encode())
            return

        # Set servo positions
        if self.path == "/servo0/0":
            config["servo0"] = SERVO_MIN
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config).encode())
            return

        if self.path == "/servo0/100":
            config["servo0"] = SERVO_MAX
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config).encode())
            return

        if self.path == "/servo0/50":
            config["servo0"] = SERVO_HALF
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config).encode())
            return

        if self.path == "/servo1/0":
            config["servo1"] = SERVO_MIN
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config).encode())
            return

        if self.path == "/servo1/100":
            config["servo1"] = SERVO_MAX
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config).encode())
            return

        if self.path == "/servo1/50":
            config["servo1"] = SERVO_HALF
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(config).encode())
            return

        # check if tricorder found an element, and if so, update the state
        # XXX: Dirty hack, fix this one day
        el = re.compile("/tricorder/data/(?P<element>.*).json")
        m = el.match(self.path)
        if m:
            config[m.group('element')] = 1

        # file access
        if self.path.endswith("/"):
            f = os.path.join(".", web_dir, self.path[1:], "index.html")
        else:
            f = os.path.join(".", web_dir,self.path[1:])

        print("Request %s, file is %s"%(self.path, f))

        if os.path.exists(f) and os.path.isfile(f):
            # XXX: possibly security risk here, need to expand .. in filepaths
            _, ext = os.path.splitext(f)
            if ext in mime:
                ctype = mime[ext]
            else:
                ctype = "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-type", ctype)
            self.end_headers()
            shutil.copyfileobj(open(f, 'rb'), self.wfile)
        else:
            # file requested is invalid
            self.send_error(404)

        return

    def do_POST(self):
        return

# -- start here -- #

# create http daemon
# TODO: Make this threaded
httpd = HTTPServer(addy,httpd_handler)
httpd.timeout = 0.1

print("Starting HTTP Server")
config['httpd_running'] = True

# configure the PCA9685 on the I2C ports
i2c_bus = busio.I2C(SCL, SDA)
pca = PCA9685(i2c_bus, address=0x40)
pca.frequency = 60

last_tic = int(time.time()*1000) # msec, assuming the OS reports sub-seconds
while config['httpd_running']:
    # Check for any pending HTTP events
    httpd.handle_request()

    cur_time = int(time.time()*1000)
    if cur_time-last_tic>500:   # tic every 500ms
        last_tic = cur_time

        # update LEDs
        led = config["leds"]
        ledstep = config["led-step"]

        if led == "off":
            set_leds(off)
        elif led == "scan":
            if ledstep > len(scan):
                ledstep = 0
            set_leds(scan[ledstep])
            config["led-step"] = ledstep
        elif led == "countdown":
            if ledstep > len(countdown):
                ledstep = 0
            set_leds(countdown[ledstep])
            config["led-step"] = ledstep
        elif led == "liftoff":
            if ledstep > len(liftoff):
                ledstep = 0
            set_leds(liftoff[ledstep])
            config["led-step"] = ledstep
        elif led == "warp":
            if ledstep > len(warp):
                ledstep = 0
            set_leds(warp[ledstep])
            config["led-step"] = ledstep

        # Update servo positions
        if "servo0" in config:
            pos = config["servo0"]
            pca.channels[14].duty_cycle = pos
            del config["servo0"]
        if "servo1" in config:
            pos = config["servo1"]
            pca.channels[15].duty_cycle = pos
            del config["servo1"]


print("Stopped HTTP Server")
