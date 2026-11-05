within GeneratedInterfaces;
package GeneratedInterfaces
  connector Command
    input Real manual;
    input Real auto;
    input Integer mode;
  end Command;

  connector Status
    output Integer code;
  end Status;

  connector Throttle
    output Real demand;
    output Boolean enabled;
  end Throttle;

end GeneratedInterfaces;
