{
  description = "A possibletie to controll obs from a streamdeck";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    nixpkgs.lib.recursiveUpdate (flake-utils.lib.eachSystem [ "aarch64-linux" "x86_64-linux" ] (
      system:
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

        overlays.default = pythonOverlay;

        # Adding hydraJobs
        hydraJobs = {
          # Job to build the mprisRecord package
          mprisRecord = pkgs.mprisRecord;

          # Job to build the development shell environment
          devShell = pkgs.mkShell {
            inherit (self.devShells.${system}) default;
          };
        };
      }
    )) (flake-utils.lib.eachSystem [ "aarch64-darwin" "x86_64-darwin" ] (system: {
      overlays.default = (final: prev: {}); # Provide an empty overlay to not fail
    }));
}
