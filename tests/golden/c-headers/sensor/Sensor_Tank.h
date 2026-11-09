#ifndef SENSOR_TANK_H
#define SENSOR_TANK_H

#include "Sensor_InterfaceCommon.h"

/* Generated interface for Sensor.Tank. Do not edit manually. */

#define SENSOR_TANK_GUID "{25dea124-0dbb-5ba3-b000-54cbbd00f846}"

typedef enum Sensor_Tank_ValueReference {
  SENSOR_TANK_VR_CAPACITY = 0,
  SENSOR_TANK_VR_RESERVE = 1,
  SENSOR_TANK_VR_SUPPLY_RATE = 2,
  SENSOR_TANK_VR_LEVEL_REMAINING = 3,
  SENSOR_TANK_VR_LEVEL_FRACTION = 4,
  SENSOR_TANK_VR_LEVEL_EMPTY = 5,
} Sensor_Tank_ValueReference;

enum { Sensor_Tank_VrCount = 6 };

#ifdef __cplusplus
#include <string>

struct Sensor_Tank_Instance {
  Sensor_VrMapping vr_map[6] = {};
  double capacity = 3160;
  double reserve = 0.08;
  Sensor_Rate supply = {};
  Sensor_LevelState level = {};
};

inline void Sensor_Tank_initialize_vr_map(Sensor_Tank_Instance* instance) {
  for (size_t i = 0; i < Sensor_Tank_VrCount; ++i) {
    instance->vr_map[i] = {nullptr, SENSOR_DATA_NONE, false};
  }
  instance->vr_map[SENSOR_TANK_VR_CAPACITY] = {&instance->capacity, SENSOR_DATA_REAL, true};
  instance->vr_map[SENSOR_TANK_VR_RESERVE] = {&instance->reserve, SENSOR_DATA_REAL, true};
  instance->vr_map[SENSOR_TANK_VR_SUPPLY_RATE] = {&instance->supply.rate, SENSOR_DATA_REAL, true};
  instance->vr_map[SENSOR_TANK_VR_LEVEL_REMAINING] = {&instance->level.remaining, SENSOR_DATA_REAL, false};
  instance->vr_map[SENSOR_TANK_VR_LEVEL_FRACTION] = {&instance->level.fraction, SENSOR_DATA_REAL, false};
  instance->vr_map[SENSOR_TANK_VR_LEVEL_EMPTY] = {&instance->level.empty, SENSOR_DATA_BOOLEAN, false};
}

#endif  /* __cplusplus */
#endif  /* SENSOR_TANK_H */