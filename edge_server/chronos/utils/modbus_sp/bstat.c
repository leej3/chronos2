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
 * bstat: Show status of a Lochinvar Knight Boiler (WHN 285) via ModBus
 *
 * Usually pointed at a RS-485 serial port device, but may also query through
 * a ModBus/TCP gateway such as mbusd (http://http://mbus.sourceforge.net/)
 * 
 *
 * To compile:
 *     cc -o bstat -lmodbus -lm bstat.c
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
  printf("Usage: $0 [-h] [-s serial port][-i ip addr [-p port]]\n\n");
  printf("-h\tShow this help\n");
  printf("-s\tSerial Port Device for ModBus/RTU\n");
  printf("-i\tIP Address for ModBus/TCP\n");
  printf("-p\tTCP Port for ModBus/TCP (optional, default 502)\n");
  exit(1);
}

// Convert Celcius to Fahrenheit
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
  FILE *ifp;
  int spVal;
  
  
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
    // These are the current communication parameters for this boiler
    // Change for other boilers
    mb = modbus_new_rtu(serport, 9600, 'E', 8, 1);
  
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
  printf("System Supply Temp:    %5.1f°F\n", c_to_f(1.0*hregs[6]/10));
  
  
  /* Read 9 registers from the address 0x30003 */
  if (modbus_read_input_registers(mb, 0x30003, 9, iregs) != 9) {
    printf("Error: Modbus read input at addr 0x30003 failed\n");
    goto out;
  }
  /* System Supply Setp */
  // Can't Read this
  //  printf("System Supply Setp:    %5.1f°C  %5.1f°F\n", 1.0*iregs[0]/2, c_to_f(iregs[0]/2));
  /* Outlet Setp */
  // Can't read this
  //  printf("Outlet Setp:           %5.1f°C  %5.1f°F\n", 1.0*iregs[4]/10, c_to_f(iregs[4]/10));
  /* Outlet Temp */
  printf("Outlet Temp:           %5.1f°F\n", c_to_f(1.0*iregs[5]/10));
  /* Intlet Temp */
  printf("Inlet Temp:            %5.1f°F\n", c_to_f(1.0*iregs[6]/10));
  /* Flue Temp */
  printf("Flue Temp:             %5.1f°F\n", c_to_f(1.0*iregs[7]/10));
  /* Cascade Current Power */
  printf("Cascade Current Power: %5.1f%%\n", 1.0*iregs[3]);
  /* Firing Rate */
  printf("Lead Firing Rate       %5.1f%%\n", 1.0*iregs[8]);

  ifp = fopen("/home/rj/sp.txt", "r");
  if (ifp == NULL) {
    printf("Can't open input file /home/rj/sp.txt \n");
    goto out;
  }  
  while (fscanf(ifp, "%d", &spVal) != EOF) {
    //        printf("Val", spVal);
        printf("");
  }  

  fclose(ifp);
  printf("Last Setpoint sent:     %d  °F\n", spVal); 

  printf("\n");
  printf("    +-------------+\n");
  printf("    |             | %5.1f°F             %5.1f°F\n", c_to_f(1.0*iregs[5]/10), c_to_f(1.0*hregs[6]/10));
  printf("    |Cascade Fire |---------------------------->\n");
  printf("    |   %3.0f\%%      |\n",1.0*iregs[3]);
  printf("    |             |\n");  
  printf("    | Lead Fire   |\n");
  printf("    |    %3.0f\%%     |\n", 1.0*iregs[8]);
  printf("    |             | %5.1f°F\n", c_to_f(1.0*iregs[6]/10));
  printf("    |             |<----------------------------\n");
  printf("    +-------------+\n");

 

  err = 0;
 out:
  modbus_close(mb);
  modbus_free(mb);
  return err;
}
