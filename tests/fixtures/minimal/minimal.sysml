// Minimal synthetic architecture: one interface parameter, one input, one
// output. This is the smallest artifact set the generators must support.
package Minimal {
  private import ScalarValues::*;
  private import PysspCore::*;

  port def ParameterInterface;
  attribute def ParameterSet;

  port def Signal {
    attribute value : Real;
  }

  port def GainParameters :> ParameterInterface {
    attribute gain : Real = 2.0;
  }

  part def Scale {
    in port parameters : GainParameters;
    in port u : Signal;
    out port y : Signal;
  }

  part def Root {
    part scale : Scale;
  }
}
