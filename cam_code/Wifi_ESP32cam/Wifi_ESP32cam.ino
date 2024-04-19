#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>

const char* WIFI_SSID[] = { "Yvan", "Amar", "D4 of LVT 2"}; // Array of WiFi SSIDs
const char* WIFI_PASS[] = { "12345678", "12345678", "LuKeAnItA@4756#*"}; // Array of corresponding WiFi passwords
const int NUM_WIFI_NETWORKS = 3; // Number of WiFi networks

WebServer server(80);

static auto loRes = esp32cam::Resolution::find(320, 240);
static auto hiRes = esp32cam::Resolution::find(800, 600); //high resolution
//static auto hiRes = esp32cam::Resolution::find(640, 480);

void serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("Capture Fail");
    server.send(503, "", "");
    return;
  }

  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void handleJpgLo()
{
  if (!esp32cam::Camera.changeResolution(loRes)) {
    Serial.println("SET-LO-RES FAIL");
  }
  serveJpg();
}

void handleJpgHi()
{
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}

void setup()
{
  Serial.begin(115200);
  Serial.println();

  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);

  // Connect to one of the WiFi networks
  bool connected = false;
  for (int i = 0; i < NUM_WIFI_NETWORKS; i++) {
    WiFi.begin(WIFI_SSID[i], WIFI_PASS[i]);
    Serial.printf("Attempting to connect to %s...\n", WIFI_SSID[i]);

    int attempts = 0;
    while (!connected && attempts < 20) { // Try to connect for up to 10 seconds
      delay(500);
      if (WiFi.status() == WL_CONNECTED) {
        connected = true;
        break;
      }
      attempts++;
    }

    if (connected) {
      Serial.println("Connected to WiFi!");
      break;
    } else {
      Serial.println("Connection failed.");
    }
  }

  if (!connected) {
    Serial.println("Unable to connect to any WiFi network.");
    return;
  }

  Serial.print("http://");
  Serial.print(WiFi.localIP());
  Serial.println("/cam-lo.jpg");
  Serial.print("http://");
  Serial.print(WiFi.localIP());
  Serial.println("/cam-hi.jpg");
  server.on("/cam-lo.jpg", handleJpgLo);
  server.on("/cam-hi.jpg", handleJpgHi);
  server.begin();
}

void loop()
{
  server.handleClient();
}