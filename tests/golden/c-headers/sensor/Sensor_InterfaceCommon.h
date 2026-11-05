#ifndef SENSOR_INTERFACECOMMON_H
#define SENSOR_INTERFACECOMMON_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Generated from architecture package Sensor. Do not edit manually. */

typedef struct Sensor_Rate {
  double rate;
} Sensor_Rate;

typedef struct Sensor_LevelState {
  double remaining;
  double fraction;
  bool empty;
} Sensor_LevelState;

typedef enum Sensor_DataType {
  SENSOR_DATA_NONE = 0,
  SENSOR_DATA_REAL = 1,
  SENSOR_DATA_INTEGER = 2,
  SENSOR_DATA_BOOLEAN = 3,
  SENSOR_DATA_STRING = 4,
} Sensor_DataType;

typedef struct Sensor_VrMapping {
  void* data;
  Sensor_DataType type;
  bool writable;
} Sensor_VrMapping;

#endif  /* SENSOR_INTERFACECOMMON_H */
