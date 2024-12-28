#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpsse.h>
#include <time.h>
#include <unistd.h>

#define WADDR	(0xD0)	// Write start address command
#define RADDR	(0xD1)	// Read command

// Write time initialization
typedef struct {
	uint8_t i2c_addr;	// 0xD0 read address, 0xD1 write address
	uint8_t wd_addr;	// 0
	uint8_t	sec;		// reg 0
	uint8_t	min;		// reg 1
	uint8_t	hour;		// reg 2
	uint8_t	wday;		// reg 3
	uint8_t	date;		// reg 4
	uint8_t	mon;		// reg 5
	uint8_t	year;		// reg 6
	uint8_t am1_sec;	// reg 7
	uint8_t	am1_min;	// reg 8
	uint8_t	am1_hour;	// reg 9
	uint8_t am1_day_date;	// reg 10
	uint8_t am2_min;	// reg 11
	uint8_t am2_hour;	// reg 12
	uint8_t	am2_day_date;	// reg 13
	uint8_t	control;	// reg 14
	uint8_t ctrl_status;	// reg 15
	int8_t	aging_offset;	// reg 16
	int8_t	temp_msb;	// reg 17
	uint8_t	temp_lsb;	// reg 18
} t_ds3231regs;


const t_ds3231regs set_current_date(void);
volatile uint8_t run = 1;

// Signal handler function
void handle_sigint(int sig) {
	printf("Caught signal %d (Ctrl+C).\n", sig);
	run = 0;
}


int main(void)
{
	// Register the signal handler for SIGINT
	signal(SIGINT, handle_sigint);

	struct mpsse_context *ds3231 = NULL;
	
	if ((ds3231 = MPSSE(I2C, FOUR_HUNDRED_KHZ, MSB)) != NULL && ds3231->open)
	{
		printf("%s initialized at %dHz (I2C)\n", GetDescription(ds3231), GetClock(ds3231));
		printf("VID 0x%04x PID 0x%04x\n", GetVid(ds3231), GetPid(ds3231));
		
		t_ds3231regs ds3231regs = set_current_date();

		Start(ds3231);
		Write(ds3231, (char*)(&ds3231regs), sizeof(ds3231regs));
		if (GetAck(ds3231) == ACK)
		{
			printf("Initialized time on DS3231\n");
			Stop(ds3231);
			// read some timing
			while (run)
			{
				sleep(1);

				// I2C Write/Read Transaction (Write Pointer, then Read) - Slave Receive and Transmit cycle

				// set the read pointer on DS3231
				ds3231regs.i2c_addr=0xD0;
				ds3231regs.wd_addr = 0;
				Start(ds3231);
				Write(ds3231, (char *)(&ds3231regs), 2);
				if (GetAck(ds3231) == ACK)
				{
					// initialize reading
					ds3231regs.i2c_addr=0xD1;
					Start(ds3231);
					Write(ds3231, (char *)(&ds3231regs), 1);
				}
				else
				{
					printf("Failed to set the read pointer on DS3231: %s\n", ErrorString(ds3231));
					run = 0;
				}

				// read data
				if (GetAck(ds3231) == ACK)
				{
					// read all but the last byte
					SendAcks(ds3231);
					char* data = Read(ds3231, sizeof(ds3231regs)-3);
	
					/* Tell libmpsse to send NACKs after reading data */
					SendNacks(ds3231);

					/* Read one last byte, with a NACK */
					char* c = Read(ds3231, 1);
					for (int i = 0; i < sizeof(ds3231regs)-3; ++i)
					{
						printf("%02x ", (uint8_t)data[i]);
					}
					printf("%02x\n", (uint8_t)*c);
					free(data);
					free(c);
				}
				else
				{
					printf("Failed to initialize read operation on DS3231: %s\n", ErrorString(ds3231));
					run = 0;
				}
				// End I2C transaction.
				Stop(ds3231);
			}
			printf("Exiting...\n");

		}
		else
		{
			printf("Failed to initialize time on DS3231: %s\n", ErrorString(ds3231));
		}
		Stop(ds3231);

		Close(ds3231);
	}
	else
	{
		printf("Failed to initialize MPSSE: %s\n", ErrorString(ds3231));
	}

	return 0;
}


const t_ds3231regs set_current_date(void)
{
	time_t t;
	struct tm tm;

	t_ds3231regs regs;
	memset(&regs, 0, sizeof(regs));
	// repeat if second has changed while converting - try to be accurate within about a second
	do {
		t = time(NULL);
		localtime_r(&t, &tm);
		int8_t mon = tm.tm_mon + 1;
		int8_t year = tm.tm_year % 100;

		regs.i2c_addr = WADDR;
		regs.sec  = ((tm.tm_sec / 10) << 4) + (tm.tm_sec % 10);
		regs.min  = ((tm.tm_min / 10) << 4) + (tm.tm_min % 10);
		regs.hour = ((tm.tm_hour / 10) << 4) + (tm.tm_hour % 10);
		regs.wday = tm.tm_wday + 1;
		regs.date = ((tm.tm_mday / 10) << 4) + (tm.tm_mday % 10);
		regs.mon  = ((mon / 10) << 4) + (mon % 10);
		regs.year = ((year / 10) << 4) + (year % 10);
	} while (t != time(NULL));
	return regs;
}

