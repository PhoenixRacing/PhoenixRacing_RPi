//include libraries
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>//for debugging purposes

//define missing boolean compatibility
typedef char bool;
#define true 1
#define false 0

//macros
//TODO: change these characters to bytes that can actually be reserved
//		must be greater than 99
#define START_CHAR 0x0F
#define END_CHAR 0x0E
#define BUFFER_SIZE 13

/*
Tach:		1 pin out 				(1 byte)
SignalLEDs:	2 pins out				(2 bytes)
Button:		1 pin in, 2 pins out 	(2 bytes)
7SegDisp:	9 pins out				(8 bytes)

Total: 14 pins out, 1 pin in (13 bytes)
*/

//typedefs
typedef struct {
	char digits[4];
	bool colon;
	char decimal;
} sevenSegmentDisplay;

typedef struct {
	bool left;
	bool right;
} LEDs;

typedef struct {
	bool button;
	bool buttonLED;
	sevenSegmentDisplay numDisplay1;
	sevenSegmentDisplay numDisplay2;
	char tachDisplay;
	LEDs indicators;
} state;

//function prototypes
//general
int main(void);
void setup(void);
void loop(void);
//tach spectrum
void initializeTachSpectrum(void);
void updateTachSpectrum(void);
//SSDs
void initializeSSDs(void);
void updateSSDs(void);
void resetSSDCounter(void);
//TODO: add functionality to change decimals in the seven segment display

//declare static variables
static const tachSpectrumMap[10] = {2,7,9,11,13,15,16,17,18,19};
static state carState;

int main(void){
	setup();

	while (true){
		loop();
	}
}

void setup(void){
	//initialize variables
	//testing values
	carState.numDisplay1.digits[0]=1;
	carState.numDisplay1.digits[1]=2;
	carState.numDisplay1.digits[2]=3;
	carState.numDisplay1.digits[3]=4;
	carState.numDisplay1.colon = false;
	carState.numDisplay1.decimal = 0b00000010;

	carState.numDisplay2.digits[0]=0;
	carState.numDisplay2.digits[1]=4;
	carState.numDisplay2.digits[2]=2;
	carState.numDisplay2.digits[3]=0;
	carState.numDisplay2.colon = true;
	carState.numDisplay2.decimal = 0b00000000;
	/*
 	char test = ~((carState.numDisplay1.decimal & 0b00000010 ? 1:0) << PORTD7);

	carState.numDisplay1.digits[3] = (test & 0b00010000) ? 1:0;
	carState.numDisplay1.digits[2] = (test & 0b00100000) ? 1:0;
	carState.numDisplay1.digits[1] = (test & 0b01000000) ? 1:0;
	carState.numDisplay1.digits[0] = (test & 0b10000000) ? 1:0;

	carState.numDisplay2.digits[3] = (test & 0b00000001) ? 1:0;
	carState.numDisplay2.digits[2] = (test & 0b00000010) ? 1:0;
	carState.numDisplay2.digits[1] = (test & 0b00000100) ? 1:0;
	carState.numDisplay2.digits[0] = (test & 0b00001000) ? 1:0;
	*/
	cli();//disable global interrupts

	/* Initialize the SPI as a slave with interrupts enabled
	and clock frequency of the oscillator freq (8Mhz)/16 */
	SPCR = (1 << SPE) | (1 << SPR0) | (1 << SPIE);

	// setup PortD Pin0 as an output for testing purposes
	DDRD |= (1 << DDD0);		//Set PortD Pin0 as an output
	PORTD &= !(1 << PORTD0);	//Set PortD Pin0 high to turn on LED
	initializeSSDs();
	initializeTachSpectrum();
	sei();//enable global interrupts
}

void loop(void){
	// code that is meant to executed each loop goes here
	/*
	//Test the tach display and the SSDs
	int i;
	for (i=0; i<11; i++){
		carState.tachDisplay = i;
		carState.numDisplay1.digits[3]=i%10;
		carState.numDisplay1.digits[2]=(i%100)/10;
		_delay_ms(500);
	}
	*/

}

//to be updated at consistent intervals
ISR(TIMER0_OVF_vect){
	updateSSDs();
	updateTachSpectrum();
}

