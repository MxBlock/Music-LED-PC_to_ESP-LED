#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#define GREEN_PIN 12
#define RED_PIN 14
#define BLUE_PIN 13

const char *ssid = "microwave";
const char *password = "AllergutenDingesinddrei";

WiFiUDP udp;
unsigned int localPort = 80 ;

void setup() {
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  //Serial.begin(115200);
  blink(8, 50);
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }
  blink(4, 250);
  udp.begin(localPort);
  //Serial.println(WiFi.localIP());

}

void loop() {
  while (udp.parsePacket() > 0 && udp.available() > 0) {  // Check for at least one byte
    char packetBuffer[255]; // Buffer to hold incoming packet
    int len = udp.read(packetBuffer, 255); // Read the packet into buffer
    if (len > 0) {
      packetBuffer[len] = 0; // Null-terminate the string
      // Parse the comma-separated integers
      int r, g, b;
      sscanf(packetBuffer, "%d,%d,%d", &r, &g, &b);
      change_LED(r, g, b);
      //Serial.println(String(r) + "\t" + String(g) + "\t" + String(b));
    }
  }
}

void change_LED(int r, int g, int b) {
  analogWrite(RED_PIN, r);
  analogWrite(GREEN_PIN, g);
  analogWrite(BLUE_PIN, b);
}

void blink(int x, int time) {
  for (int i = 0; i < x; i++) {
    change_LED(0, 0, 0);
    delay(time);
    change_LED(255, 255, 255);
    delay(time);
  }
}
