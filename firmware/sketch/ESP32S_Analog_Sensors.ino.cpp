#include <Arduino.h>
#line 1 "C:\\Users\\maxmu\\AppData\\Local\\Arduino15\\RemoteSketchbook\\ArduinoCloud\\102790958244770503153\\ESP32S_Analog_Sensors\\ESP32S_Analog_Sensors.ino"
#include <WiFi.h>
#include <FS.h>
#include <LittleFS.h>

#define N_CHANNELS 15        // Number of analog channels
#define SAMPLES_PER_PACKET 5 // Samples per channel per packet
#define SAMPLE_RATE 250      // Hz

const int analogPin[N_CHANNELS] = {36, 39, 34, 32, 33, 25, 26, 27, 14, 12, 13, 4, 0, 2, 15}; // Analog input pins
const char* ssid = "Your_SSID";
const char* password = "Your@Password!";

IPAddress local_IP(192, 168, 16, 1);
IPAddress gateway(192, 168, 16, 1);
IPAddress subnet(255, 255, 255, 0);

WiFiServer server(80); // HTTP server on port 80

uint16_t sampleBuffer[N_CHANNELS][SAMPLES_PER_PACKET]; // Buffer to store samples
unsigned long lastTransmitTime = 0;
const unsigned long transmitInterval = 20; // Milliseconds

#line 23 "C:\\Users\\maxmu\\AppData\\Local\\Arduino15\\RemoteSketchbook\\ArduinoCloud\\102790958244770503153\\ESP32S_Analog_Sensors\\ESP32S_Analog_Sensors.ino"
void setup();
#line 36 "C:\\Users\\maxmu\\AppData\\Local\\Arduino15\\RemoteSketchbook\\ArduinoCloud\\102790958244770503153\\ESP32S_Analog_Sensors\\ESP32S_Analog_Sensors.ino"
void loop();
#line 65 "C:\\Users\\maxmu\\AppData\\Local\\Arduino15\\RemoteSketchbook\\ArduinoCloud\\102790958244770503153\\ESP32S_Analog_Sensors\\ESP32S_Analog_Sensors.ino"
void sendPacket(WiFiClient& client);
#line 23 "C:\\Users\\maxmu\\AppData\\Local\\Arduino15\\RemoteSketchbook\\ArduinoCloud\\102790958244770503153\\ESP32S_Analog_Sensors\\ESP32S_Analog_Sensors.ino"
void setup() {
  Serial.begin(115200);

  WiFi.softAPConfig(local_IP, gateway, subnet);
  WiFi.softAP(ssid, password);

  Serial.print("Access Point IP: ");
  Serial.println(WiFi.softAPIP());

  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected");

    while (client.connected()) {
      unsigned long currentTime = millis();

      // Collect and send data every 20 ms
      if (currentTime - lastTransmitTime >= transmitInterval) {
        lastTransmitTime = currentTime;

        // Sample data
        for (int i = 0; i < SAMPLES_PER_PACKET; i++) {
          for (int ch = 0; ch < N_CHANNELS; ch++) {
            sampleBuffer[ch][i] = analogRead(analogPin[ch]);
          }
          delayMicroseconds(1000000 / SAMPLE_RATE); // Sample at 250 Hz
        }

        // Prepare and send the packet
        sendPacket(client);
      }
    }
    client.stop();
    Serial.println("Client disconnected");
  }
}

void sendPacket(WiFiClient& client) {
  // Header:
  // - uint8_t: Number of channels
  // - uint8_t: Samples per packet
  // - uint32_t: Timestamp (ms since start)
  uint8_t header[6];
  header[0] = N_CHANNELS;
  header[1] = SAMPLES_PER_PACKET;
  uint32_t timestamp = millis();
  memcpy(&header[2], &timestamp, sizeof(timestamp));

  // Send header
  client.write(header, sizeof(header));

  // Send payload (binary samples)
  for (int i = 0; i < SAMPLES_PER_PACKET; i++) {
    for (int ch = 0; ch < N_CHANNELS; ch++) {
      client.write((uint8_t*)&sampleBuffer[ch][i], sizeof(sampleBuffer[ch][i]));
    }
  }

  Serial.println("Packet sent");
}

