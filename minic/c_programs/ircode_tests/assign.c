void main(void){
    int a = 100;
    float b;
    float c;
    a = a + 2;
    a = 2 + a;
    a += 5;
    a -= -a;
    a *= 7;
    a /= 15;
    a %= 2;
//    b %= a; // error float = int
//    c %= 5.5; // error % on float
}
