#ifndef GENERATOR_INTERFACECOMMON_H
#define GENERATOR_INTERFACECOMMON_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Generated from architecture package Generator. Do not edit manually. */

typedef struct Generator_RealSignal {
  double value;
} Generator_RealSignal;

typedef enum Generator_DataType {
  GENERATOR_DATA_NONE = 0,
  GENERATOR_DATA_REAL = 1,
  GENERATOR_DATA_INTEGER = 2,
  GENERATOR_DATA_BOOLEAN = 3,
  GENERATOR_DATA_STRING = 4,
} Generator_DataType;

typedef struct Generator_VrMapping {
  void* data;
  Generator_DataType type;
  bool writable;
} Generator_VrMapping;

#endif  /* GENERATOR_INTERFACECOMMON_H */
