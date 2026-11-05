// Primary root of a two-root load: the composition the exporter selects, and a
// definition whose bare name also exists in the included package.
package Packages {
  private import ScalarValues::*;
  private import PysspCore::*;
  private import Support::*;

  port def ParameterInterface;
  attribute def ParameterSet;

  port def PackagesSignal {
    attribute value : Real;
  }

  port def PackagesParameters :> ParameterInterface {
    attribute gain : Real = 1.0;
  }

  part def Leaf {
    in port parameters : PackagesParameters;
    in port u : PackagesSignal;
    out port y : PackagesSignal;
  }

  part def PackagesComposition {
    part unit : Support::Unit;
  }
}
