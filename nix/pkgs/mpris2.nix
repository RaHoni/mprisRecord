{
  lib,
  fetchPypi,
  python3Packages,
}:
python3Packages.buildPythonPackage rec {
  pname = "mpris2";
  version = "1.0.2";

  propagatedBuildInputs = [ ];

  src = fetchPypi {
    inherit pname version;
    hash = "sha256-JmO+A/B1WQVXRu8o5v5oeSFl6z2tyEiA7KiEGip+sYU=";
  };

  doCheck = false;

}
