import spi, time

status = spi.openSPI(speed=200000,device="/dev/spidev0.1")
print status

while True:
	try:
		for i in range(256):
			for j in range(1000):
				print spi.transfer((i,))
	except KeyboardInterrupt:
		spi.closeSPI()
		break