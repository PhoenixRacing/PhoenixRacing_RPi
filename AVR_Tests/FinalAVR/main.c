//include libraries
#include "main.h"
//#include <util/delay.h>//for debugging purposes

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
	carState.numDisplay1.digits[2]=5;
	carState.numDisplay1.digits[3]=9;
	carState.numDisplay1.colon = false;
	carState.numDisplay1.decimal = 0b00000010;

	carState.numDisplay2.digits[0]=0;
	carState.numDisplay2.digits[1]=4;
	carState.numDisplay2.digits[2]=2;
	carState.numDisplay2.digits[3]=0;
	carState.numDisplay2.colon = true;
	carState.numDisplay2.decimal = 0b00000000;

	carState.buttonLED1 = true;
	carState.buttonLED2 = true;
	cli();//disable global interrupts
	// setup PortD Pin0 as an output for testing purposes
	initializeSPI();
	initializeTachSpectrum();
	initializeSSDs();
	initializeButton();
	initializeIndicators();
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



/******
**SPI**
*******/
static int dataPos = 0;
static char* statePtrs[21] = {&(carState.tachDisplay), &(carState.numDisplay1.digits[0]),\
	&(carState.numDisplay1.digits[1]), &(carState.numDisplay1.digits[2]), &(carState.numDisplay1.digits[3]),\
	&(carState.numDisplay1.decimal), &(carState.numDisplay1.colon), &(carState.numDisplay2.digits[0]),\
	&(carState.numDisplay2.digits[1]), &(carState.numDisplay2.digits[2]), &(carState.numDisplay2.digits[3]),\
	&(carState.numDisplay2.decimal), &(carState.numDisplay2.colon), &(carState.buttonLED1),\
	&(carState.buttonLED2), &(carState.indicators.up),  &(carState.indicators.down), &(carState.indicators.yellow),\
	&(carState.indicators.error), &(carState.indicators.debug)};

void initializeSPI(void){
	//Initialize the SPI as a slave with interrupts enabled
	//and clock frequency of the oscillator freq (8Mhz)/16
	SPCR = (1 << SPE) | (1 << SPR0) | (1 << SPIE);
}

void updateCarState(char data, int position){

}

ISR(SPI_STC_vect){
	//define the interrupt behavior for spi serial transfer complete
	switch (SPDR){
		case START_CHAR:
			dataPos = 0;
			break;
		case END_CHAR:
			break;
			updateTachSpectrum();
			updateButton();
			updateIndicators();
		default:
			if (dataPos >= sizeof(statePtrs)){
				*(statePtrs[dataPos]) = SPDR;
			}
			dataPos++;
	}
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
	// setup output pins for the seven segment display
	SSD_DIGIT_DIR_REG |= (1 << SSD1_DIR) | (1 << SSD2_DIR) | (1 << SSD3_DIR) | (1 << SSD4_DIR);
	//Initialize to zero
	SSD_DIGIT_REG &= ~(0b00001111 << SSD_DIGIT);
	// setup ssd advance and reset
	SSD_ADVANCE_DIR_REG |= (1 << SSD_ADVANCE_DIR);
	SSD_RESET_DIR_REG |= (1 << SSD_RESET_DIR);
	// setup the colon pin for the ssd
	SSD_COLON_DIR_REG |= 1 << SSD_COLON_DIR;
	SSD_COLON_REG |= 1 << SSD_COLON;//initialize the colon to off
	// setup the decimal pin
	SSD_DECIMAL_DIR_REG |= 1 << SSD_DECIMAL_DIR;
	SSD_DECIMAL_REG |= 1 << SSD_DECIMAL;//initialize the decimal to off

	// Reset the counter
	resetSSDCounter();

	//setup the timer interrupt for the ssd update
	TCCR0A |= 1 << CS00; // enable timer 0
	TIMSK0 |= 1 << TOIE0;
}

void resetSSDCounter(void){
	SSD_RESET_REG |= 1 << SSD_RESET;
	SSD_RESET_REG &= ~(1 << SSD_RESET);
	ssdDigitLocation = 0;
}

