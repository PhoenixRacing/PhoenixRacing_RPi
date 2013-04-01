void setup() {
  // set the SS pin as an output (i.e. configure as master) and initialize SPI
  //pinMode (10, OUTPUT);
  //SPI.begin();
  Serial.begin(9600);
}

void loop() {
  Serial.println(1);//SPI.transfer(LED_state));
  delay(1);
}
