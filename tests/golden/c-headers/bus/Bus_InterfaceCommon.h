#ifndef BUS_INTERFACECOMMON_H
#define BUS_INTERFACECOMMON_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Generated from architecture package Bus. Do not edit manually. */

typedef struct Bus_Actuation {
  double channel_a;
  double channel_b;
  double channel_c;
} Bus_Actuation;

typedef struct Bus_Orientation {
  double roll;
  double pitch;
  double yaw;
} Bus_Orientation;

typedef struct Bus_Position {
  double x;
  double y;
  double z;
} Bus_Position;

typedef struct Bus_StatusPacket {
  double speed;
  int health;
} Bus_StatusPacket;

typedef enum Bus_DataType {
  BUS_DATA_NONE = 0,
  BUS_DATA_REAL = 1,
  BUS_DATA_INTEGER = 2,
  BUS_DATA_BOOLEAN = 3,
  BUS_DATA_STRING = 4,
} Bus_DataType;

typedef struct Bus_VrMapping {
  void* data;
  Bus_DataType type;
  bool writable;
} Bus_VrMapping;

#endif  /* BUS_INTERFACECOMMON_H */