void updateSSDs(void){
	//clear the digit to reduce ghosting
	SSD_DIGIT_REG |= (0b00001111 << SSD1);
	SSD_DECIMAL_REG |= 1 << SSD_DECIMAL;
	SSD_COLON_REG |= 1 << SSD_COLON;

	//update the counter and pulse the appropriate pin
	if (ssdDigitLocation < 9){
		ssdDigitLocation++;
		//pulse advance pin pin
		SSD_ADVANCE_REG |= 1 << SSD_ADVANCE;
		SSD_ADVANCE_REG &= ~(1 << SSD_ADVANCE);
	}else{
		resetSSDCounter();
	}

	//set the appropriate pins high
	if (ssdDigitLocation < 8){
		//TODO: add functionality for the decimal point

		char val;
		bool decimalOn;
		if (ssdDigitLocation < 4){
			val = carState.numDisplay1.digits[ssdDigitLocation];
			decimalOn = carState.numDisplay1.decimal & (1 << (3-ssdDigitLocation));
		}else{
			val = carState.numDisplay2.digits[ssdDigitLocation-4];
			decimalOn = carState.numDisplay2.decimal & (1 << (7-ssdDigitLocation));
		}

		char temp = SSD_DIGIT_REG;
		temp &= ((val | 0b11110000) << SSD_DIGIT) | ~(0xFF << SSD_DIGIT);//for all of the val bits that are 0
		temp |= val << SSD_DIGIT;//for all of the val bits that are 1
		PORTD = temp;

		//this is
		SSD_DECIMAL_REG &= ~((decimalOn ? 1:0) << SSD_DECIMAL);
		SSD_DECIMAL_REG |= (decimalOn ? 0:1) << SSD_DECIMAL;

	}else if (ssdDigitLocation == 8){
		//functionality for the colon
		SSD_COLON_REG |= !carState.numDisplay1.colon << SSD_COLON;
		SSD_COLON_REG &= ~(carState.numDisplay1.colon << SSD_COLON);
	}else{
		SSD_COLON_REG |= !carState.numDisplay2.colon << SSD_COLON;
		SSD_COLON_REG &= ~(carState.numDisplay2.colon << SSD_COLON);
	}
}

ISR(TIMER0_OVF_vect){
	updateSSDs();
}

/*********
**Button**
*********/
void initializeButton(void){
	//setup the button as an input and enable the interrupt on pin change
	BUTTON_DIR_REG &= ~(1 << BUTTON_DIR);
	BUTTON_PCMSK |= 1 << BUTTON_PCINT;
	//setup the button lights as outputs
	BUTTON_LIGHT_DIR_REG |= (1 << BUTTON_LIGHT1_DIR) | (1 << BUTTON_LIGHT2_DIR);
}	

void updateButton(void){
	BUTTON_LIGHT_REG |= carState.buttonLED1 << BUTTON_LIGHT1;
	BUTTON_LIGHT_REG |= carState.buttonLED2 << BUTTON_LIGHT1;
	BUTTON_LIGHT_REG &= ~(carState.buttonLED1 << BUTTON_LIGHT1);
	BUTTON_LIGHT_REG &= ~(carState.buttonLED2 << BUTTON_LIGHT1);
}

ISR(BUTTON_PCINT_vect){
	//define the behavior for a signal switch on the button pin

	//read the button state
	carState.button = BUTTON_REG && BUTTON;
	//put the button state into the SPI buffer
	SPDR = carState.button;
}

/*************
**Indicators**
*************/
void initializeIndicators(void){
	IND_LIGHT1_DIR_REG |= 1 << IND_LIGHT1_DIR;
	IND_LIGHT2_DIR_REG |= 1 << IND_LIGHT2_DIR;
	IND_LIGHT3_DIR_REG |= 1 << IND_LIGHT3_DIR;
	IND_LIGHT4_DIR_REG |= 1 << IND_LIGHT4_DIR;
	IND_LIGHT5_DIR_REG |= 1 << IND_LIGHT5_DIR;
}

void updateIndicators(void){
	IND_LIGHT1_REG |= carState.indicators.up << IND_LIGHT1;
	IND_LIGHT2_REG |= carState.indicators.down << IND_LIGHT2;
	IND_LIGHT3_REG |= carState.indicators.yellow << IND_LIGHT3;
	IND_LIGHT4_REG |= carState.indicators.error <<  IND_LIGHT4;
	IND_LIGHT5_REG |= carState.indicators.debug <<  IND_LIGHT5;
}