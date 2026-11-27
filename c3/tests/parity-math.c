#include <stdio.h>
#include <math.h>
#include <string.h>
#include <unistd.h>

#define CHECK(x) if (!(x)) { printf("FAIL %d\r",__LINE__); return 1; }
static union { double value; unsigned word[4]; } result;
static int bits(double value, unsigned a, unsigned b, unsigned c, unsigned d)
{
    result.value=value;
    if (result.word[0]!=a || result.word[1]!=b || result.word[2]!=c || result.word[3]!=d) {
        printf("BITS %x %x %x %x\r",result.word[0],result.word[1],result.word[2],result.word[3]);
        return 0;
    }
    return 1;
}
int main(void)
{

    rad();
    CHECK(bits(sin(0.0),0,0,0,0));
    CHECK(bits(cos(0.0),0x3ff0,0,0,0));
    CHECK(bits(sqrt(4.0),0x4000,0,0,0));
    CHECK(bits(sqr(3.0),0x4022,0,0,0));
    CHECK(bits(inv(2.0),0x3fe0,0,0,0));
    CHECK(bits(fabs(-2.0),0x4000,0,0,0));
    CHECK(bits(dabs(-2.0),0x4000,0,0,0));
    CHECK(bits(trunc(3.5),0x4008,0,0,0));
    CHECK(bits(dexp(1.5,2),0x4018,0,0,0));
    CHECK(bits(exp(0.0),0x3ff0,0,0,0));
    result.value=log(1.0);
    CHECK((result.word[0]&0x7fff) <= 0x3cd0);
    CHECK(fabs(sin(0.5235987755982989)-0.5)<0.0000001);
    CHECK(fabs(cos(1.047197551196598)-0.5)<0.0000001);
    CHECK(fabs(atan(1.0)-0.7853981633974483)<0.0000001);
    CHECK(fabs(asin(0.5)-0.5235987755982989)<0.0000001);
    CHECK(fabs(acos(0.5)-1.047197551196598)<0.0000001);
    CHECK(fabs(sqrt(2.0)-1.414213562373095)<0.0000001);
    CHECK(fabs(exp(1.0)-2.718281828459045)<0.0000001);
    CHECK(fabs(log(2.0)-0.6931471805599453)<0.0000001);
    CHECK(fabs(pow(2.0,3.0)-8.0)<0.0000001);
    CHECK(fabs(sinh(1.0)-1.175201193643801)<0.0000001);
    CHECK(fabs(cosh(1.0)-1.543080634815244)<0.0000001);
    CHECK(fabs(tanh(1.0)-0.761594155955765)<0.0000001);
    deg();
    CHECK(fabs(sin(30.0)-0.5)<0.0000001);
    rad();
    fputs("MATH PASS\r",stdout);
    return 0;
}
