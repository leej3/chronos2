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

int c_to_f(float c)
{
  return ((c * 9)/5 + 32);
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
  int16_t regs[8];	/* Holds results of register reads */
  
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
    mb = modbus_new_rtu(serport, 9600, 'E', 8, 1);
  
  if (!mb) {
    perror("Error: modbus_new failed");
    goto out;
  }
  
  if (modbus_set_slave(mb, 1)) {
    perror("Error: modbus_set_slave failed");
    goto out;
  }
  
  if (modbus_connect(mb)) {
    perror("Error: modbus_connect failed");
    goto out;
  }
  

  /* Read 2 registers from the address 0x300 */
  if (modbus_read_input_registers(mb, 0x30003, 2, regs) != 2) {
    printf("Error: Modbus read input at addr 0x300 failed\n");
    goto out;
  }
  /* Flue temp: degrees C, 8 bits */
  printf("System Supply Setp: %.1f °F\n", 2.0*regs[0]/2+32);

  /* Read 7 registers from the address 0x40000 */
  if (modbus_read_registers(mb, 0x40000, 7, regs) != 7) {
    printf("Error: Modbus read of 7 regs at addr 0x40000 failed\n");
    goto out;
  }
  
  /* Flue temp: degrees C, 8 bits */
  printf("Reg0: %d \n", regs[0]);
  printf("Reg1: %d \n", regs[1]);
  printf("Reg2: %d \n", regs[2]);
  printf("Reg3: %d \n", regs[3]);
  printf("Reg4: %d \n", regs[4]);
  printf("Reg5: %d \n", regs[5]);
  printf("System Supply Temp: %.1f °F\n", 2.0*regs[6]/10+32);
  
    

  // if (modbus_write_register(mb, 0x40000, 1) != 1) {
//	printf("Error: Modbus write of 0x40000 failed\n");
//		goto out;
//	}
	
	
//   printf("Writing Setpoint = 10 \n");
   
  //if (modbus_write_register(mb, 0x40002, 10) != 1) {
	//printf("Error: Modbus write of 0x40003 failed\n");
	//	goto out;
	//}
  
     
	 	if (modbus_read_registers(mb, 0x40000, 7, regs) != 7) {
		printf("Error: Modbus read of 7 regs at addr 0x40000 failed\n");
		goto out;
	}

	/* Flue temp: degrees C, 8 bits */
  printf("Reg0: %d \n", regs[0]);
  printf("Reg1: %d \n", regs[1]);
  printf("Reg2: %d \n", regs[2]);
  printf("Reg3: %d \n", regs[3]);
  printf("Reg4: %d \n", regs[4]);
  printf("Reg5: %d \n", regs[5]);
  printf("System Supply Temp: %.1f °F\n", (1.0*regs[6]/10)*9/5+32);
  
 	/* Read 2 registers from the address 0x300 */
//	if (modbus_read_input_registers(mb, 0x30003, 2, regs) != 2) {
//		printf("Error: Modbus read input at addr 0x300 failed\n");
//		goto out;
//	}
	/* Flue temp: degrees C, 8 bits */
  printf("System Supply Setp: %.1f °F\n", (1.0*regs[0]/2)*9/5+32);
  
 	/* Read 2 registers from the address 0x300 */
//	if (modbus_read_input_registers(mb, 0x30011, 2, regs) != 2) {
	//	printf("Error: Modbus read input at addr 0x300 failed\n");
		//goto out;
//	}
/* Read 2 registers from the address 0x300 */
	if (modbus_read_input_registers(mb, 0x30003, 9, regs) != 9) {
		printf("Error: Modbus read input at addr 0x30003 failed\n");
		goto out;
	}
/* System Supply Setp */
  printf("System Supply Setp:    %5.1f °F\n", (1.0*regs[0]/2)*9/5+32);
	/* Cascade Current Power */
  printf("Cascade Current Power: %5.1f %\n", 1.0*regs[3]);
	/* Outlet Setp */
  printf("Outlet Setp:           %5.1f °F\n", (1.0*regs[4]/10)*9/5+32);
	/* Outlet Temp */
  printf("Outlet Temp:           %5.1f °F\n", (1.0*regs[5]/10))*9/5+32;
	/* Intlet Temp */
  printf("Inlet Temp:            %5.1f °F\n", (1.0*regs[6]/10)*9/5+32);
	/* Flue Temp */
  printf("Flue Temp:             %5.1f °F\n", (1.0*regs[7]/10)*9/5+32);
	/* Firing Rate */
  printf("Firing Rate:           %5.1f %\n", 1.0*regs[8]);



        err = 0;
out:
	modbus_close(mb);
	modbus_free(mb);
	return err;
}
