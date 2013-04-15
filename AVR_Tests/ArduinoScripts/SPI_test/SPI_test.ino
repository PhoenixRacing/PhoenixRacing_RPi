#include <SPI.h>
int num = 0;

void setup() {
  // set the SS pin as an output (i.e. configure as master) and initialize SPI
  pinMode (SS, OUTPUT);
  SPI.begin();
  
  Serial.begin(9600);
}

void loop() {
  digitalWrite(SS,LOW);
  Serial.print(num-1)
  Serial.print(": ")
  Serial.println(SPI.transfer(num++));
  digitalWrite(SS,HIGH);
  delay(200);
}