/****************
**Tach Spectrum**
*****************/
void initializeTachSpectrum(void){

	//configure OC1A (PB1) as an output for PWM in non-inverted mode
	DDRB |= 1 << DDB1;
	TCCR1A |= 1 << COM1A1;

	//put timer 1 in fast PWM mode with TOP at ICR1 and compare at OCR1A
	TCCR1A |= (1 << WGM11);
	TCCR1B |= (1 << WGM12) | (1 << WGM13);

	//Period is 40 clock cycles
	ICR1 = 40;
	OCR1A = 0;

	//start the clock with no prescalar
	TCCR1B |= 1 << CS10;
}

inline void updateTachSpectrum(void){
	OCR1A = tachSpectrumMap[carState.tachDisplay-1];
}


/*************************
**Seven Segment Displays**
*************************/

//the digit that is currently being updated
static char ssdDigitLocation = 0;

void initializeSSDs(void){
	// setup PortD Pin[1:4] as output pins for the seven segment display
	DDRD |= (1 << DDD1) | (1 << DDD2) | (1 << DDD3) | (1 << DDD4);
	//Initialize to zero
	PORTD &= ~((1 << PORTD1) | (1 << PORTD2) | (1 << PORTD3) | (1 << PORTD4));
	// setup PortB Pin7 as output for the ssd advance and reset
	DDRB |= (1 << DDB7) | (1 << DDB6);
	// setup the colon pin for the ssd
	DDRD |= 1 << DDD6;
	PORTD |= 1 << PORTD6;//initialize the colon to off
	// setup the decimal pin
	DDRD |= 1 << DDD7;
	PORTD |= 1 << PORTD7;//initialize the decimal to off

	// Reset the counter
	resetSSDCounter();

	//setup the timer interrupt for the ssd update
	TCCR0A |= 1 << CS00; // enable timer 0
	TIMSK0 |= 1 << TOIE0;
}

void resetSSDCounter(void){
	PORTB |= 1 << PORTB6;
	PORTB &= ~(1 << PORTB6);
	ssdDigitLocation = 0;
}

void updateSSDs(void){
	//clear the digit to reduce ghosting
	PORTD |= (0b00001111 << PORTD1);
	PORTD |= 1 << PORTD6;
	PORTD |= 1 << PORTD7;

	//update the counter and pulse the appropriate pin
	if (ssdDigitLocation < 9){
		ssdDigitLocation++;
		//pulse pin 7
		PORTB |= 1 << PORTB7;
		PORTB = !(1 << PORTB7);
	}else{
		resetSSDCounter();
	}

	//set the appropriate pins high
	if (ssdDigitLocation < 8){
		//TODO: add functionality for the decimal point

		char val;
		bool on;
		if (ssdDigitLocation < 4){
			val = carState.numDisplay1.digits[ssdDigitLocation];
			on = carState.numDisplay1.decimal & (1 << (3-ssdDigitLocation));
		}else{
			val = carState.numDisplay2.digits[ssdDigitLocation-4];
			on = carState.numDisplay2.decimal & (1 << (7-ssdDigitLocation));
		}

		char temp = PORTD;
		temp &= ((val | 0b11110000) << PORTD1) | ~(0xFF << PORTD1);//for all of the val bits that are 0
		temp |= val << PORTD1;//for all of the val bits that are 1
		PORTD = temp;



		PORTD &= ~((on ? 1:0) << PORTD7);
		PORTD |= (on ? 0:1) << PORTD7;

	}else if (ssdDigitLocation == 8){
		//functionality for the colon

		//PORTD |= 1 << PORTD6;
		//PORTD &= ~((1 ? 0:1) << PORTD6);
		PORTD |= !carState.numDisplay1.colon << PORTD6;
		PORTD &= ~(carState.numDisplay1.colon << PORTD6);
	}else{
		PORTD |= !carState.numDisplay2.colon << PORTD6;
		PORTD &= ~(carState.numDisplay2.colon << PORTD6);
	}
}

/******
**SPI**
******/
static char data[BUFFER_SIZE];
static int dataPos = 0;
ISR(SPI_STC_vect){
	//define the interrupt behavior for spi serial transfer complete
	
	switch (SPDR){
		case START_CHAR:
			dataPos = 0;
			break;
		case END_CHAR:
			break;
		default:
			data[dataPos] = SPDR;
	} 
}

/*********
**Button**
*********/
ISR(PCINT0_vect){
	//define the behavior for a signal switch on pin PB0

	//read the button state
	carState.button = PORTD & PORTD0;
	//put the button state into the SPI buffer
	SPDR = carState.button;
}