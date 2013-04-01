//include libraries
#include <avr/io.h>
#include <avr/interrupt.h>
 
int main(void);
static char lastByte = 0;

 int main(void){
 	// initialize the SPI as a slave with interrupts enables
	// and clock frequency of the oscillator freq (8Mhz)/16

	SPCR = (1 << SPE) | (1 << SPR0) | (1 << SPIE);

	while(1);
}

ISR(SPI_STC_vect){
	//define the interrupt behavior for spi serial transfer complete
	SPDR = lastByte;
	lastByte = SPDR;
}