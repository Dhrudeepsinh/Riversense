// #include <ESP8266WiFi.h>
// #include <ESP8266HTTPClient.h>
// #include <TinyGPS++.h>

// const char* ssid = "AndroidShare_CE";
// const char* password = "58263957";

// const char* serverName = "http://192.168.157.122:3000/data";

// TinyGPSPlus gps;

// // Use Serial for GPS RX
// #define GPS_RX D7


// void setup() {
//   Serial.begin(115200);

//   // Set D7 as input for GPS
//   pinMode(GPS_RX, INPUT);

//   WiFi.begin(ssid, password);
//   Serial.print("Connecting");

//   while (WiFi.status() != WL_CONNECTED) {
//     delay(1000);
//     Serial.print(".");
//   }

//   Serial.println("\nConnected!");
// }

// void loop() {

//   // 🔥 MANUAL GPS READ (stable trick)
//   while (digitalRead(GPS_RX)) {
//     gps.encode(digitalRead(GPS_RX));
//   }

//   // Debug GPS status
//   if (gps.location.isUpdated()) {
//     Serial.print("Lat: ");
//     Serial.println(gps.location.lat(), 6);
//     Serial.print("Lng: ");
//     Serial.println(gps.location.lng(), 6);
//   } else {
//     Serial.println("Waiting for GPS signal...");
//   }

//   if (WiFi.status() == WL_CONNECTED) {

//     WiFiClient client;
//     HTTPClient http;

//     int turbidityValue = analogRead(A0);
//     int turbidityStatus = (turbidityValue < 350) ? 1 : 0;

//     float latitude = gps.location.isValid() ? gps.location.lat() : 0.0;
//     float longitude = gps.location.isValid() ? gps.location.lng() : 0.0;

//     http.begin(client, serverName);
//     http.addHeader("Content-Type", "application/json");

//     String jsonData = "{";
//     jsonData += "\"turbidity_value\":" + String(turbidityValue) + ",";
//     jsonData += "\"turbidity_status\":" + String(turbidityStatus) + ",";
//     jsonData += "\"latitude\":" + String(latitude, 6) + ",";
//     jsonData += "\"longitude\":" + String(longitude, 6);
//     jsonData += "}";

//     int httpResponseCode = http.POST(jsonData);

//     Serial.print("HTTP Response: ");
//     Serial.println(httpResponseCode);
//   }

//   delay(5000);
// }

// }


#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "Galaxy F34 5G EA6C";
const char* password = "rjpanchal";

const char* serverName = "http://192.168.157.122:3000/data";

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  WiFi.begin(ssid, password);
  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\n✅ WiFi Connected!");
}

void loop() {
  int turbidityValue = analogRead(A0);
  int turbidityStatus = (turbidityValue < 350) ? 1 : 0;

  Serial.print("Turbidity: ");
  Serial.print(turbidityValue);
  Serial.print(" | Status: ");
  Serial.println(turbidityStatus);

  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    
    http.begin(client, serverName);
    http.addHeader("Content-Type", "application/json");

    String jsonData = "{\"turbidity_value\":" + String(turbidityValue) + 
                      ",\"turbidity_status\":" + String(turbidityStatus) + "}";

    int httpCode = http.POST(jsonData);
    
    Serial.print("HTTP Response: ");
    Serial.println(httpCode);
    
    http.end();
  }

  delay(5000);
}