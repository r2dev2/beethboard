# Beethboard

I am a 18th century piano god and cannot use a computer.

https://user-images.githubusercontent.com/50760816/224879174-fd0b87ff-f30e-4ec4-baff-0aa216c6abfe.mov

## What

User plays keys on the piano and the computer detects which keys were pressed using fast fourier transforms (ffts) to determine which key to press on the computer. For example, middle c on the piano maps to the computer typing in "m".

Below graphic explains it clearly (sorry for the blinding light mode lol)

![image](https://user-images.githubusercontent.com/50760816/224879375-5ae5b2c3-9d16-4202-a41d-ba4b6e2f4514.png)

## Why

This is my Physics 4BL final project. I use arduino microphone instead of built-in microphone because we need to use arduino in project.

## Implementation

Here comes the NERRD stuff 🤓

### Arduino

1. we bypass the ADCSRA of the arduino with the line `ADCSRA = (ADCSRA & 0xf8) | 0x04;` which I have no clue why it works but it makes `analogRead()` fast af
2. the arduino reads the voltage output from the microphone and the current time in microseconds
3. if there is space remaining in the serial buffer between the arduino and computer, it sends the voltage read and the timesteamp
4. every 256 measurements sent, the arduino will send a carriage return "\r\n" to signify the end of the batch
  * if you are wondering why, it's bc I wrote the python code to loop over the lines of the serial connection and am too lazy to change
5. messages are sent at a baud rate of 2,500,500 because that's the fastest we can go (I think)

### Python

Note: we choose to batch fft by 4096 because it is an integer mulitple of the arduino's sending batch size and 4096 measurements is enough to reliably perform ffts. 

1. use pyserial to read the arduino's output
2. for each calibrated note, perform a fft on the middle batch of 4096 and extract the top 3 peaks by intensity above 50 Hz
3. add each batch of 256 that is sent from the arduino to a buffer of the last 4096 measurements from the arduino
4. perform an fft on the last 4096 measurements and compare the top 3 peaks with the top 3 peaks of each calibrated note using a weighted chi^2 deviation
  * apologies for lack of latex but gh does not want to play nice today TAT
  * chi^2 = sum for (o, e) in observed x expected of (normalized_intensity(e) + normalized_intensity(o)) * (freq(o) - freq(e))^2 / freq(e)
  * we normalize intensity by dividing the intensity by its max value
  * this formula was chosen to factor in both intensity and frequency of peaks: large peaks should contribute more to the matching and each peak should be of relatively similar intensities
5. if no peaks pass a certain threshold or if the best chi^2 isn't low enough, no note was played
6. after every interval for which a note is played, find the most common measured note played
7. type measured note

## Usage

O god why would u ever try to run this urself.

If you do tho,

```bash
export ARDUINO_BEETHBOARD_PORT="port of arduino, in my case /dev/ttyACM0"
make run # upload arduino code to arduino, depends on arduino-cli
python3 src/beethboard.py record --rdir=piano # start calibration session and save to directory `piano`
                                              # in calibration cli, type `r 1` to start recording note #1 and `s` to stop recording
                                              # note ids must be integer between 1 and 26 bc pls i haven't made this program generic yet
python3 src/beethboard.py detect --rdir=piano # start detection session with calibration from directory `piano`
python3 src/fft.py piano/1.json # visualize the fft of the calibration of note 1 of the piano calibration
```

U also need to `python3 -m pip install pyserial` along with the data science goodies like numpy and matplotlib and scipy.

## License

[Do WTF U Want](./LICENSE)

## Who

Me and mah physics 4bl lab group: Julia Melendez-Hiriart and Aubrey Anderson.

Big thanks to Arthur our overpowered TA who is goated at physics and helps us a lot.
