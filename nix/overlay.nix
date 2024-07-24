(final: prev: {
  python3 = prev.python3.override {
    packageOverrides = pyfinal: pyprev: {
      mpris2 = prev.callPackage ./pkgs/mpris2.nix { };
    };
  };
  mprisRecord = prev.callPackage ./pkgs/mprisRecord.nix { };
  python3Packages = final.python3.pkgs;
})
