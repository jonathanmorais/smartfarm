#include <SPI.h>
#include <Ethernet.h>

// Configuração de rede
byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
char server[] = "192.168.1.100"; // IP do seu servidor
int serverPort = 5000;

// Pinos do sensor
int pinvcc = 10;
int reading = A0;
int reading2 = 7;

EthernetClient client;

void setup() {
  Serial.begin(9600);
  
  // Configura sensor
  pinMode(pinvcc, OUTPUT);
  pinMode(reading2, INPUT);
  digitalWrite(pinvcc, HIGH);
  
  Serial.println("Inicializando Ethernet...");
  
  if (Ethernet.begin(mac) == 0) {
    Serial.println("❌ Falha no DHCP");
    return;
  }
  
  Serial.print("✅ Arduino IP: ");
  Serial.println(Ethernet.localIP());
  delay(2000);
}

void loop() {
  // Lê sensores
  int umidade = analogRead(reading);
  int umidade2 = digitalRead(reading2);
  
  delay(500);
  digitalWrite(pinvcc, LOW);
  
  // Mostra no Serial
  Serial.print("Umidade (%): ");
  Serial.println(umidade);
  Serial.print("Umidade Bool: ");
  Serial.println(umidade2);
  
  // Envia para API
  enviarParaAPI(umidade, umidade2);
  
  delay(250);
  digitalWrite(pinvcc, HIGH);
  delay(10000); // Envia a cada 10 segundos
}

void enviarParaAPI(int analogica, int digital) {
  Serial.print("📡 Enviando... ");
  
  if (client.connect(server, serverPort)) {
    
    // Monta JSON
    String json = "{";
    json += "\"umidade_analogica\":" + String(analogica) + ",";
    json += "\"umidade_digital\":" + String(digital) + ",";
    json += "\"device_id\":\"arduino_eth\"";
    json += "}";
    
    // HTTP POST
    client.println("POST /sensor HTTP/1.1");
    client.print("Host: ");
    client.println(server);
    client.println("Content-Type: application/json");
    client.print("Content-Length: ");
    client.println(json.length());
    client.println("Connection: close");
    client.println();
    client.println(json);
    
    // Aguarda resposta
    delay(1000);
    
    // Verifica se deu certo
    bool sucesso = false;
    while (client.available()) {
      String line = client.readStringUntil('\n');
      if (line.indexOf("\"success\":true") != -1) {
        sucesso = true;
      }
    }
    
    client.stop();
    Serial.println(sucesso ? "✅" : "❌");
    
  } else {
    Serial.println("❌ Conexão falhou");
  }
}