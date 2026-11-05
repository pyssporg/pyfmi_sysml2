// Storage-tank component: two interface parameters, one real input, one output
// payload with a Boolean field. Ported from ssp_airplane's FuelSystem shape and
// stripped of every domain-specific name.
package Sensor {
  port def ParameterInterface;
  attribute def ParameterSet;

  port def Rate {
    attribute rate : Real;
  }

  port def LevelState {
    attribute remaining : Real;
    attribute fraction : Real;
    attribute empty : Boolean;
  }

  port def TankParameters :> ParameterInterface {
    attribute capacity : Real = 3160.0;
    attribute reserve : Real = 0.08;
  }

  part def Tank {
    in port parameters : TankParameters;
    in port supply : Rate;
    out port level : LevelState;
  }

  part def SensorComposition {
    part tank : Tank;
  }
}
