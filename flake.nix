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
    flake-utils.lib.eachSystem (nixpkgs.lib.lists.remove ["x86-64-darwin" "aarch64-apple-darwin" "x86_64-apple-darwin"] (flake-utils.lib.defaultSystems) ) (
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
    );
}
