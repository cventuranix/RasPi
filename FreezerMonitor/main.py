##########################################################
# Using a RasPi PIo 2 W
# This app and simple sensors will monitor a Freezer
# Temp sensor ds18x20
# Switch https://www.amazon.com/dp/B085XQLQ3N?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_1&th=1
# Batt  https://www.amazon.com/dp/B0BFX5B5YL?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_1
#
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

print(os.listdir())
#if os.stat("config.py"):
 #   print("File exists!")
#else:
#    print("Entering Setup Mode...")
    
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



wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connection 
while not wlan.isconnected():
    time.sleep(1)
NetConfig=wlan.ifconfig()
#print(NetConfig)
print('IP:', NetConfig[0])

##### Add Code Here #####

# Check for URL update
# Grab code
URLOutputFile="RepoURLs.py"
print(RepoURL)
response = urequests.get(RepoURL)
if response.status_code == 200:
    # Write the contents in 'wb' (write binary) mode
    with open(URLOutputFile, "wb") as file:
        file.write(response.content)
        print("Download complete.")
    #print(f"Failed to download. Status code: {response.status_code}")
    #print("Getting new URL File....")
    #print(response.status_code)
    response.close()
    
print("Opening: ",URLOutputFile)
with open(URLOutputFile, "r") as file:
    print(file.read())


file.close()



SecondsSinceBoot=(time.ticks_ms()/1000)

print('Seconds since boot:',SecondsSinceBoot)

#Get Local Time
now = time.localtime()
hour = now[3]
minute = now[4]
print('Time:',hour,":",minute)

#Test SMS
# Twilio Credentials and Parameters
account_sid = "SK6688a13c486f0329e74ee3c2b7fbc5f9"
auth_token = "UUosxJhFn45JbWPrK0aJPzrQTszSDBbI"
sender = "+17372583742"
recipient = "+15104150750"
message_body = "Raspberry Pi Pico 2 W ONLINE!"
Turl = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
data = f"From={sender}&To={recipient}&Body={message_body}"
#response = urequests.post(Turl, data=data, headers=headers)
#response = urequests.post(Turl, data=data, headers=headers, auth=(account_sid,auth_token))
#print(response.status_code)
#if response.status_code >= 200 and response.status_code < 300:
#    print("SMS sent successfully!")
#else:
#    print("Failed to send SMS:", response.text)

#response.close()
#SID=SK6688a13c486f0329e74ee3c2b7fbc5f9
#Secret=UUosxJhFn45JbWPrK0aJPzrQTszSDBbI
#AuthToken=d90c847dc1a6c928109e5236c76bff87
#AccountSID=AC569ec7c30e155675da831a120e59f914

##########################################################################
# MAIN CODE STARTS HERE

ip_address = wlan.ifconfig()

def webserver():
    while True:
        #Power Sensor
        batt_sensor = ADC(28) # Pin 34 On Pico 2W
        
        PowerMultiplier=.00005646 # 3.7/65536
        
        BattSensor = batt_sensor.read_u16()
        if BattSensor > 60512:
            BattLevel="95%" 
        elif BattSensor > 59512:
            BattLevel="90%"
        elif BattSensor > 58802:
            BattLevel="80%"  
        elif BattSensor > 58448:
            BattLevel="70%"   
        elif BattSensor > 57917:
            BattLevel="60%" 
        elif BattSensor > 57739:
            BattLevel="50%"
        elif BattSensor > 57562:
            BattLevel="40%"  
        elif BattSensor > 57031:
            BattLevel="30%"    
        elif BattSensor > 56854:
            BattLevel="20%"
        elif BattSensor > 53490: #6023
            BattLevel="10%"
        else:
            BattLevel=0
    # Setup Webpage
    # Set up socket and start listening
        print('Setting up web server...') 
    # Main loop to listen for connections
        if ip_address:
        # Set up the TCP socket
            addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
            s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(addr)
            s.listen(1)
        
            print("Listening on port 80...")
        
    
            print('Building Web Page...')
        temp_f=77
        def get_html():
            html = f"""
                <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Pico Web Server</title>
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                    </head>
                    <body>
                        <h1>Freezer Monitor Status</h1>
                        <h2>Time: {hour}:{minute}
                        Battery: {BattLevel}
                        Temp Sensor: {temp_f}F
                        Door Sensor: {Door}
                    </body>
                    </html>
                    """
            return str(html)
        print('Waiting for connections...')

        client, addr = s.accept()
        print('Got a connection from', addr)
        
        # Receive and parse the request
        request = client.recv(1024).decode('utf-8')
        request = str(request)
        print('Request content = %s' % request)

        # Generate HTML response
        response = get_html()  

        # Send the HTTP response and close the connection
        client.send('HTTP/1.1 200 OK\n')
        client.send('Content-Type: text/html\n')
        client.send('Connection: close\n\n')
        client.sendall(response)
        client.close()
        s.close()
        print('Connection closed')
#        s.close()
            
    
# End Web Page

#Run Webserver
_thread.start_new_thread(webserver, ())

    
EverythingOK = 5000
while True:
        
        
        now = time.localtime()
        hour = now[3]
        minute = now[4]
        #if minute < 10:
        #        minute=0.minute
        print('Time:',hour,":",minute)
        led.off()
        time.sleep_ms(EverythingOK)
        # UNCOMMENT TO STOP LOOP
        #break
    
        
# Start sensor checks!
        print("Checking Sensors..")
        #Power Sensor
        batt_sensor = ADC(28) # Pin 34 On Pico 2W
        
        PowerMultiplier=.00005646 # 3.7/65536
        
        BattSensor = batt_sensor.read_u16()
        
        if BattSensor > 60512:
            BattLevel="95%" 
        elif BattSensor > 59512:
            BattLevel="90%"
        elif BattSensor > 58802:
            BattLevel="80%"  
        elif BattSensor > 58448:
            BattLevel="70%"   
        elif BattSensor > 57917:
            BattLevel="60%" 
        elif BattSensor > 57739:
            BattLevel="50%"
        elif BattSensor > 57562:
            BattLevel="40%"  
        elif BattSensor > 57031:
            BattLevel="30%"    
        elif BattSensor > 56854:
            BattLevel="20%"
        elif BattSensor > 53490: #6023
            BattLevel="10%"
        else:
            BattLevel=0
            
        print('Battery Reading:',BattSensor,BattLevel)
        
    #Door Sensor
        #adc_pin2 = ADC(26) # Pin 31 On Pico 2W
        
        #DoorSensor = adc_pin2.read_u16()
        #if DoorSensor <= 50000:
        Door="Closed"
        #    EverythingOK = 0
        #    print('Door Open:',DoorSensor)
        #else:
        #    EverythingOK = 1000
        
        #Temp Sensor
        #ds_pin = machine.Pin(16) # Pin 21 On Pico 2W
        #ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
        
    #Power Sensor
        #power_sensor = ADC(28)
        
#        roms = ds_sensor.scan()
        #print("Found DS devices: ", roms)
#        ds_sensor.convert_temp()
#        for rom in roms:
#            temp_c = ds_sensor.read_temp(rom)
#            temp_f = ((temp_c * (9/5)) + 32)
#            print(f"Temperature: {temp_f:.2f} °F")
        
#        if temp_f >= 50:
#            EverythingOK = 0
#            print('Temp:',temp_f)
#        else:
#            EverythingOK = 1000
        
#        if EverythingOK != 1000 : EverythingOK = 200




##### No Code After This #####
           
        led.on()
        
        if EverythingOK == 5000 : print("Everything OK!")
        else:
            print("Something Wrong!")



