/*
 * Minimal program that triggers a KLEE error: divide by zero
 * when the symbolic x happens to be 0.
 */

#include <klee/klee.h>

int main() {
    int x;
    klee_make_symbolic(&x, sizeof(x), "x");
    return 10 / x;
}
