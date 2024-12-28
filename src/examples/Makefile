LDFLAGS=-lmpsse

all: spiflash spiflashfast i2ceeprom ds1305 ds3231 gpio bitbang

spiflash: spiflash.c
	$(CC) $(CFLAGS) spiflash.c -o spiflash $(LDFLAGS)

spiflashfast: spiflashfast.c
	$(CC) $(CFLAGS) spiflashfast.c -o spiflashfast $(LDFLAGS)

i2ceeprom: i2ceeprom.c
	$(CC) $(CFLAGS) i2ceeprom.c -o i2ceeprom $(LDFLAGS)

ds1305: ds1305.c
	$(CC) $(CFLAGS) ds1305.c -o ds1305 $(LDFLAGS)

ds3231: ds3231.c
	$(CC) $(CFLAGS) ds3231.c -o ds3231 $(LDFLAGS)

gpio: gpio.c
	$(CC) $(CFLAGS) gpio.c -o gpio $(LDFLAGS)

bitbang: bitbang.c
	$(CC) $(CFLAGS) bitbang.c -o bitbang $(LDFLAGS)

clean:
	rm -f *.dSYM
	rm -f bitbang gpio ds1305 ds3231 i2ceeprom spiflash spiflashfast

distclean: clean
