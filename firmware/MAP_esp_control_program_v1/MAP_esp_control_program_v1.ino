#include <WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>

const int MPU_addr=0x68;

int16_t Tmp;
int16_t values[6];

const char* ssid = "ESP_AP";
const char* password = "12345678";

WiFiUDP udp;
const int udpPort = 1234;

bool transmitting = false;
int transmitionStartedAt = 0;
int lastTransmissionAt = 0;

void setup() {
  Wire.begin(8, 9);
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);

  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);
  udp.begin(udpPort);


  pinMode(1, OUTPUT);
  pinMode(21, INPUT_PULLUP);
}

void loop() {
  digitalWrite(1, transmitting ? HIGH : LOW);

  if(millis() - transmitionStartedAt > 1000){
    transmitting = false;
  }

  if(digitalRead(21) == 0 && !transmitting){
    transmitionStartedAt = millis();
    transmitting = true;
  }

  Wire.beginTransmission(MPU_addr);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr,14,true);

  values[0] = Wire.read()<<8|Wire.read();    
  values[1] = Wire.read()<<8|Wire.read();
  values[2] = Wire.read()<<8|Wire.read();
  Tmp=Wire.read()<<8|Wire.read();
  values[3]=Wire.read()<<8|Wire.read();
  values[4]=Wire.read()<<8|Wire.read();
  values[5]=Wire.read()<<8|Wire.read();


  if(millis() - lastTransmissionAt >= 20){
    if(transmitting){
      udp.beginPacket("192.168.4.2", udpPort);
      udp.write((uint8_t*)values, sizeof(values));
      udp.endPacket();
    }

    lastTransmissionAt = millis();
  }
}
