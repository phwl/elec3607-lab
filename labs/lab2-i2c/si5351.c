#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <i2c/smbus.h>

#define	I2C_FNAME	"/dev/i2c-0"
#define	SI5351_ADDR	0x60
#define	SI5351_REGS	256

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
		printf("r dev(0x%x) reg(0x%x)=0x%x (decimal %d)\n", SI5351_ADDR, reg, res, res);
	return res;
}

int
main()
{
	int	a = 23, b = 290261, c = 1048575, d = 22, e = 0, f = 1, R = 1;
	double	fin = 27e6, fout;
	unsigned char	reg[SI5351_REGS];

	i2c_init();
	for (int i = 0; i < SI5351_REGS; i++)
		reg[i] = i2c_read(i);
	fout = (double)fin * ((double)a + (double)b / c) / 
               ((double)R * d + (double)e / f);
	int xp3 = ((reg[5] & 0xf0) << 12) + (reg[0] << 8) + reg[1];
	int xp2 = (reg[5] & 0xf) << 16 + reg[6] << 8 + reg[7];
	int xp1 = (reg[2] & 0x3) << 16 + reg[3] << 8 + reg[4];
	printf("P1,P2,P3 = %x %x %x\n", xp1, xp2, xp3);
	c = p3;
	printf("Fout = %g\n", fout);
}

