LDFLAGS=-lmpsse -lftdi1
LIBFTDI1=1

all: spiflash spiflashfast i2ceeprom ds1305 gpio bitbang

spiflash:
	$(CC) $(CFLAGS) -DLIBFTDI1=$(LIBFTDI1) spiflash.c -o spiflash $(LDFLAGS)

spiflashfast:
	$(CC) $(CFLAGS) -DLIBFTDI1=$(LIBFTDI1) spiflashfast.c -o spiflashfast $(LDFLAGS)

i2ceeprom:
	$(CC) $(CFLAGS) -DLIBFTDI1=$(LIBFTDI1) i2ceeprom.c -o i2ceeprom $(LDFLAGS)

ds1305:
	$(CC) $(CFLAGS) -DLIBFTDI1=$(LIBFTDI1) ds1305.c -o ds1305 $(LDFLAGS)

gpio:
	$(CC) $(CFLAGS) -DLIBFTDI1=$(LIBFTDI1) gpio.c -o gpio $(LDFLAGS)

bitbang:
	$(CC) $(CFLAGS) -DLIBFTDI1=$(LIBFTDI1) bitbang.c -o bitbang $(LDFLAGS)

clean:
	rm -f *.dSYM
	rm -f bitbang gpio ds1305 i2ceeprom spiflash spiflashfast

distclean: clean
