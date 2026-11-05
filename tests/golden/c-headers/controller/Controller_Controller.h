#ifndef CONTROLLER_CONTROLLER_H
#define CONTROLLER_CONTROLLER_H

#include "Controller_InterfaceCommon.h"

/* Generated interface for Controller.Controller. Do not edit manually. */

typedef enum Controller_Controller_ValueReference {
  CONTROLLER_CONTROLLER_VR_GAINS_0_ = 0,
  CONTROLLER_CONTROLLER_VR_GAINS_1_ = 1,
  CONTROLLER_CONTROLLER_VR_LABEL = 2,
  CONTROLLER_CONTROLLER_VR_COMMAND_MANUAL = 3,
  CONTROLLER_CONTROLLER_VR_COMMAND_AUTO = 4,
  CONTROLLER_CONTROLLER_VR_COMMAND_MODE = 5,
  CONTROLLER_CONTROLLER_VR_THROTTLE_DEMAND = 6,
  CONTROLLER_CONTROLLER_VR_THROTTLE_ENABLED = 7,
  CONTROLLER_CONTROLLER_VR_STATUS_CODE = 8,
} Controller_Controller_ValueReference;

enum { Controller_Controller_VrCount = 9 };

#ifdef __cplusplus
#include <string>

struct Controller_Controller_Instance {
  Controller_VrMapping vr_map[9] = {};
  double gains[2] = {1, 2.5};
  std::string label = "nominal";
  Controller_Command command = {};
  Controller_Throttle throttle = {};
  Controller_Status status = {};
};

inline void Controller_Controller_initialize_vr_map(Controller_Controller_Instance* instance) {
  for (size_t i = 0; i < Controller_Controller_VrCount; ++i) {
    instance->vr_map[i] = {nullptr, CONTROLLER_DATA_NONE, false};
  }
  instance->vr_map[CONTROLLER_CONTROLLER_VR_GAINS_0_] = {&instance->gains[0], CONTROLLER_DATA_REAL, true};
  instance->vr_map[CONTROLLER_CONTROLLER_VR_GAINS_1_] = {&instance->gains[1], CONTROLLER_DATA_REAL, true};
  instance->vr_map[CONTROLLER_CONTROLLER_VR_LABEL] = {&instance->label, CONTROLLER_DATA_STRING, true};
  instance->vr_map[CONTROLLER_CONTROLLER_VR_COMMAND_MANUAL] = {&instance->command.manual, CONTROLLER_DATA_REAL, true};
  instance->vr_map[CONTROLLER_CONTROLLER_VR_COMMAND_AUTO] = {&instance->command.auto_, CONTROLLER_DATA_REAL, true};
  instance->vr_map[CONTROLLER_CONTROLLER_VR_COMMAND_MODE] = {&instance->command.mode, CONTROLLER_DATA_INTEGER, true};
  instance->vr_map[CONTROLLER_CONTROLLER_VR_THROTTLE_DEMAND] = {&instance->throttle.demand, CONTROLLER_DATA_REAL, false};
  instance->vr_map[CONTROLLER_CONTROLLER_VR_THROTTLE_ENABLED] = {&instance->throttle.enabled, CONTROLLER_DATA_BOOLEAN, false};
  instance->vr_map[CONTROLLER_CONTROLLER_VR_STATUS_CODE] = {&instance->status.code, CONTROLLER_DATA_INTEGER, false};
}

#endif  /* __cplusplus */
#endif  /* CONTROLLER_CONTROLLER_H */