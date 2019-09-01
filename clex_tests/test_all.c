12345

0b10101010
00b
0xFa2

071
0

1234.523

546

4546.

42.0

.902905

.0

00

test "esto \b es una "str"

"esto tambien\r es una" str"

"  "
char string[] = "hola mundo";

"asas\" fuera"

'@'

"@"
@

'\'

'/'
'\t'

'\'

'.'

'?'

char s = '\n'

"esto es un 'c' har"

123.45

51.


58.087

50.0

0.123

.523

.7

0.0

int main()
{
    int t1 = 0, t2 = 1, nextTerm = 0, n;
    printf("Enter a positive number: ");
    scanf(n);
    // displays the first two terms which is always 0 and 1
    printf("Fibonacci Series: %d, %d, ", t1, t2);
    nextTerm = t1 + t2;
    while(nextTerm <= n)
    {
        printf(nextTerm);
        t1 = t2;
        t2 = nextTerm;
        nextTerm = t1 + t2;
    }

    return 0;
}

/* C program to illustrate
use of
multi-line comment */
#include <stdio.h>
int main(void)
{

    /* Multi-line Welcome user comment
    written to demonstrate comments
    in C/C++ *
    printf("Welcome to GeeksforGeeks");
    return 0;
}