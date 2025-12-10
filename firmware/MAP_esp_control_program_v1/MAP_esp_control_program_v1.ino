#include <WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>

const int MPU_addr=0x68;

int16_t AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ;
int16_t values[6];

const char* ssid = "ESP_AP";
const char* password = "12345678";

WiFiUDP udp;
const int udpPort = 1234;

bool transmitting = false;
int transmitionStartedAt = 0;
int lastTransmissionAt = 0;

void setup() {
  Serial.begin(115200);

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

  if(millis() - transmitionStartedAt > 4000){
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
  AcX=Wire.read()<<8|Wire.read();    
  AcY=Wire.read()<<8|Wire.read();
  AcZ=Wire.read()<<8|Wire.read();
  Tmp=Wire.read()<<8|Wire.read();
  GyX=Wire.read()<<8|Wire.read();
  GyY=Wire.read()<<8|Wire.read();
  GyZ=Wire.read()<<8|Wire.read();

  values[0] = AcX;
  values[1] = AcY;
  values[2] = AcZ;
  values[3] = GyX;
  values[4] = GyY;
  values[5] = GyZ;


  // serialu se pak zbavit!!
  Serial.print(values[0]); Serial.print(",");
  Serial.print(values[1]); Serial.print(",");
  Serial.print(values[2]); Serial.print(",");

  Serial.print(values[3]); Serial.print(",");
  Serial.print(values[4]); Serial.print(",");
  Serial.println(values[5]);


  if(millis() - lastTransmissionAt >= 100){
    if(transmitting){
      udp.beginPacket("192.168.4.2", udpPort);
      udp.write((uint8_t*)values, sizeof(values));
      udp.endPacket();
    }

    lastTransmissionAt = millis();
  }
}
