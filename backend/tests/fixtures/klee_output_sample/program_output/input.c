#include <klee/klee.h>
#include <stdio.h>

int main() {
  int x;
  klee_make_symbolic(&x, sizeof(x), "x");
  printf("hello from klee web\n");
  if (x > 0) {
    printf("x is positive\n");
  } else {
    printf("x is not positive\n");
  }
  return 0;
}
