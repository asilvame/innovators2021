from m5stack import * 
from m5ui import *
from uiflow import *
import wifiCfg
import espnow
from m5mqtt import M5mqtt
import hat
import json
import unit
import machine
import urequests
import machine
from micropython import const
import ntptime

setScreenColor(0x111111)
macAddr = None
id_client_control = None
id_client_business = None
business_topic_p = None
business_topic_s = None
sensorData = None
mensaje = None
ssid = "WIFI_SSID"
password_wifi = "WIFI_PASS"
wifiCfg.wlan_sta.active(True)
wifiCfg.doConnect(ssid, password_wifi)

espnow.init()

while (not wifiCfg.wlan_sta.isconnected()):
    wifiCfg.doConnect(ssid, password_wifi)

ntp = ntptime.client(host='es.pool.ntp.org', timezone=1)
rtc.setTime((ntp.year()), (ntp.month()), (ntp.day()), (ntp.hour()), (ntp.minute()), (ntp.second()))

#hat_env0 = hat.get(hat.ENV)
#gps0 = unit.get(unit.GPS,unit.PORTA)
#pir0 = unit.get(unit.PIR, (21,22))
espnow.init()

label0 = M5TextBox(78, 0, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=90)
label1 = M5TextBox(61, 0, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=90)
label2 = M5TextBox(44, 0, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=90)
label3 = M5TextBox(26, 0, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=90)

macAddr = str((espnow.get_mac_addr()))
macAddr = macAddr.replace(':', '').upper()
id_client_control = macAddr
id_client_business = "b_"+id_client_control
frec=1

business_topic_p = "business/TEAM_6/ENT/server"
business_topic_s = "business/TEAM_6/ENT/device/"+id_client_business
label0.setText(str(macAddr))
label1.setText(str(id_client_business))
label3.setText('Hello GPS')
label0.setText(str(business_topic_p))
wait(3)
label0.setText('Inicio Envio')
label1.setText(str(str(macAddr)))
label3.setText('Searching for Sats')
wait(3)

m5mqtt = M5mqtt(str(id_client_business), 'iothub02.onesaitplatform.com', 8883, str(id_client_control), '<token_acesso>', 30, ssl = True)

def fun_business_c2d_(topic_data):  
  global m5mqtt,business_topic_p,gps0,macAddr,frec
  #Proceso del comando Cloud-2-Device
  label1.setText(str(topic_data))
  wait(0.2)
  jsonTopic_data=json.loads(topic_data)
  frec=jsonTopic_data["frec"]
   #Ejemplo, función de Echo del mensaje mandado
  mensaje_echo = {'deviceId':macAddr,'latitude':-1,'longitude':-1,'timestamp':ntp.formatDatetime('-', ':'),'payload':jsonTopic_data}
  wait(0.2)
  m5mqtt.publish(str(business_topic_p),json.dumps(mensaje_echo))

def fun_business_d2c_(topic_data):  
  global m5mqtt,business_topic_p
  #Proceso del comando Cloud-2-Device
  label1.setText(str(topic_data))
  m5mqtt.publish(str(business_topic_p),str((json.dumps(topic_data))))

m5mqtt.subscribe(business_topic_s, fun_business_c2d_)
m5mqtt.start()


while True:
 
    sensorData = {'hum':0,'temp':0,'press':0,'light':0}
    label2.setText(str(id_client_business))
    label3.setText(str(business_topic_p))
    mensaje = {'deviceId':macAddr,'frec':frec,'latitude':-1,'longitude':-1,'timestamp':ntp.getTimestamp()}
    mensaje.update(sensorData)
    #Proceso del envio de datos Device-2-Cloud
    fun_business_d2c_(mensaje)

    label0.setText('Publicando...')
    M5Led.on()
    wait(0.5)
    M5Led.off()
    mensaje.clear()
    sensorData.clear()
    wait(frec-0.5)
    while (not wifiCfg.wlan_sta.isconnected()):
        wifiCfg.doConnect(ssid, password_wifi)