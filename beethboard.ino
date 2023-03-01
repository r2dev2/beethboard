#define MIC_READ_PIN A0
#define BUFF_SIZE 256
#define BAUD 153600

int tx_head = 0;
int tx_sent = 0;
int mic_read[BUFF_SIZE] = {0};
unsigned long timestamp[BUFF_SIZE] = {0};
const int packet_size = sizeof(unsigned long) / sizeof(char) + sizeof(int) / sizeof(char);

void setup() {
	Serial.begin(BAUD);
	ADCSRA = (ADCSRA & 0xf8) | 0x04; // yea idk wtf this does it makes it fast :shrug:
}

void loop() {
	if (Serial.availableForWrite() <= 0) return;
	mic_read[tx_head] = analogRead(MIC_READ_PIN);
	timestamp[tx_head] = micros();
	Serial.write((uint8_t *) &timestamp[tx_head], sizeof(unsigned long) / sizeof(char));
	Serial.write((uint8_t *) &mic_read[tx_head], sizeof(int) / sizeof(char));
	tx_sent++;
	tx_head = (tx_head + 1) % BUFF_SIZE;
	if (tx_sent % 16 == 0) {
		tx_sent = 0;
		Serial.println();
	}
}
