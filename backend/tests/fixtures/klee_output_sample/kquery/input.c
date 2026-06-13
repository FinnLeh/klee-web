#include <klee/klee.h>
int main() {
  int x;
  klee_make_symbolic(&x, sizeof(x), "x");
  if (x > 0) {
    if (x < 100) return 1;
  }
  return 0;
}
