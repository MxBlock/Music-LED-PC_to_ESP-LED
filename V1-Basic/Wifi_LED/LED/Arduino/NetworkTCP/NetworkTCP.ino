#include <ESP8266WiFi.h>

#define GREEN_PIN 5
#define RED_PIN 4
#define BLUE_PIN 0

const char *ssid = "microwave";
const char *password = "AllergutenDingesinddrei";

WiFiServer server(80);

void setup() {
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  Serial.begin(115200);
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }
  server.begin();
}

void loop() {
  int x;
  String message;
  WiFiClient client = server.available();
  if (client) {
    blink(4);
    while (client.connected()) {
      /*
      if (client.available()) {
        message = client.readStringUntil('\n');
        message.trim();
        x = message.toInt();
        change_LED(x, x, x);
        client.flush();
        */

        if (client.available()) {
          x = client.read();
          change_LED(x, x, x);
        }
      }
    }
  }
}

void change_LED(int x, int y, int z){
  analogWrite(GREEN_PIN, x);
  analogWrite(RED_PIN, y);
  analogWrite(BLUE_PIN, z);
}

void blink(int x) {
  for (int i = 0; i < x; i++) {
      change_LED(0, 0, 0);
      delay(250);
      change_LED(255, 255, 255);
      delay(250);
  }
}

