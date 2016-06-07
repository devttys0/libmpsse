#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <mpsse.h>

int main(void)
{
	struct mpsse_context *io = NULL;
	int retval = EXIT_FAILURE;
	int i = 0;
	int j = 0;

	io = MPSSE(BITBANG, 0, 0);

	if(io && io->open)
	{
		for(i=0; i<10; i++)
		{
			for (j=0; j<8; j++)
			{
				PinHigh(io, j);
				printf("Pin %d is: %d\n", j, PinState(io, j, -1));
				usleep(100000);

				PinLow(io, j);
				printf("Pin %d is: %d\n", j, PinState(io, j, -1));
			}
		}

		retval = EXIT_SUCCESS;
	}
	else
	{
		printf("Failed to open MPSSE: %s\n", ErrorString(io));
	}

	Close(io);

	return retval;
}
