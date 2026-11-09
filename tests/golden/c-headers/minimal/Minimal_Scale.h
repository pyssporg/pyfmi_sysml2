#ifndef MINIMAL_SCALE_H
#define MINIMAL_SCALE_H

#include "Minimal_InterfaceCommon.h"

/* Generated interface for Minimal.Scale. Do not edit manually. */

#define MINIMAL_SCALE_GUID "{1cd5dff9-41fe-5fdf-abd6-fe39bc507661}"

typedef enum Minimal_Scale_ValueReference {
  MINIMAL_SCALE_VR_GAIN = 0,
  MINIMAL_SCALE_VR_U_VALUE = 1,
  MINIMAL_SCALE_VR_Y_VALUE = 2,
} Minimal_Scale_ValueReference;

enum { Minimal_Scale_VrCount = 3 };

#ifdef __cplusplus
#include <string>

struct Minimal_Scale_Instance {
  Minimal_VrMapping vr_map[3] = {};
  double gain = 2;
  Minimal_Signal u = {};
  Minimal_Signal y = {};
};

inline void Minimal_Scale_initialize_vr_map(Minimal_Scale_Instance* instance) {
  for (size_t i = 0; i < Minimal_Scale_VrCount; ++i) {
    instance->vr_map[i] = {nullptr, MINIMAL_DATA_NONE, false};
  }
  instance->vr_map[MINIMAL_SCALE_VR_GAIN] = {&instance->gain, MINIMAL_DATA_REAL, true};
  instance->vr_map[MINIMAL_SCALE_VR_U_VALUE] = {&instance->u.value, MINIMAL_DATA_REAL, true};
  instance->vr_map[MINIMAL_SCALE_VR_Y_VALUE] = {&instance->y.value, MINIMAL_DATA_REAL, false};
}

#endif  /* __cplusplus */
#endif  /* MINIMAL_SCALE_H */