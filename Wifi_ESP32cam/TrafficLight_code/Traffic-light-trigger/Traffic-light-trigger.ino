#include <WiFi.h>

// Define the pins for the first set of traffic lights
const int greenPin1 = 4;
const int yellowPin1 = 2;
const int redPin1 = 15;

// Define the pins for the second set of traffic lights
const int greenPin2 = 14;
const int yellowPin2 = 12;
const int redPin2 = 13;

WiFiServer server(8080); // Define the port for communication
WiFiClient client;

void setup() {
  pinMode(greenPin1, OUTPUT);
  pinMode(yellowPin1, OUTPUT);
  pinMode(redPin1, OUTPUT);
  
  pinMode(greenPin2, OUTPUT);

  pinMode(yellowPin2, OUTPUT);
  pinMode(redPin2, OUTPUT);
  
  Serial.begin(115200);
  
  // Connect to WiFi
   WiFi.begin("D4 of LVT 2", "LuKeAnItA@4756#*");
  //WiFi.begin("Yvan", "12345678");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  // Start the server
  server.begin();
  
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Check if a client has connected
  if (!client.connected()) {
    client = server.available();
  }
  if (client) {
    Serial.println("New client connected");
    
    // Read the request
    String request = client.readStringUntil('\r');
    Serial.println(request);
    
    // Process the request
    if (request.indexOf("1") != -1) {
      // Turn on the green light for the first set, and red light for the second set
      digitalWrite(greenPin1, HIGH);
      digitalWrite(yellowPin1, LOW);
      digitalWrite(redPin1, LOW);
      
      digitalWrite(greenPin2, LOW);
      digitalWrite(yellowPin2, LOW);
      digitalWrite(redPin2, HIGH);
      
      Serial.println("Green light turned on for Set 1, and Red light turned on for Set 2.");
      delay(3000); // Wait for 3 seconds
    } else if (request.indexOf("0") != -1) {
      // Turn on the red light for the first set, and green light for the second set
      digitalWrite(greenPin1, LOW);
      digitalWrite(yellowPin1, LOW);
      digitalWrite(redPin1, HIGH);
      
      digitalWrite(greenPin2, HIGH);
      digitalWrite(yellowPin2, LOW);
      digitalWrite(redPin2, LOW);
      
      Serial.println("Red light turned on for Set 1, and Green light turned on for Set 2.");
      delay(3000); // Wait for 3 seconds
    }
  }
}
