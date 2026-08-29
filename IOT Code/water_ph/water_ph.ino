// ----------- PIN DEFINITIONS -----------
#define PH_PIN A0
#define WATER_PIN A1

// ----------- pH CALIBRATION -----------
float neutralVoltage = 1.38;
float slope = -0.1575;

void setup() {
  Serial.begin(9600);
}

void loop() {

  // ----------- pH SENSOR -----------
  int phVal = analogRead(PH_PIN);
  float phVoltage = phVal * (5.0 / 1023.0);
  float pH = 7 + ((phVoltage - neutralVoltage) / slope);

  // ----------- WATER LEVEL SENSOR -----------
  int waterVal = analogRead(WATER_PIN);
  float waterPercent = map(waterVal, 0, 1023, 0, 100);

  // ----------- SEND JSON ONLY -----------
  Serial.print("{");
  Serial.print("\"pH\":");
  Serial.print(pH, 2);
  Serial.print(",");

  Serial.print("\"water_level\":");
  Serial.print(waterPercent);

  Serial.println("}");

  delay(2000);
}
// #include <ESP8266WiFi.h>
// #include <ESP8266HTTPClient.h>

// // -------- WIFI --------
// const char* ssid = "AndroidShare_CE";
// const char* password = "58263957";

// // -------- SERVER --------
// const char* serverURL = "http://192.168.1.5:3000/data"; // CHANGE IP

// // -------- PINS --------
// #define PH_PIN A0
// #define WATER_PIN A0  // if using only one analog, else adjust

// float neutralVoltage = 1.38;
// float slope = -0.1575;

// void setup() {
//   Serial.begin(115200);

//   WiFi.begin(ssid, password);
//   Serial.print("Connecting");

//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");
//   }

//   Serial.println("\nConnected!");
// }

// void loop() {

//   // -------- READ SENSORS --------
//   int phVal = analogRead(PH_PIN);
//   float voltage = phVal * (3.3 / 1023.0);
//   float pH = 7 + ((voltage - neutralVoltage) / slope);

//   int waterVal = analogRead(WATER_PIN);
//   int waterPercent = map(waterVal, 0, 1023, 0, 100);

//   // -------- SEND DATA --------
//   if (WiFi.status() == WL_CONNECTED) {
//     WiFiClient client;
//     HTTPClient http;

//     http.begin(client, serverURL);
//     http.addHeader("Content-Type", "application/json");

//     String json = "{";
//     json += "\"pH\":" + String(pH, 2) + ",";
//     json += "\"water_level\":" + String(waterPercent) + ",";
//     json += "\"turbidity_value\":600,";
//     json += "\"turbidity_status\":2";
//     json += "}";

//     int httpResponseCode = http.POST(json);

//     Serial.print("Response: ");
//     Serial.println(httpResponseCode);

//     http.end();
//   }

//   delay(5000); // send every 5 sec
// }