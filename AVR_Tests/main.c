//include libraries
#include <avr/io.h>
#include <avr/interrupt.h>

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
int main(void);
void setup(void);
void loop(void);
void updatePeripherals(void);
void initializeSSDs(void);
void updateSevenSegmentDisplays(void);
void resetSSDCounter(void);
//TODO: add functionality to change other stuff in the
//seven segment display

//declare static variables
static char data[BUFFER_SIZE];
static int dataPos = 0;
static char buttonState;
static sevenSegmentDisplay display1;
static sevenSegmentDisplay display2;

int main(void){
	setup();

	while (true){
		loop();
	}
}

void setup(void){
	//initialize variables
	display1.digits[0]=1;
	display1.digits[1]=2;
	display1.digits[2]=3;
	display1.digits[3]=4;
	display1.colon = true;

	display2.digits[0]=5;
	display2.digits[1]=6;
	display2.digits[2]=7;
	display2.digits[3]=8;
	display2.colon = false;

	cli();//disable global interrupts
	/* Initialize the SPI as a slave with interrupts enabled
	and clock frequency of the oscillator freq (8Mhz)/16 */

	SPCR = (1 << SPE) | (1 << SPR0) | (1 << SPIE);

	// setup PortD Pin0 as an output for testing purposes
	DDRD |= (1 << DDD0);		//Set PortD Pin0 as an output
	PORTD &= !(1 << PORTD0);	//Set PortD Pin0 high to turn on LED
	initializeSSDs();
	sei();//enable global interrupts
}

void loop(void){
	// code that is meant to executed each loop goes here
	updatePeripherals();
}

//the digit that is currently being updated
static char ssdDigitLocation = 0;

void updatePeripherals(void){
	int a=0;
}

void initializeSSDs(void){
	// setup PortD Pin[1:4] as output pins for the seven segment display
	DDRD |= (1 << DDD1) | (1 << DDD2) | (1 << DDD3) | (1 << DDD4);
	//Initialize to zero
	PORTD &= !((1 << PORTD1) | (1 << PORTD2) | (1 << PORTD3) | (1 << PORTD4));
	// setup PortB Pin7 as output for the ssd advance and reset
	DDRB |= (1 << DDB7) | (1 << DDB6);
	// setup the colon pin for the ssd
	DDRD |= (1 << DDD6);
	PORTD &= !(1 << PORTD6);//initialize the colon to off

	// Reset the counter
	resetSSDCounter();

	//setup the timer interrupt for the ssd update
	TCCR1B |= 1<<CS11 | 1<<CS10;	//Divide by 64
	OCR1A = 16;//15600;//6;		//Count 16 cycles for 1 millisecond interrupt
	TCCR1B |= 1<<WGM12;		//Put Timer/Counter1 in CTC mode
	TIMSK1 |= 1<<OCIE1A;		//enable timer compare interrupt

}

void resetSSDCounter(void){
	PORTB |= 1 << PORTB6;
	PORTB &= !(1 << PORTB6);
	ssdDigitLocation = 0;
}

void updateSevenSegmentDisplays(void){
	//clear the digit to reduce ghosting
	PORTD |= (0b00001111 << PORTD1);

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
		if (!(ssdDigitLocation % 2)){
			val = display1.digits[ssdDigitLocation/2];
		}else{
			val = display2.digits[ssdDigitLocation/2];
		}
		//val = ssdDigitLocation+1;
		char temp = PORTD;
		temp &= !(val << PORTD1);
		temp |= val << PORTD1;
		PORTD = temp;
	}else if (ssdDigitLocation == 8){
		//functionality for the colon
		PORTD |= display1.colon << PORTD6;
		PORTD &= !(display1.colon << PORTD6);
	}else{
		PORTD |= display2.colon << PORTD6;
		PORTD &= !(display2.colon << PORTD6);
	}
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

ISR(TIMER1_COMPA_vect){		//Interrupt Service Routine
	updateSevenSegmentDisplays();
}

/*****************************
******************************
****Seven Segment Display*****
******************************
*****************************/