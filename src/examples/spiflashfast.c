/*
 * Example code of using the low-latency FastRead and FastWrite functions (SPI and C only).
 * Contrast to spiflash.c.
 */

#include <stdio.h>
#include <stdlib.h>
#include <mpsse.h>

#define SIZE	0x10			// Size of SPI flash device: 1MB
#define RCMD	"\x03\x00\x00\x00"	// Standard SPI flash read command (0x03) followed by starting address (0x000000)
#define FOUT	"flash.bin"		// Output file

int main(void)
{
	FILE *fp = NULL;
	char data[SIZE] = { 0 };
	int retval = EXIT_FAILURE;
	struct mpsse_context *flash = NULL;
	
	if((flash = MPSSE(SPI0, TWELVE_MHZ, MSB)) != NULL && flash->open)
	{
		printf("%s initialized at %dHz (SPI mode 0)\n", GetDescription(flash), GetClock(flash));
		
		Start(flash);
		FastWrite(flash, RCMD, sizeof(RCMD) - 1);
		FastRead(flash, data, SIZE);
		Stop(flash);
		
		if(data)
		{
			fp = fopen(FOUT, "wb");
			if(fp)
			{
				fwrite(data, 1, SIZE, fp);
				fclose(fp);
				
				printf("Dumped %d bytes to %s\n", SIZE, FOUT);
				retval = EXIT_SUCCESS;
			}

		}
	}
	else
	{
		printf("Failed to initialize MPSSE: %s\n", ErrorString(flash));
	}

	Close(flash);

	return retval;
}
