#define MIC_READ_PIN A0
#define BUFF_SIZE 256

int mic_read[BUFF_SIZE] = {0};
unsigned long timestamp[BUFF_SIZE] = {0};

void setup() {
	Serial.begin(115200);
	ADCSRA = (ADCSRA & 0xf8) | 0x04; // yea idk wtf this does it makes it fast :shrug:
}

void loop() {
	for (int i = 0; i < BUFF_SIZE; ++i) {
		mic_read[i] = analogRead(MIC_READ_PIN);
		timestamp[i] = micros();
	}

	for (int i = 0; i < BUFF_SIZE; ++i) {
		Serial.write((uint8_t *) &timestamp[i], sizeof(unsigned long) / sizeof(char));
		Serial.write((uint8_t *) &mic_read[i], sizeof(int) / sizeof(char));
	}
	Serial.println();
	Serial.flush();
}
