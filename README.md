# operator-csvgen

The Operator CSV Generator project aims to make creating the initial Cluster Service Version(CSV) for operators built without the `operator-sdk` easier based on the existing Kubernetes yaml files.

The CSV is necessary to add an operator to OperatorHub.io

## Usage

```
$ python operatorcsv.py -h
usage: operatorcsv.py [-h] [--manifests-dir MANIFESTS_DIR] [--name NAME]
                      [--version VERSION]

Operator CSV Generator

optional arguments:
  -h, --help            show this help message and exit
  --manifests-dir MANIFESTS_DIR
                        Path to kubernetes manifests
  --name NAME, -n NAME  Operator name e.g. cloudoperator
  --version VERSION, -v VERSION
                        Operator semantic version e.g. 1.0.0
$
```
