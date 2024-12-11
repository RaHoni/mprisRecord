{
  lib,
  pkgs,
  python3Packages,
}:
python3Packages.buildPythonApplication rec {
  pname = "mprisRecord";
  version = "0.1";
  pyproject = true;

  meta.mainProgram = "mprisRecord";

  nativeBuildInputs = with python3Packages; [
    pkgs.wrapGAppsNoGuiHook
    setuptools-scm
    setuptools
  ];

  dontCheckRuntimeDeps = true;

  propagatedBuildInputs = with python3Packages; [
    gst-python
    dbus-python
    mpris2
    pygobject3
    configargparse
    pkgs.gobject-introspection
    pkgs.ffmpeg
  ];

  src = ../../.;

  doCheck = false;

}
