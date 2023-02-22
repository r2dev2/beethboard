#define MIC_READ_PIN A0

int mic_read = 0;
unsigned long timestamp = 0;

void setup() {
	Serial.begin(9600);
}

void loop() {
	mic_read = analogRead(MIC_READ_PIN);
	timestamp = millis();
	Serial.print(timestamp);
	Serial.print(",");
	Serial.println(mic_read);
}
