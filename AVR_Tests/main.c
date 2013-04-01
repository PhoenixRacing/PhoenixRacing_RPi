//include libraries
#include <avr/io.h>
#include <avr/interrupt.h>

//define missing boolean compatibility
typedef char bool;
#define true 1
#define false 0

//macros
#define START_CHAR 0x0F
#define END_CHAR 0x0E
#define BUFFER_SIZE 4

//function prototypes
int main(void);
void setup(void);
void loop(void);
void updatePeripherals(void);


static bool buttonState = false;
static char data[BUFFER_SIZE];
static int dataPos = 0;

int main(void){
	setup();

	while (true){
		loop();
	}
}

void setup(void){
	// initialize the SPI as a slave with interrupts enables
	// and clock frequency of the oscillator freq (8Mhz)/16

	SPCR = (1 << SPE) | (1 << SPR0) | (1 << SPIE);

	// setup PortD Pin0 as an output for testing purposed
	DDRD |= (1 << DDD0);		//Set PortD Pin0 as an output
	PORTD |= (1 << PORTD0);	//Set PortD Pin0 high to turn on LED
}

void loop(void){
	// code that is meant to executed each loop goes here
	updatePeripherals();
}

void updatePeripherals(void){
	int a=0;
}

ISR(SPI_STC_vect){
	//define the interrupt behavior for spi serial transfer complete
	
	switch (SPDR){
		case START_CHAR:
			dataPos = 0;
			break;
		case END_CHAR:
			updatePeripherals();
			break;
		default:
			data[dataPos] = SPDR;
	} 
}

ISR(PCINT0_vect){
	//define the behavior for a signal switch on pin PB0
	buttonState = PORTD & PORTD0;
	SPDR = buttonState;
}