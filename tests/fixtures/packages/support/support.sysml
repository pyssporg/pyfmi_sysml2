// Included root: a part definition with parts that the primary composition
// uses, and a second definition sharing a bare name with the primary package.
package Support {
  port def SupportSignal {
    attribute value : Real;
  }

  port def SupportParameters :> Packages::ParameterInterface {
    attribute bias : Real = 0.5;
  }

  part def Leaf {
    in port parameters : SupportParameters;
    in port u : SupportSignal;
    out port y : SupportSignal;
  }

  part def Unit {
    part leaf : Support::Leaf;
  }
}
