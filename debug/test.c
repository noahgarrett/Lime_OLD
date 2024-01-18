#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
int main() { char *a = strdup("apples");strcpy(a, "bubbles");return 1;free(a); }