// Direct FMU model: the exported part definition is itself the component,
// marked ':> FmuModel', with no container composition above it.
package Generator {
  private import ScalarValues::*;
  private import PysspCore::*;

  part def FmuModel;
  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  port def ParameterInterface;
  attribute def ParameterSet;

  port def RealSignal {
    attribute value : Real;
  }

  port def GeneratorParameters :> ParameterInterface {
    attribute gain : Real = 2.0;
    attribute offset : Real = 0.5;
  }

  attribute def GeneratorFmu :> FmuMetadata {
    attribute source = "build/Generator.fmu";
    attribute implementation = "CoSimulation";
  }

  part def Generator :> FmuModel {
    attribute fmu_meta : GeneratorFmu;
    in port parameters : GeneratorParameters;
    out port y : RealSignal;
  }
}
