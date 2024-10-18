/*
 * Copyright (c) 2014 Eric Sandeen <sandeen@sandeen.net>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Library General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 */

/*
 * tt-status: Show status of a Triangle Tube Solo Prestige boiler via ModBus
 *
 * Usually pointed at a RS-485 serial port device, but may also query through
 * a ModBus/TCP gateway such as mbusd (http://http://mbus.sourceforge.net/)
 * 
 *
 *  Reading only Modbus Registers
 *
 *     
 */

#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <modbus/modbus.h>

#define CHECK_BIT(var,pos) ((var) & (1<<(pos)))

void usage(void)
{
	printf("Usage: tt-status [-h] [-s serial port][-i ip addr [-p port]]\n\n");
	printf("-h\tShow this help\n");
	printf("-s\tSerial Port Device for ModBus/RTU\n");
	printf("-i\tIP Address for ModBus/TCP\n");
	printf("-p\tTCP Port for ModBus/TCP (optional, default 502)\n");
	exit(1);
}

float c_to_f(float c)
{
	return ((9.0f/5.0f)*c + 32.0f);
}

struct status_bits {
	int	bit;
	char	*desc;
};

struct status_bits status[] = {
	{ 0, "PC Manual Mode" },
	{ 1, "DHW Mode" },
	{ 2, "CH Mode" },
	{ 3, "Freeze Protection Mode" },
	{ 4, "Flame Present" },
	{ 5, "CH(1) Pump" },
	{ 6, "DHW Pump" },
	{ 7, "System / CH2 Pump" }
};

int main(int argc, char **argv)
{
	int c;
	int i;
	int err = 1;
	int port = 502;		/* default ModBus/TCP port */
	char ipaddr[16] = "";	/* ModBus/TCP ip address */
	char serport[32] = "";	/* ModBus/RTU serial port */
	modbus_t *mb;		/* ModBus context */
  int16_t iregs[9];	/* Holds results of input register reads */
	int16_t hregs[9];	/* Holds results of holding register reads */

	while ((c = getopt(argc, argv, "hs:i:p:")) != -1) {
		switch (c) {
		case 'h':
			usage();
			break;
		case 's':
			strncpy(serport, optarg, sizeof(serport));
			serport[31] = '\0';
			break;
		case 'i':
			strncpy(ipaddr, optarg, sizeof(ipaddr));
			serport[31] = '\0';
			break;
		case 'p':
			port = atoi(optarg);
			break;
		default:
			usage();
		}
	}

	if (!ipaddr[0] && !serport[0]) {
		printf("Error: Must specify either ip addresss or serial port\n\n");
		usage();
	}
	if (ipaddr[0] && serport[0]) {
		printf("Error: Must specify only one of ip addresss or serial port\n\n");
		usage();
	}

	if (ipaddr[0])
		mb = modbus_new_tcp(ipaddr, port);
	else
		mb = modbus_new_rtu(serport, 38400, 'N', 8, 1);

	if (!mb) {
		perror("Error: modbus_new failed");
		goto out;
	}

/* #warning slave ID needs to be an option too */
	if (modbus_set_slave(mb, 1)) {
		perror("Error: modbus_set_slave failed");
		goto out;
	}

	if (modbus_connect(mb)) {
		perror("Error: modbus_connect failed");
		goto out;
	}


  	/* Read 7 registers from the address 0x40000 */
	if (modbus_read_registers(mb, 0x40000, 7, hregs) != 7) {
		printf("Error: Modbus read of 7 regs at addr 0x40000 failed\n");
		goto out;
	}

	/* System Supply Temp */
  printf("System Supply Temp:    %5.1f°C  %5.1f°F\n", 1.0*hregs[6]/10, c_to_f(hregs[6]/10));

  
 	/* Read 9 registers from the address 0x30003 */
	if (modbus_read_input_registers(mb, 0x30003, 9, iregs) != 9) {
		printf("Error: Modbus read input at addr 0x30003 failed\n");
		goto out;
	}
	/* System Supply Setp */
  printf("System Supply Setp:    %5.1f°C  %5.1f°F\n", 1.0*iregs[0]/2, c_to_f(iregs[0]/2));
	/* Cascade Current Power */
  printf("Cascade Current Power: %5.1f%%\n", 1.0*iregs[3]);
	/* Outlet Setp */
  printf("Outlet Setp:           %5.1f°C  %5.1f°F\n", 1.0*iregs[4]/10, c_to_f(iregs[4]/10));
	/* Outlet Temp */
  printf("Outlet Temp:           %5.1f°C  %5.1f°F\n", 1.0*iregs[5]/10, c_to_f(iregs[5]/10));
	/* Intlet Temp */
  printf("Inlet Temp:            %5.1f°C  %5.1f°F\n", 1.0*iregs[6]/10, c_to_f(iregs[6]/10));
	/* Flue Temp */
  printf("Flue Temp:             %5.1f°C  %5.1f°F\n", 1.0*iregs[7]/10, c_to_f(iregs[7]/10));
	/* Firing Rate */
  printf("Firing Rate:           %5.1f%%\n", 1.0*iregs[8]);
  
  
  printf("\n");
  printf("    +-------------+(%5.1f°C)            (%5.1f°C)\n", 1.0*iregs[4]/10, 1.0*iregs[0]/2);
  printf("    |             | %5.1f°C              %5.1f°C\n", 1.0*iregs[5]/10, 1.0*hregs[6]/10);
  printf("    |             |---------------------------->\n");
  printf("    |             |\n");
  printf("    |             |\n");  
  printf("    | Firing Rate |\n");
  printf("    |    %3.0f\%%     |\n", 1.0*iregs[8]);
  printf("    |     \\|/     | %5.1f°C\n", 1.0*iregs[6]/10);
  printf("    |             |<----------------------------\n");
  printf("    |             |\n");
  printf("    +-------------+\n");

 

        err = 0;
out:
	modbus_close(mb);
	modbus_free(mb);
	return err;
}