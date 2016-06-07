#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <mpsse.h>

int main(void)
{
	struct mpsse_context *io = NULL;
	int i = 0, retval = EXIT_FAILURE;
	int j;

	io = MPSSE(GPIO, 1, 0);
	
	if(io && io->open)
	{
		for(i=0; i<10; i++)
		{
			for (j=GPIOL0; j <= GPIOL3; j++)
			{
				PinHigh(io, j);
				printf("GPIOL%d State: %d\n", j - GPIOL0, PinState(io, j, -1));
				usleep(100000);
			
				PinLow(io, j);
				printf("GPIOL%d State: %d\n", j - GPIOL0, PinState(io, j, -1));
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
