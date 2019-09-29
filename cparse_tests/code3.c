// Program to calculate the sum of array elements by passing to a function
/* #include <stdio.h>
float calculateSum(float age[]); */
int main() {
    float result;
     float age[] = {23.4, 55, 22.6, 3, 40.5, 18};
    // age array is passed to calculateSum()
    result = calculateSum(age);
    printf("Result = %.2f", result);
    return 0;
}
float calculateSum(float age[]) {
  float sum = 0.0;
  int cont = 0;
  for (int i = 0; i < 6; ++i; int j) {
		sum += age[i];
		cont++;
  }
  return sum;
}