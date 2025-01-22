#include <DmxSimple.h>

void setup() {
  Serial.begin(9600);
  DmxSimple.usePin(3);
  DmxSimple.maxChannel(4);
}

String inputBuffer = "";

void loop() {
  // Read input value
  inputBuffer = Serial.readStringUntil('\n');

  // Extract values index
  int redIndex = inputBuffer.indexOf("r");
  int greenIndex = inputBuffer.indexOf("g");
  int blueIndex = inputBuffer.indexOf("b");
  int effectIndex = inputBuffer.indexOf("e");

  // Extract values
  int redValue = inputBuffer.substring(redIndex + 1, greenIndex).toInt();
  int greenValue = inputBuffer.substring(greenIndex + 1, blueIndex).toInt();
  int blueValue = inputBuffer.substring(blueIndex + 1, effectIndex).toInt();
  int effectValue = inputBuffer.substring(effectIndex + 1).toInt();

  // Set values
  if (inputBuffer != "") {
    DmxSimple.write(1, redValue);
    DmxSimple.write(2, greenValue);
    DmxSimple.write(3, blueValue);
    DmxSimple.write(4, effectValue);
  }
}