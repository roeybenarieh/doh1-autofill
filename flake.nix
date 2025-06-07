# for more information: https://medium.com/@daniel.garcia_57638/nix-nirvana-packaging-python-apps-with-uv2nix-c44e79ae4bc9
{
  description = "doh1-autofill";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/master";
    flake-utils.url = "github:numtide/flake-utils";

    # Core pyproject-nix ecosystem tools
    pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
    uv2nix.url = "github:pyproject-nix/uv2nix";
    pyproject-build-systems.url = "github:pyproject-nix/build-system-pkgs";

    # Ensure consistent dependencies between these tools
    pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";
    uv2nix.inputs.nixpkgs.follows = "nixpkgs";
    pyproject-build-systems.inputs.nixpkgs.follows = "nixpkgs";
    uv2nix.inputs.pyproject-nix.follows = "pyproject-nix";
    pyproject-build-systems.inputs.pyproject-nix.follows = "pyproject-nix";
  };

  outputs = { self, nixpkgs, flake-utils, uv2nix, pyproject-nix, pyproject-build-systems, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python312; # desired Python version

        # 1. Load Project Workspace (parses pyproject.toml, uv.lock)
        workspace = uv2nix.lib.workspace.loadWorkspace {
          workspaceRoot = ./.; # Root of flake/project
        };

        # 2. Generate Nix Overlay from uv.lock (via workspace)
        uvLockedOverlay = workspace.mkPyprojectOverlay {
          sourcePreference = "wheel"; # Or "sdist"
        };

        # 3. Placeholder for Your Custom Package Overrides
        myCustomOverrides = final: prev: {
          /* e.g., some-package = prev.some-package.overridePythonAttrs (...); */
        };

        # 4. Construct the Final Python Package Set
        pythonSet =
          (pkgs.callPackage pyproject-nix.build.packages { inherit python; }).overrideScope (nixpkgs.lib.composeManyExtensions [
            pyproject-build-systems.overlays.default # For build tools
            uvLockedOverlay # Your locked dependencies
            myCustomOverrides # Your fixes
          ]);

        # --- This is where your project's metadata is accessed ---
        projectNameInToml = "doh1-autofill"; # MUST match [project.name] in pyproject.toml!
        thisProjectAsNixPkg = pythonSet.${projectNameInToml};

        # 5. Create the Python Runtime Environment
        appPythonEnv = pythonSet.mkVirtualEnv
          (thisProjectAsNixPkg.pname + "-env")
          workspace.deps.default; # Uses deps from pyproject.toml [project.dependencies]

        # app dependencies packages
        dep_packages = with pkgs; [
          appPythonEnv # Runtime Python environment
          uv
          firefox
        ];
      in
      {
        # Development Shell
        devShells.default = pkgs.mkShell {
          packages = dep_packages;
          shellHook = '' /* Your custom shell hooks */ '';
        };

        # Nix Package for Your Application
        packages.default = pkgs.stdenv.mkDerivation {
          pname = thisProjectAsNixPkg.pname;
          version = thisProjectAsNixPkg.version;
          src = ./.; # Source of your main script

          nativeBuildInputs = [ pkgs.makeWrapper ];
          buildInputs = dep_packages;

          installPhase = ''
            # creating /bin dir inside the deriviation
            mkdir -p $out/bin 
            # copy code to /bin dir
            cp main.py $out/bin/main.py
            cp -r ${./src} $out/bin/src
            # creating wrapper executable for the entire project
            makeWrapper ${appPythonEnv}/bin/python $out/bin/${thisProjectAsNixPkg.pname} \
              --add-flags $out/bin/main.py \
              --prefix PATH : "${pkgs.lib.makeBinPath [ pkgs.firefox ]}"
          '';
        };
        packages.${thisProjectAsNixPkg.pname} = self.packages.${system}.default;

        # App for `nix run`
        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/${thisProjectAsNixPkg.pname}";
        };
        apps.${thisProjectAsNixPkg.pname} = self.apps.${system}.default;
      }
    );
}
