{
  pkgs ? import <nixpkgs> { },
}:
pkgs.mkShell {
  packages = with pkgs.python3Packages; [
    pkgs.mprisRecord
    pkgs.ffmpeg
    pkgs.qpwgraph
    gst-python
    # select Python packages herepy
    dbus-python
    mpris2
    pygobject3
  ];
}
