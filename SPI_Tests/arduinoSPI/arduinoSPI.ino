#include <SPI.h>

void setup(){
  SPI.begin();
}

void loop(){
  SPI.transfer(255);
  
}
