#include <WiFi.h>

// Define the pins for the first set of traffic lights (main road)
const int greenPin1 = 4;
const int yellowPin1 = 2;
const int redPin1 = 15;

// Define the pins for the second set of traffic lights (by road - right side)
const int greenPin2 = 5;
const int yellowPin2 = 18;
const int redPin2 = 19;

// Define the pins for the third set of traffic lights (opposing traffic)
const int greenPin3 = 14;
const int yellowPin3 =  12;
const int redPin3 = 13;

WiFiServer server(8080); // Define the port for communication
WiFiClient client;

void setup() {
  pinMode(greenPin1, OUTPUT);
  pinMode(yellowPin1, OUTPUT);
  pinMode(redPin1, OUTPUT);
  
  pinMode(greenPin2, OUTPUT);
  pinMode(yellowPin2, OUTPUT);
  pinMode(redPin2, OUTPUT);
  
  pinMode(greenPin3, OUTPUT);
  pinMode(yellowPin3, OUTPUT);
  pinMode(redPin3, OUTPUT);
  
  Serial.begin(115200);
  
  // Connect to WiFi
  WiFi.begin("Yvan", "12345678");
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
    String sequenceRequest = request.substring(0, 3); // Extract the first 3 characters
    if (sequenceRequest == "100") {
      // Sequence 1: Main Road Green
      digitalWrite(greenPin1, HIGH);
      digitalWrite(yellowPin1, LOW);
      digitalWrite(redPin1, LOW);
      
      digitalWrite(greenPin2, LOW);
      digitalWrite(yellowPin2, LOW);
      digitalWrite(redPin2, HIGH);
      
      digitalWrite(greenPin3, LOW);
      digitalWrite(yellowPin3, LOW);
      digitalWrite(redPin3, HIGH);
      
      Serial.println("Sequence 1: Main Road Green");
    } else if (sequenceRequest == "101") {
      // Sequence 2: By Road (Right Side) Green
      digitalWrite(greenPin1, LOW);
      digitalWrite(yellowPin1, LOW);
      digitalWrite(redPin1, HIGH);
      
      digitalWrite(greenPin2, HIGH);
      digitalWrite(yellowPin2, LOW);
      digitalWrite(redPin2, LOW);
      
      digitalWrite(greenPin3, LOW);
      digitalWrite(yellowPin3, LOW);
      digitalWrite(redPin3, HIGH);
      
      Serial.println("Sequence 2: By Road (Right Side) Green");
    } else if (sequenceRequest == "102") {
      // Sequence 3: Opposing Road Green
      digitalWrite(greenPin1, LOW);
      digitalWrite(yellowPin1, LOW);
      digitalWrite(redPin1, HIGH);
      
      digitalWrite(greenPin2, LOW);
      digitalWrite(yellowPin2, LOW);
      digitalWrite(redPin2, HIGH);
      
      digitalWrite(greenPin3, HIGH);
      digitalWrite(yellowPin3, LOW);
      digitalWrite(redPin3, LOW);
      
      Serial.println("Sequence 3: Opposing Road Green");
    } else {
      // Invalid request
      Serial.println("Invalid sequence request");
    }
    
    delay(3000); // Wait for 3 seconds before processing next request
  }
}

