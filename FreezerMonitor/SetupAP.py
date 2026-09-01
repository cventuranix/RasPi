#########################################################
# Using a RasPi PIo 2 W
# This app and simple sensors will monitor a Freezer
# Temp sensor ds18x20
# Switch https://www.amazon.com/dp/B085XQLQ3N?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_1&th=1
# Batt  https://www.amazon.com/dp/B0BFX5B5YL?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_1
# Door Switch Blue to Voltage, Black to pin 31

#Notes:
# Webserver runs on its own core.
###########################################################



import network
import socket
import time
import urequests
import requests
import gc
import os
import _thread
import ntptime
from machine import Pin
from machine import ADC
import onewire
import machine
import ds18x20
from URLs import RepoURL # Config file with URLs to fetch Data


#Power On LED	
led = Pin("LED", Pin.OUT)
led.on()


#WiFI Info
#BELOW Settings for Lab Testing, REMOVE FROM Release Code!!!
ssid = 'Penny24'
password = 'feadfeadfe'


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
#wlan.connect(ssid, password)

# Wait for connection 
#while not wlan.isconnected():
#    time.sleep(1)
#NetConfig=wlan.ifconfig()
#print(NetConfig)
#print('IP:', NetConfig[0])

##### Add Code Here #####

#If config.py doesn't exist, enter setup

def file_exists(filename):
        try:
            os.stat(filename)
            return True
        except OSError:
            return False

if file_exists("config.py"):
    print("config.py exists!")
else:
    print("Entering Setup Mode....")
    SSID = "FeezerMon"
    PASSWORD = "Fr3323r!"
    def start_access_point(SSID, PASSWORD):
    # Initialize the Access Point interface
        ap = network.WLAN(network.AP_IF)
    # Configure network name and security
        ap.config(essid=SSID, password=PASSWORD)
    # Activate the AP
        ap.active(True)
    # Wait for the interface to become active
        while not ap.active():
            time.sleep(1)
        
        print("Access Point successfully activated!")
        print("IP Address configuration:", ap.ifconfig())
        ip_address = ap.ifconfig()[0]
        print(ip_address)
        
        html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
            <body><h1>FreezerMon Setup!</h1><H3><form id="form">
            
            <input name="SSID" id="red">
            <label for="red">SSID</p>
            
            <input name="Passkey" id="green">
             <label for="green">Passkey</p>
            
            <input name="Text Number" id="blue">
            <label for="blue">Text Number</p>
            
            <input type="submit" id="submit">
        </form></body></html>"""
            
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #creating socket object
        s.bind(('', 80))
        s.listen(5)
        print(ip_address)
        while True:
            conn, addr = s.accept()
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024)
            print('Content = %s' % str(request))
            response_header = "HTTP/1.1 200 OK\r\n"
            response_header += "Content-Type: text/html; charset=utf-8\r\n"
            response_header += f"Content-Length: {len(html)}\r\n\r\n"
            response = html
            conn.send(response_header)
            response = html
            conn.send(response)
            conn.close()
        
        
        
 # Run Setup Access Point
    start_access_point(SSID, PASSWORD)
    
    #while ap.active() == False:
    #   pass
    print('Connection is successful')
    
    


