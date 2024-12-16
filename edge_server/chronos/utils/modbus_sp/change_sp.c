/*
 * Copyright (c) 2014 Eric Sandeen <sandeen@sandeen.net>
 * Modified by Adam Thomas <code@adamthomas.us> January, 2015
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
 * change_sp: Show status of a Lochinvar Knight Boiler (WHN 285) via ModBus
 *
 * Usually pointed at a RS-485 serial port device, but may also query through
 * a ModBus/TCP gateway such as mbusd (http://http://mbus.sourceforge.net/)
 * 
 *
 *  Reading only Modbus Registers
 *
 *   To Compile:
 *  cc -o change_sp -lmodbus -lm change_sp.c
 */

#include <errno.h>
#include <math.h>
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
  printf("-t\tSetpoint (Default 85 degrees)\n");
  exit(1);
}

// Convert Celcius to Fahrenheit
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
  int sp = 85;
  int spt;
  int port = 502;	 /* default ModBus/TCP port */
  char ipaddr[16] = "";	 /* ModBus/TCP ip address */
  char serport[32] = ""; /* ModBus/RTU serial port */
  modbus_t *mb;		 /* ModBus context */
  int16_t regs[8];	 /* Holds results of register reads */
  
  while ((c = getopt(argc, argv, "hs:i:p:t:")) != -1) {
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
    case 't':

      // Note the boiler need to receive a percentage value between 0
      // and 100 which is then translated to a setpoint value based on the
      // BMS configuration paramaters: Volts at Minimum, Volts at
      // Maximum, Set Point at Minimum Volts, and Set Point at Maximum Volts
      // For our boiler these values are set at 2V, 9V, 70 degrees F,
      // and 110 degrees F, respectively.
      //
      // Refer to Lochinvar documentation for more information:
      //http://www.lochinvar.com/_linefiles/KBII-SER%20Rev%20I.pdf
      // http://www.lochinvar.com/_linefiles/SYNC-MODB%20REV%20H.pdf

      // This equation was derived emprically by fitting a line to a
      // set of percent values sent to the boiler and the resulting set points
      sp = trunc(-101.4856+1.7363171*atoi(optarg));
      spt = atoi(optarg);
      if ((sp > 100) || (sp < 0)) {
	printf("Invalid Setpoint (%i): setpoint must be between 70 and 110 degrees F\n",spt);
	  exit(1);
      }
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
  
    
  /* Read 7 registers from the address 0x40000 */
  if (modbus_read_registers(mb, 0x40000, 7, regs) != 7) {
    printf("Error: Modbus read of 7 regs at addr 0x40000 failed\n");
    goto out;
  }

  printf("Reg40001: %d \n", regs[0]);
  printf("Reg40002: %d \n", regs[1]);
  printf("Reg40003: %d \n", regs[2]);
  printf("Reg40004: %d \n", regs[3]);
  printf("Reg40005: %d \n", regs[4]);
  printf("Reg40006: %d \n", regs[5]);
    
  // Write Enable
  if (modbus_write_register(mb, 0x40000, 4) != 1) {
    printf("Error: Modbus write of 0x40001 failed\n");
    goto out;
  }
  
  printf("\nWriting Configuration = 4 \n");
  printf("Reg40001: %d \n", regs[0]);
  printf("Reg40002: %d \n", regs[1]);
  printf("Reg40003: %d \n", regs[2]);
  printf("Reg40004: %d \n", regs[3]);
  printf("Reg40005: %d \n", regs[4]);
  printf("Reg40006: %d \n", regs[5]);

  
  printf("\nWriting Setpoint = %i degree (%i percent) \n", spt,sp);
   
  if (modbus_write_register(mb, 0x40002, sp) != 1) {
    printf("Error: Modbus write of 0x40003 failed\n");
    goto out;
  }  
  
  if (modbus_read_registers(mb, 0x40000, 7, regs) != 7) {
    printf("Error: Modbus read of 7 regs at addr 0x40000 failed\n");
    goto out;
  }
  
  printf("Reg40001: %d \n", regs[0]);
  printf("Reg40002: %d \n", regs[1]);
  printf("Reg40003: %d \n", regs[2]);
  printf("Reg40004: %d \n", regs[3]);
  printf("Reg40005: %d \n", regs[4]);
  printf("Reg40006: %d \n", regs[5]);
  printf("System Supply Temp: %.1f °C\n", 1.0*regs[6]/10);
  
        err = 0;
out:
	modbus_close(mb);
	modbus_free(mb);
	return err;
}

