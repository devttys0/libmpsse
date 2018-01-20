.PHONY: clean distclean
LDFLAGS=-lmpsse

# Define default CFLAGS if not given
# NOTE: You may want to adjust with local changes here
ifeq ($(CFLAGS),)
	CFLAGS=-DLIBFTDI1=1 -O0 -g3 -ggdb
endif

TARGETS=spiflash spiflashfast i2ceeprom ds1305 gpio bitbang i2cpca9685

all: $(TARGETS)

spiflash: spiflash.c
	$(CC) $(CFLAGS) spiflash.c -o spiflash $(LDFLAGS)

spiflashfast: spiflashfast.c
	$(CC) $(CFLAGS) spiflashfast.c -o spiflashfast $(LDFLAGS)

i2ceeprom: i2ceeprom.c
	$(CC) $(CFLAGS) i2ceeprom.c -o i2ceeprom $(LDFLAGS)

ds1305:
	$(CC) $(CFLAGS) ds1305.c -o ds1305 $(LDFLAGS)

gpio: gpio.c
	$(CC) $(CFLAGS) gpio.c -o gpio $(LDFLAGS)

bitbang: bitbang.c
	$(CC) $(CFLAGS) bitbang.c -o bitbang $(LDFLAGS)

clean:
	rm -f *.dSYM
	rm -f $(TARGETS)

distclean: clean
