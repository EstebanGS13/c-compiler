//#include <stdio.h>
//void displayNumbers(int num[2][2]);
int main(void)
{
    int num[];
    printf("Enter 4 numbers:\n");
    int i;
    for (i = 0; i < 2; ++i)
        for (int j = 0; j < 2; ++j)
            scanf("%d", num[i]);
    // passing multi-dimensional array to a function
    displayNumbers(num);
    return 0;
}
void displayNumbers(int num[])
{
    printf("Displaying:\n");
    int i;
    for (i = 0; i < 2; ++i) {
        int j;
        for (j = 0; j < 2; ++j) {
           printf("%d\n", num[i]);
        }
    }
}