int a;

int bambam(int x, bool b) {
    if (b) {
        return 0;
    }
    return bambam(x, !b);
}

int pebbles(int x, int y) {
    bool v;
    int w;
    v = x == y;
    w = 3;
    w = bambam(x, v);
    return w;
}