//include libraries
#include <avr/io.h>
#include <avr/interrupt.h>
 
int main(void);

 int main(void){
 	// initialize the SPI as a slave with interrupts enabled
	cli();
 	DDRB = 1<<DDB4;
	SPCR |= (1 << SPE) | (1 << SPIE);
	SPDR = 12;
	sei();

	while(1);
}

ISR(SPI_STC_vect){
	//define the interrupt behavior for spi serial transfer complete
	SPDR = SPDR;
}