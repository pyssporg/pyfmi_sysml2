#ifndef MINIMAL_INTERFACECOMMON_H
#define MINIMAL_INTERFACECOMMON_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Generated from architecture package Minimal. Do not edit manually. */

typedef struct Minimal_Signal {
  double value;
} Minimal_Signal;

typedef enum Minimal_DataType {
  MINIMAL_DATA_NONE = 0,
  MINIMAL_DATA_REAL = 1,
  MINIMAL_DATA_INTEGER = 2,
  MINIMAL_DATA_BOOLEAN = 3,
  MINIMAL_DATA_STRING = 4,
} Minimal_DataType;

typedef struct Minimal_VrMapping {
  void* data;
  Minimal_DataType type;
  bool writable;
} Minimal_VrMapping;

#endif  /* MINIMAL_INTERFACECOMMON_H */
