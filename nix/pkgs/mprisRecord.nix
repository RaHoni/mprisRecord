{
  lib,
  pkgs,
  python3Packages
}:
python3Packages.buildPythonApplication rec {
        pname = "recordFromSpotify";
        version = "0.1";
        pyproject = true;

        meta.mainProgram = "record";

        nativeBuildInputs = with python3Packages; [ setuptools-scm setuptools ];

        dontCheckRuntimeDeps = true;

        propagatedBuildInputs = with python3Packages; [ mpris2 pygobject3 configargparse pkgs.gobject-introspection ];

        src = ../../.;

        doCheck = false;

        }

