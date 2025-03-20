#include <WiFi.h>
#include <WiFiUdp.h>

#define GREEN_PIN 2  // Adjusted for ESP32
#define RED_PIN 15     // Adjusted for ESP32
#define BLUE_PIN 4    // Adjusted for ESP32

const char *ssid = "XXX";
const char *password = "XXX";

WiFiUDP udp;
unsigned int localPort = 80;
char packetBuffer[255];  // Buffer to store incoming UDP packets

void setup() {
  Serial.begin(115200);  // Start Serial communication
  WiFi.begin(ssid, password);
  
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  
  Serial.println("\nConnected to WiFi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());  // Print the IP address

  udp.begin(localPort);

  // Set up LED PWM channels
  ledcSetup(0, 5000, 8);  // Channel 0, 5kHz frequency, 8-bit resolution
  ledcSetup(1, 5000, 8);
  ledcSetup(2, 5000, 8);

  // Attach GPIO pins to PWM channels
  ledcAttachPin(RED_PIN, 0);
  ledcAttachPin(GREEN_PIN, 1);
  ledcAttachPin(BLUE_PIN, 2);
}

void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    int len = udp.read(packetBuffer, 254);  // Read packet
    if (len > 0) {
      packetBuffer[len] = '\0';  // Null-terminate the string
      Serial.print("Received: ");
      Serial.println(packetBuffer);
      
      int r, g, b;
      if (sscanf(packetBuffer, "%d,%d,%d", &r, &g, &b) == 3) {  // Parse values
        change_LED(r, g, b);
      }
    }
  }
}

void change_LED(int r, int g, int b) {
  ledcWrite(0, r);
  ledcWrite(1, g);
  ledcWrite(2, b);
}
