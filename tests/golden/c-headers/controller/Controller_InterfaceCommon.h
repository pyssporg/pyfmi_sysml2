#ifndef CONTROLLER_INTERFACECOMMON_H
#define CONTROLLER_INTERFACECOMMON_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Generated from architecture package Controller. Do not edit manually. */

typedef struct Controller_Command {
  double manual;
  double auto_;
  int mode;
} Controller_Command;

typedef struct Controller_Throttle {
  double demand;
  bool enabled;
} Controller_Throttle;

typedef struct Controller_Status {
  int code;
} Controller_Status;

typedef enum Controller_DataType {
  CONTROLLER_DATA_NONE = 0,
  CONTROLLER_DATA_REAL = 1,
  CONTROLLER_DATA_INTEGER = 2,
  CONTROLLER_DATA_BOOLEAN = 3,
  CONTROLLER_DATA_STRING = 4,
} Controller_DataType;

typedef struct Controller_VrMapping {
  void* data;
  Controller_DataType type;
  bool writable;
} Controller_VrMapping;

#endif  /* CONTROLLER_INTERFACECOMMON_H */
