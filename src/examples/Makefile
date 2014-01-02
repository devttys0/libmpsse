LDFLAGS=-lmpsse

all: spiflash spiflashfast i2ceeprom ds1305 gpio bitbang

spiflash:
	$(CC) $(CFLAGS) spiflash.c -o spiflash $(LDFLAGS)

spiflashfast:
	$(CC) $(CFLAGS) spiflashfast.c -o spiflashfast $(LDFLAGS)

i2ceeprom:
	$(CC) $(CFLAGS) i2ceeprom.c -o i2ceeprom $(LDFLAGS)

ds1305:
	$(CC) $(CFLAGS) ds1305.c -o ds1305 $(LDFLAGS)

gpio:
	$(CC) $(CFLAGS) gpio.c -o gpio $(LDFLAGS)

bitbang:
	$(CC) $(CFLAGS) bitbang.c -o bitbang $(LDFLAGS)

clean:
	rm -f *.dSYM
	rm -f bitbang gpio ds1305 i2ceeprom spiflash spiflashfast

distclean: clean
