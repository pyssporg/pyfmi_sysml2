#ifndef GENERATOR_H
#define GENERATOR_H

#include "Generator_InterfaceCommon.h"

/* Generated interface for Generator. Do not edit manually. */

typedef enum Generator_ValueReference {
  GENERATOR_VR_GAIN = 0,
  GENERATOR_VR_OFFSET = 1,
  GENERATOR_VR_Y_VALUE = 2,
} Generator_ValueReference;

enum { Generator_VrCount = 3 };

#ifdef __cplusplus
#include <string>

struct Generator_Instance {
  Generator_VrMapping vr_map[3] = {};
  double gain = 2;
  double offset = 0.5;
  Generator_RealSignal y = {};
};

inline void Generator_initialize_vr_map(Generator_Instance* instance) {
  for (size_t i = 0; i < Generator_VrCount; ++i) {
    instance->vr_map[i] = {nullptr, GENERATOR_DATA_NONE, false};
  }
  instance->vr_map[GENERATOR_VR_GAIN] = {&instance->gain, GENERATOR_DATA_REAL, true};
  instance->vr_map[GENERATOR_VR_OFFSET] = {&instance->offset, GENERATOR_DATA_REAL, true};
  instance->vr_map[GENERATOR_VR_Y_VALUE] = {&instance->y.value, GENERATOR_DATA_REAL, false};
}

#endif  /* __cplusplus */
#endif  /* GENERATOR_H */