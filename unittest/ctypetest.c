#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>

static int failed;

static void check_true(const char *name, int condition)
{
	if (condition)
		printf("%s [PASS]\n", name);
	else {
		printf("%s [FAIL]\n", name);
		failed = 1;
	}
}

void simple(void)
{
	check_true("simple isascii", isascii('a'));
	check_true("simple isalpha", isalpha('a'));
	check_true("simple islower", islower('a'));
	check_true("simple isupper", isupper('A'));
	check_true("simple isdigit", isdigit('5'));
	check_true("simple isxdigit", isxdigit('A'));
	check_true("simple isspace", isspace(' '));
	check_true("simple ispunct", ispunct('!'));
	check_true("simple iscntrl", iscntrl(0));
	check_true("simple !isalpha", !isalpha('5'));
	check_true("simple !isdigit", !isdigit('a'));
	check_true("simple !isspace", !isspace('A'));
	check_true("simple tolower", tolower('A') == 'a');
	check_true("simple tolower unchanged", tolower('z') == 'z');
	check_true("simple toupper", toupper('a') == 'A');
	check_true("simple toupper unchanged", toupper('Z') == 'Z');
}

void exhaustive( void )
{
	int a, n;
	int (*classfn)(int);

	for (a=0; a<256; a++) {
		classfn=isdigit;
		if (isdigit(a) != (*classfn)(a)) failed=1;
		classfn=isalpha;
		if (isalpha(a) != (*classfn)(a)) failed=1;
		classfn=isprint;
		if (isprint(a) != (*classfn)(a)) failed=1;
		classfn=isspace;
		if (isspace(a) != (*classfn)(a)) failed=1;
	}
	check_true("classification macro/function agreement", !failed);
	n='0'; a=isdigit(n++);
	check_true("isdigit evaluates once", a && n == '1');
	n='A'; a=isalpha(n++);
	check_true("isalpha evaluates once", a && n == 'B');
	n='!'; a=isprint(n++);
	check_true("isprint evaluates once", a && n == '"');
	n=' '; a=isspace(n++);
	check_true("isspace evaluates once", a && n == '!');

	for( a=0; a<0x80; a++ )
	{
		if( !isascii(a) )
		{
			printf("%s isascii+ [FAIL: %d]\n",__func__, a );
			failed = 1;
			break;
		}
	}

	for( a=0x80; a<0x100; a++ )
	{
		if( isascii(a) )
		{
			printf("%s isascii- [FAIL]: %d\n",__func__, a );
			failed = 1;
			break;
		}
	}
}

int main()
{
	simple();
	exhaustive();
	return failed;
}
