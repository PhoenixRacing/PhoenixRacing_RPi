#include <avr/io.h>
#include <avr/interrupt.h>

/* Boolean Support */
typedef char bool;
#define true 1
#define false 0

/* Car State */
//Tach:			1 pin out 				(1 byte)
//SignalLEDs:	5 pins out				(5 bytes)
//Button:		1 pin in, 2 pins out 	(3 bytes)
//7SegDisp:		8 pins out				(12 bytes)
//
//Total: 16 pins out, 1 pin in (21 bytes)

typedef struct {
	char digits[4];
	bool colon;
	char decimal;
} sevenSegmentDisplay;

typedef struct {
	bool up;
	bool down;
	bool yellow;
	bool error;
	bool debug;
} LEDs;

typedef struct {
	char tachDisplay;
	sevenSegmentDisplay numDisplay1;
	sevenSegmentDisplay numDisplay2;
	bool button;
	bool buttonLED1;
	bool buttonLED2;
	LEDs indicators; 
} state;

/* General */
int main(void);
void setup(void);
void loop(void);

/* SPI */
void initializeSPI(void);
#define START_CHAR 0x10
#define END_CHAR 0x11

/* Tachometer */
void initializeTachSpectrum(void);
void updateTachSpectrum(void);

/* Seven Segment Display */
void initializeSSDs(void);
void updateSSDs(void);
void resetSSDCounter(void);
#define SSD_DIGIT_DIR_REG DDRD
#define SSD_DIGIT_REG PORTD
#define SSD1_DIR DDD1
#define SSD2_DIR DDD2
#define SSD3_DIR DDD3
#define SSD4_DIR DDD4
#define SSD_DIGIT PORTD1
#define SSD1 PORTD1
#define SSD2 PORTD2
#define SSD3 PORTD3
#define SSD4 PORTD4
#define SSD_ADVANCE_DIR_REG DDRD
#define SSD_ADVANCE_REG PORTD
#define SSD_ADVANCE_DIR DDD7
#define SSD_ADVANCE PORTD7
#define SSD_RESET_DIR_REG DDRD
#define SSD_RESET_REG PORTD
#define SSD_RESET_DIR DDD6
#define SSD_RESET PORTD6
#define SSD_COLON_DIR_REG DDRB
#define SSD_COLON_REG PORTB
#define SSD_COLON_DIR DDB6
#define	SSD_COLON PORTB6
#define SSD_DECIMAL_DIR_REG DDRB
#define SSD_DECIMAL_REG PORTB
#define SSD_DECIMAL_DIR DDB7
#define	SSD_DECIMAL PORTB7

/* Button */
void initializeButton(void);
void updateButton(void);
#define BUTTON_DIR_REG DDRC
#define BUTTON_REG PORTC
#define BUTTON_DIR DDC4
#define BUTTON PORTC4
#define BUTTON_PCMSK PCMSK1
#define BUTTON_PCINT PCINT12	
#define BUTTON_PCINT_vect PCINT1_vect
#define BUTTON_LIGHT_DIR_REG DDRC
#define BUTTON_LIGHT_REG PORTC
#define BUTTON_LIGHT1_DIR DDC3
#define BUTTON_LIGHT2_DIR DDC5
#define BUTTON_LIGHT1 PORTC3
#define BUTTON_LIGHT2 PORTC5

/* Indicators */
void initializeIndicators(void);
void updateIndicators(void);
#define IND_LIGHT1_DIR_REG DDRC
#define IND_LIGHT2_DIR_REG DDRC
#define IND_LIGHT3_DIR_REG DDRC
#define IND_LIGHT4_DIR_REG DDRD
#define IND_LIGHT5_DIR_REG DDRD
#define IND_LIGHT1_REG PORTC
#define IND_LIGHT2_REG PORTC
#define IND_LIGHT3_REG PORTC
#define IND_LIGHT4_REG PORTD
#define IND_LIGHT5_REG PORTD
#define IND_LIGHT1_DIR DDC0
#define IND_LIGHT2_DIR DDC1
#define IND_LIGHT3_DIR DDC2
#define IND_LIGHT4_DIR DDD5
#define IND_LIGHT5_DIR DDD0
#define IND_LIGHT1 PORTC0
#define IND_LIGHT2 PORTC1
#define IND_LIGHT3 PORTC2
#define IND_LIGHT4 PORTD5
#define IND_LIGHT5 PORTD0