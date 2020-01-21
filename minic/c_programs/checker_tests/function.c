int test(int a){
    return test(a);
}

void sort(int A[]){
    return A; // error return int in void func
}

void main(){
    int a = test(4);
    int b = sort(a); // error assign void expr to int var
    return ;
}