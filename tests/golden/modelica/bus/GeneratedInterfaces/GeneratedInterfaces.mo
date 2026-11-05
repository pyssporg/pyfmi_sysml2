within GeneratedInterfaces;
package GeneratedInterfaces
  connector Actuation
    input Real channel_a;
    input Real channel_b;
    input Real channel_c;
  end Actuation;

  connector Orientation
    Real roll;
    Real pitch;
    Real yaw;
  end Orientation;

  connector Position
    Real x;
    Real y;
    Real z;
  end Position;

  connector StatusPacket
    output Real speed;
    output Integer health;
  end StatusPacket;

end GeneratedInterfaces;
