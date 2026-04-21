#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

/************ DEVICE ************/
#define DEVICE_ID "esp32_cc_01"

/************ WIFI ************/
const char* ssid     = "vivo";
const char* password = "deepak123";

/************ BACKEND ************/
#define RAW_URL "http://10.95.52.200:8000/api/ingest/raw"

/************ PINS ************/
#define TRIG_PIN   25
#define ECHO_PIN   33
#define DHT_PIN    21

#define DHT_TYPE DHT11
DHT dht(DHT_PIN, DHT_TYPE);

/************ TIMING ************/
unsigned long lastSample = 0;

/************ ULTRASONIC ************/
float readDistanceCM(){
  digitalWrite(TRIG_PIN,LOW); delayMicroseconds(2);
  digitalWrite(TRIG_PIN,HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN,LOW);
  long d = pulseIn(ECHO_PIN,HIGH,30000);
  if(d==0) return -1;
  return d*0.034/2;
}

int getDoorState(){
  float dist = readDistanceCM();
  if(dist >= 12 && dist <= 18) return 0;   // CLOSED
  if(dist >= 25) return 1;                 // OPEN
  return 1;
}

/************ SEND DATA ************/
void sendRaw(float t, float h, int d){
  if(WiFi.status()!=WL_CONNECTED) return;

  HTTPClient http;
  http.begin(RAW_URL);
  http.addHeader("Content-Type", "application/json");

  String body = "{";
  body += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
  body += "\"temperature\":" + String(t,2) + ",";
  body += "\"humidity\":" + String(h,2) + ",";
  body += "\"door\":" + String(d);
  body += "}";

  int code = http.POST(body);

  Serial.print("HTTP Response: ");
  Serial.println(code);

  String response = http.getString();
  Serial.println(response);

  http.end();
}

/************ SETUP ************/
void setup(){
  Serial.begin(115200);

  pinMode(TRIG_PIN,OUTPUT);
  pinMode(ECHO_PIN,INPUT);

  dht.begin();

  WiFi.begin(ssid,password);
  while(WiFi.status()!=WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
}

/************ LOOP ************/
void loop(){

  // read every 2 seconds
  if(millis()-lastSample >= 2000){
    lastSample = millis();

    float t = dht.readTemperature();
    float h = dht.readHumidity();
    int d = getDoorState();

    if (isnan(t) || isnan(h)){
      Serial.println("Sensor error");
      return;
    }

    Serial.printf("T=%.2f H=%.2f D=%d\n", t, h, d);

    sendRaw(t, h, d);
  }
}