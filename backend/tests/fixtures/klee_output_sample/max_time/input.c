#include <klee/klee.h>

#define N 14

int main() {
  int arr[N];
  klee_make_symbolic(arr, sizeof(arr), "arr");

  for (int i = 0; i < N - 1; i++) {
    for (int j = 0; j < N - 1 - i; j++) {
      if (arr[j] > arr[j + 1]) {
        int tmp = arr[j];
        arr[j] = arr[j + 1];
        arr[j + 1] = tmp;
      }
    }
  }
  for (int i = 0; i < N - 1; i++) {
    if (arr[i] > arr[i + 1]) return -1;
  }
  return 0;
}
