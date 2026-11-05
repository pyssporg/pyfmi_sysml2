#ifndef BUS_BUS_H
#define BUS_BUS_H

#include "Bus_InterfaceCommon.h"

/* Generated interface for Bus.Bus. Do not edit manually. */

typedef enum Bus_Bus_ValueReference {
  BUS_BUS_VR_ACTUATION_CHANNEL_A = 0,
  BUS_BUS_VR_ACTUATION_CHANNEL_B = 1,
  BUS_BUS_VR_ACTUATION_CHANNEL_C = 2,
  BUS_BUS_VR_ORIENTATION_IN_ROLL = 3,
  BUS_BUS_VR_ORIENTATION_IN_PITCH = 4,
  BUS_BUS_VR_ORIENTATION_IN_YAW = 5,
  BUS_BUS_VR_POSITION_IN_X = 6,
  BUS_BUS_VR_POSITION_IN_Y = 7,
  BUS_BUS_VR_POSITION_IN_Z = 8,
  BUS_BUS_VR_SHARED_ROLL = 9,
  BUS_BUS_VR_SHARED_PITCH = 10,
  BUS_BUS_VR_SHARED_YAW = 11,
  BUS_BUS_VR_ORIENTATION_OUT_ROLL = 12,
  BUS_BUS_VR_ORIENTATION_OUT_PITCH = 13,
  BUS_BUS_VR_ORIENTATION_OUT_YAW = 14,
  BUS_BUS_VR_POSITION_OUT_X = 15,
  BUS_BUS_VR_POSITION_OUT_Y = 16,
  BUS_BUS_VR_POSITION_OUT_Z = 17,
  BUS_BUS_VR_STATUS_SPEED = 18,
  BUS_BUS_VR_STATUS_HEALTH = 19,
} Bus_Bus_ValueReference;

enum { Bus_Bus_VrCount = 20 };

#ifdef __cplusplus
#include <string>

struct Bus_Bus_Instance {
  Bus_VrMapping vr_map[20] = {};
  Bus_Actuation actuation = {};
  Bus_Orientation orientation_in = {};
  Bus_Position position_in = {};
  Bus_Orientation shared = {};
  Bus_Orientation orientation_out = {};
  Bus_Position position_out = {};
  Bus_StatusPacket status = {};
};

inline void Bus_Bus_initialize_vr_map(Bus_Bus_Instance* instance) {
  for (size_t i = 0; i < Bus_Bus_VrCount; ++i) {
    instance->vr_map[i] = {nullptr, BUS_DATA_NONE, false};
  }
  instance->vr_map[BUS_BUS_VR_ACTUATION_CHANNEL_A] = {&instance->actuation.channel_a, BUS_DATA_REAL, true};
  instance->vr_map[BUS_BUS_VR_ACTUATION_CHANNEL_B] = {&instance->actuation.channel_b, BUS_DATA_REAL, true};
  instance->vr_map[BUS_BUS_VR_ACTUATION_CHANNEL_C] = {&instance->actuation.channel_c, BUS_DATA_REAL, true};
  instance->vr_map[BUS_BUS_VR_ORIENTATION_IN_ROLL] = {&instance->orientation_in.roll, BUS_DATA_REAL, true};
  instance->vr_map[BUS_BUS_VR_ORIENTATION_IN_PITCH] = {&instance->orientation_in.pitch, BUS_DATA_REAL, true};
  instance->vr_map[BUS_BUS_VR_ORIENTATION_IN_YAW] = {&instance->orientation_in.yaw, BUS_DATA_REAL, true};
  instance->vr_map[BUS_BUS_VR_POSITION_IN_X] = {&instance->position_in.x, BUS_DATA_REAL, true};
  instance->vr_map[BUS_BUS_VR_POSITION_IN_Y] = {&instance->position_in.y, BUS_DATA_REAL, true};
  instance->vr_map[BUS_BUS_VR_POSITION_IN_Z] = {&instance->position_in.z, BUS_DATA_REAL, true};
  instance->vr_map[BUS_BUS_VR_SHARED_ROLL] = {&instance->shared.roll, BUS_DATA_REAL, true};
  instance->vr_map[BUS_BUS_VR_SHARED_PITCH] = {&instance->shared.pitch, BUS_DATA_REAL, true};
  instance->vr_map[BUS_BUS_VR_SHARED_YAW] = {&instance->shared.yaw, BUS_DATA_REAL, true};
  instance->vr_map[BUS_BUS_VR_ORIENTATION_OUT_ROLL] = {&instance->orientation_out.roll, BUS_DATA_REAL, false};
  instance->vr_map[BUS_BUS_VR_ORIENTATION_OUT_PITCH] = {&instance->orientation_out.pitch, BUS_DATA_REAL, false};
  instance->vr_map[BUS_BUS_VR_ORIENTATION_OUT_YAW] = {&instance->orientation_out.yaw, BUS_DATA_REAL, false};
  instance->vr_map[BUS_BUS_VR_POSITION_OUT_X] = {&instance->position_out.x, BUS_DATA_REAL, false};
  instance->vr_map[BUS_BUS_VR_POSITION_OUT_Y] = {&instance->position_out.y, BUS_DATA_REAL, false};
  instance->vr_map[BUS_BUS_VR_POSITION_OUT_Z] = {&instance->position_out.z, BUS_DATA_REAL, false};
  instance->vr_map[BUS_BUS_VR_STATUS_SPEED] = {&instance->status.speed, BUS_DATA_REAL, false};
  instance->vr_map[BUS_BUS_VR_STATUS_HEALTH] = {&instance->status.health, BUS_DATA_INTEGER, false};
}

#endif  /* __cplusplus */
#endif  /* BUS_BUS_H */