{
  description = "Python project with uv2nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    uv2nix.url = "github:astraiosystems/uv2nix";
  };

  outputs = { self, nixpkgs, flake-utils, uv2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            (uv2nix.lib.${system}.mkPython {
              pyproject = ./pyproject.toml;
              lockfile = ./uv.lock;
              withDevDependencies = true;
            })
            pkgs.uv
          ];
        };
      }
    );
}
