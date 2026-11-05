// Controller component: a list parameter, a String parameter, a multi-field
// input and two outputs of mixed primitive types. Ported from ssp_airplane's
// MissionComputer shape and stripped of every domain-specific name.
package Controller {
  port def ParameterInterface;
  attribute def ParameterSet;

  port def Command {
    attribute manual : Real;
    attribute auto : Real;
    attribute mode : Integer;
  }

  port def Throttle {
    attribute demand : Real;
    attribute enabled : Boolean;
  }

  port def Status {
    attribute code : Integer;
  }

  port def ControllerParameters :> ParameterInterface {
    attribute gains : Real[2] = (1.0, 2.5);
    attribute label : String = "nominal";
  }

  part def Controller {
    in port parameters : ControllerParameters;
    in port command : Command;
    out port throttle : Throttle;
    out port status : Status;
  }

  part def ControllerComposition {
    part controller : Controller;
  }
}
