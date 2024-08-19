#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#define GREEN_PIN 5
#define RED_PIN 4
#define BLUE_PIN 0

const char *ssid = "***";
const char *password = "***";

WiFiUDP udp;
unsigned int localPort = 80 ;

void setup() {
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }
  udp.begin(localPort);
}

void loop() {
    while (udp.parsePacket() > 0 && udp.available() > 0) {  // Check for at least one byte
      int x = udp.read();  // Read a single byte
      change_LED(x, x, x);
    }
}

void change_LED(int r, int g, int b) {
  analogWrite(RED_PIN, r);
  analogWrite(GREEN_PIN, g);
  analogWrite(BLUE_PIN, b);
}
