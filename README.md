# operator-csvgen
The Operator CSV Generator project aims to create an operator Cluster Service Version file from existing Kubernetes deployment manifests. This will mostly target operators not built with the `operator-sdk`.

The Cluster Service Version or CSV is intended to be used to add an operator to OperatorHub.io

## Usage

```
$ python operatorcsv.py -h
usage: operatorcsv.py [-h] [--manifests-dir MANIFESTS_DIR] [--output OUTPUT]

Operator CSV Generator

optional arguments:
  -h, --help            show this help message and exit
  --manifests-dir MANIFESTS_DIR
                        Path to kubernetes manifests
  --output OUTPUT       Path to write resulting Operator CSV e.g.
                        operatorname.v0.1.0.clusterserviceversion.yaml
$
```

The output option as described above specifies the path where the CSV should be written. When not supplied, the generated CSV will be printed to standard out.

```
$ python operatorcsv.py --manifests-dir ../k8s-manifests  --output testoperator.v0.1.0.clusterserviceversion.yaml
The operator CSV has been written to testoperator.v0.1.0.clusterserviceversion.yaml
$
```
