// Bus component: many payload types, no parameters, Real and Integer fields,
// one inout and one undirected port. Ported from ssp_airplane's Environment
// shape and stripped of every domain-specific name.
package Bus {
  port def ParameterInterface;
  attribute def ParameterSet;

  port def Actuation {
    attribute channel_a : Real;
    attribute channel_b : Real;
    attribute channel_c : Real;
  }

  port def Orientation {
    attribute roll : Real;
    attribute pitch : Real;
    attribute yaw : Real;
  }

  port def Position {
    attribute x : Real;
    attribute y : Real;
    attribute z : Real;
  }

  port def StatusPacket {
    attribute speed : Real;
    attribute health : Integer;
  }

  part def Bus {
    in port actuation : Actuation;
    in port orientation_in : Orientation;
    in port position_in : Position;
    inout port shared : Orientation;
    out port orientation_out : Orientation;
    out port position_out : Position;
    out port status : StatusPacket;
  }

  part def BusComposition {
    part bus : Bus;
  }
}
