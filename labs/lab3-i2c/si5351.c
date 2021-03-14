#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <i2c/smbus.h>

#define	I2C_FNAME	"/dev/i2c-2"
#define	SI5351_ADDR	0x60

int	i2c_file;

void i2c_init()
{
	i2c_file = open(I2C_FNAME, O_RDWR);
	if (i2c_file < 0)
		exit(1);
}

int i2c_read(unsigned char reg)
{
	if (ioctl(i2c_file, I2C_SLAVE, SI5351_ADDR) < 0) 
		exit(1);

	int res;

	/* Using SMBus commands */
	res = i2c_smbus_read_byte_data(i2c_file, reg);
	if (res < 0) 
		exit(1);
	else 
		printf("r dev(0x%x) reg(0x%x)=0x%x\n", SI5351_ADDR, reg, res);
	return res;
}

int
main()
{
	i2c_init();
	i2c_read(0);
}
