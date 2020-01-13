// Program to calculate the sum of array elements by passing to a function
/* #include <stdio.h>
float calculateSum(float age[]); */
int main(void) {
    float result;
     float age[];
//      age[] = {23.4, 55, 22.6, 3, 40.5, 18};
    // age array is passed to calculateSum()
    result = calculateSum(age);
    printf("Result = %.2f", result);
    return 0;
}
float calculateSum(float age[]) {
  float sum;
  sum = 0.0;
  int cont;
   cont = 0;
   int i;
  for(i = 0; i < 6; ++i) {
		sum += age[i];
		cont++;
  }
  return sum;
}