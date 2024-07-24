{
  description = "A possibletie to controll obs from a streamdeck";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem
    (system: 
    let
      pythonOverlay = import ./nix/overlay.nix;      
      pkgs = import nixpkgs {
        inherit system;
        overlays = [ pythonOverlay ];
      };
    in
    {
      devShells.default = import ./nix/shell.nix { inherit pkgs; };

      packages = rec {
        mprisRecord = pkgs.mprisRecord;
        default = mprisRecord;
      };
    }
    );
}
