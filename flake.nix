{
  description = "Python development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python311;
        pythonPackages = python.pkgs;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            python
            pythonPackages.pip
            pythonPackages.virtualenv
            
            # Development tools
            pythonPackages.black
            pythonPackages.pytest
            pythonPackages.mypy
            pkgs.pyright

            # Add other system dependencies
            pkgs.just
            # pkgs.postgresql
            # pkgs.redis
          ];

          shellHook = ''
            # Create and activate virtual environment
            if [ ! -d .venv ]; then
              virtualenv .venv
            fi
            source .venv/bin/activate && echo "Virtualenv Activated"
            
            # Install dependencies if requirements.txt exists
            if [ -f requirements.txt ]; then
              pip install -r requirements.txt && echo "Installed requirements.txt"
            fi
            echo "🐍 $(python --version)"
          '';
        };
      }
    );
}
