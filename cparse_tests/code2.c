// Program to take 5 values from the user and store them in an array
// Print the elements stored in the array
#include <stdio.h>
int main() {
  int values[];
  bool test;
  printf("Enter 5 integers: ");
  // taking input and storing it in an array
  for(i = 0; i < 5; ++i) {
     scanf(values[i]);
     test = true;
  }
  printf("Displaying integers: ");
  // printing elements of an array
  for(int i = 0; i < 5; ++i) {
     printf("\n", values[i]);
     break;
  }
  return 0;
}