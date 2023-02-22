.built: beethboard.ino
	arduino-cli compile --fqbn arduino:avr:uno beethboard.ino
	date > .built

.PHONY: build
build: .built

.PHONY: run
run: build
	arduino-cli upload -p "${ARDUINO_BEETHBOARD_PORT}" --fqbn arduino:avr:uno beethboard.ino
