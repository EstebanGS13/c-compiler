int a = 0;
float A[2.4]; // error size not int

void sumar(int a, int b){
    int total[1];
    float c = 2.1;
    total = a + b;
    return total;
    while(4 < 5){
        int k = 4+2;
        i++;
        break;
    }
    break;
    return ;
}

int main(void){
//    int k = 4.5; // error diff type
//    int a = 3; // error alrd decl
//    c = 2; // error not decl
//
//    int b;
//    b = 2.42; // error not same type

    int  a = 2;
    float b = 3.14;
    int c = a + 3; // OKAY
    int d = a + b; // Error. int + float
    int e = b + 4.5; // Error. int = float
//
//    int a[9.0]; // error size not int
//    int b[0]; // error > 0
//    int c[5+2]; // error pos int
//    int d[-1]; // error pos int

    char a = 'a'; // OKAY
    char b = 'a' + 'b'; // Error (op + no soportada)
//
//    int a;
//    a = 4 + 5; // OKAY
//    a = 4.5; // Error. int = float
//    sumar(4, 2);
//    return 4.2; // error return type
//
    int A[5];
    A[k] = 1;
    sumar(A[2]);
    ;
    return 0;
}

