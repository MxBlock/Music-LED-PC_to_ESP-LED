#define GREEN_PIN 5
#define RED_PIN 4
#define BLUE_PIN 0

int x;

void setup() {
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  Serial.begin(19200);
  //Serial.setTimeout(1);  // Increase the timeout value to allow for complete message reception
}

void loop() {
  if (Serial.available() > 0) {
    x = Serial.readStringUntil('\n').toInt();
  
    //Output
    //Serial.println(x);
    analogWrite(GREEN_PIN, x);
    analogWrite(RED_PIN, x);
    analogWrite(BLUE_PIN, x);
  }
}
