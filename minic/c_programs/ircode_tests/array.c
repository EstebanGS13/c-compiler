int ARR[2];

void main(void){
//    int arr[9.8]; // error size not integer
    float A[5];
    int k = 2;
//    int a = A[k]; // error int = float
    int C[5];
    int a = C[3];
//	A[k] = 2;  // error float = int
//	A[2] %= 10.9; // error float %= float
    C[2] = 10;
    C[4] = C[4] * 5;
    C[2] *= 5;
}