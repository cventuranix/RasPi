import network
import socket
import time
import urequests
import gc
import ntptime
from machine import Pin
from machine import ADC
import onewire
import machine
import ds18x20


#Power On
led = Pin("LED", Pin.OUT)
led.on()



#WiFI Info
ssid = 'Penny24'
password = 'feadfeadfe'

# Code update URL
url = "http://www.google.com"


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connection
while not wlan.isconnected():
    time.sleep(1)


NetConfig=wlan.ifconfig()
#print(NetConfig)
print('IP:', NetConfig[0])


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

# MAIN CODE STARTS HERE
EverythingOK = 1000
while True:
        now = time.localtime()
        hour = now[3]
        minute = now[4]
        #print('Time:',hour,":",minute)
        led.off()
        time.sleep_ms(EverythingOK)
        # UNCOMMENT TO STOP LOOP
        #break
    
        
##### Add Code Here #####
        # Check for code update
        if minute <= 12: #Top of hour
        # Grab code
            response = urequests.get(url)
            if response.status_code == 200:
                print("Connected to FFE....")
                print(response.status_code)
                #print(response.text)    
                response.close()
                
        
        
        print("Checking Sensors..")
        #Door Sensor
        #adc_pin2 = ADC(28)
        
        #DoorSensor = adc_pin2.read_u16()
        #if DoorSensor <= 50000:
        #    EverythingOK = 0
        #    print('Door Open:',DoorSensor)
        #else:
        #    EverythingOK = 1000
        
        #Temp Sensor
        ds_pin = machine.Pin(16)
        ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
        
        roms = ds_sensor.scan()
        #qprint("Found DS devices: ", roms)
        ds_sensor.convert_temp()
        for rom in roms:
            temp_c = ds_sensor.read_temp(rom)
            temp_f = ((temp_c * (9/5)) + 32)
            print(f"Temperature: {temp_f:.2f} °F")
        
        if temp_f >= 50:
            EverythingOK = 0
            print('Temp:',temp_f)
        else:
            EverythingOK = 1000
        
        if EverythingOK != 1000 : EverythingOK = 200
        
##### No Code After This #####
           
        led.on()
        
        if EverythingOK == 1000 : print("Everything OK!")
        else:
            print("Something Wrong!")
        
        time.sleep_ms(EverythingOK)

