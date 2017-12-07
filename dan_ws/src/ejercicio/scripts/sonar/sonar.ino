/*
* Ultrasonic Sensor HC-SR04 and Arduino Tutorial
*
* Crated by Dejan Nedelkovski,
* www.HowToMechatronics.com
* Modified by BlackZafiro.
*/

// defines pins numbers
const int NUM_SONARES = 6;  // Number of sonars to be connected to Arduino, ca be up to 6.
const int FIRST_PIN = 2;    // trigPin = 2, echoPin = 3 and so on
const float SOUND_SPEED = 0.034;   // Speed of sound in cm/microsecond

void setup() {
  for (int i = FIRST_PIN; i < NUM_SONARES * 2 + FIRST_PIN; i += 2) {
    pinMode(i, OUTPUT);     // Sets the __trigPin__ as an Output
    pinMode(i + 1, INPUT);  // Sets the __echoPin__ as an Input
  }
  Serial.begin(9600); // Starts the serial communication
}

/** Returns distance in cm. */
int readSonar(int numSonar) {
  long duration;
  int distance;
  
  int trigPin = FIRST_PIN + (numSonar * 2);
  int echoPin = trigPin + 1;

  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance = duration * SOUND_SPEED / 2.0;
  return distance;
}

void loop() {
  for(int i = 0; i < NUM_SONARES; i++) {
    // Prints the distance on the Serial Monitor
    if(i != 0){
      Serial.print("|");
    }
    Serial.print(readSonar(i));
  }
    Serial.println("|");
}
