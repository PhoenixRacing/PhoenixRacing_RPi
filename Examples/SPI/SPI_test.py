import spi, time

OFF = 0
GREEN = 1
RED = 2

status = spi.openSPI(speed=200000,device="/dev/spidev0.1")
start = (0x10,)
tach = (10,)
digits1 = (1,1,1,1)
decimal1 = (0b00000010,)
colon1 = (1,)
digits2 = (1,1,1,1)
decimal2 = (0b00000010,)
colon2 = (1,)
buttonLights = (GREEN,)
indicators = (1,1,1,1,1)
end = (0x11,)

message = start + tach + digits1 + decimal1 + colon1 + digits2 + decimal2 + colon2 + buttonLights + indicators + end

for b in message:
	spi.transfer((b,))

spi.closeSPI()
