#!/usr/bin/env python
from os import listdir, path
from datetime import datetime
import argparse
import yaml
import re, os

def create_operator_dir(name, version):
    for directory in [name, os.sep.join([name, version])]:
        if os.path.exists(directory) is not True:
            os.mkdir(directory)
    create_package_file(name, version)

def create_crd_file(crd, filename):
    with open(filename, 'w') as f:
        yaml.dump(crd, f, default_flow_style=False)

def create_package_file(name, version):
    csvVersion = "%s.%s" % (name, version)
    pkg = {
        'packageName': name,
        'channels': [
            {'name': 'alpha', 'currentCSV': csvVersion }
        ]
    }
    package_file = "%s.package.yaml" % name
    pkg_filename = os.path.join(name, package_file)
    with open(pkg_filename, 'w') as f:
        yaml.dump(pkg, f, default_flow_style=False)

def get_operator_csv(manifest_path, version_dir, name, version):
    crds = []
    rbac = None
    access = {'role': None, 'binding': None}
    deploys = []
    version = '0.0.1' if version is None else version
    name = 'operatorname' if name is None else name
    name_version = "%s.v%s" % (name, version)

    csv = {
        'apiVersion': 'operators.coreos.com/v1alpha1',
        'kind': 'ClusterServiceVersion',
        'metadata': {
            'name': name_version,
            'namespace': 'placeholder',
            'annotations': {
                'categories': 'categoryY',
                'containerImage': 'quay.io/repository/image:v1.0.1',
                'capabilities': 'Basic Install',
                'description': '',
                'support': 'companyX',
                'certified': False,
                'alm-examples': '',
                'repository': '',
                'createdAt': get_utc_time()
                }},
        'spec': {
            'keywords': ['word 1', 'word 2', 'word 3'],
            'version': version,
            'description': '',
            'customresourcedefinitions': {
                # 'owned': crds
                },
            'displayName': 'Operator Name',
            'installModes': [
                {'type': 'OwnNamespace', 'supported': True},
                {'type': 'SingleNamespace', 'supported': True},
                {'type': 'MultiNamespace', 'supported': True},
                {'type': 'AllNamespaces', 'supported': True}
                ],
            'install': {
                'spec':
                    {
                    # 'permissions': rbac,
                    # 'deployments': deploys
                    },
                'strategy': 'deployment'
                },
                'labels': {},
                'maintainers': [{'email': '', 'name': ''}],
                'provider': {'name': ''},
                'icon': [
                    {'base64data': '',
                    'mediatype': ''}
                    ],
                'minKubeVersion': '1.11.0'
            }
    } # end clusterserviceversion

    for manifest in os.listdir(manifest_path):
        if manifest.endswith(".yaml"):
            with open(path.join(manifest_path, manifest), 'r') as f:
                try:
                    documents = yaml.load_all(f, Loader=yaml.SafeLoader)
                    for doc in documents:
                        if doc.get('kind', None) == "CustomResourceDefinition":
                            crds.append(get_owned_resource_types(doc, version_dir))
                            csv['spec']['customresourcedefinitions']['owned'] = crds

                        if doc.get('kind', None) == 'StatefulSet' or doc.get('kind', None) == 'Deployment':
                            deploys.append(get_deployment(doc))
                            csv['spec']['install']['spec']['deployments'] = deploys

                        if doc.get('kind', None) == 'ClusterRoleBinding' \
                            or doc.get('kind', None) == 'RoleBinding' \
                            or doc.get('kind', None) == 'ClusterRole' \
                            or doc.get('kind', None) == 'Role':

                            if doc.get('kind', None) == 'ClusterRoleBinding':
                                access['binding'] = doc
                                access['scope'] = 'cluster'
                            elif  doc.get('kind', None) == 'RoleBinding':
                                access['binding'] = doc
                                access['scope'] = 'namespace'
                            elif doc.get('kind', None) == 'ClusterRole' \
                                or doc.get('kind', None) == 'Role':
                                access['role'] = doc

                            if access['role'] is not None and access['binding'] is not None:
                                if access['scope'] == 'cluster':
                                    csv['spec']['install']['spec']['clusterPermissions'] = get_operator_permissions(access)
                                elif access['scope'] == 'namespace':
                                    csv['spec']['install']['spec']['permissions'] = get_operator_permissions(access)

                except yaml.YAMLError as ye:
                    print(ye)

    # if len(csv.get('spec', None).get('install', None).get('spec', None).get('deployments', None)) == 1 and len(csv.get('spec', None).get('install', None).get('spec', None).get('deployments', None)[0].get('spec', None).get('template', None).get('spec', None).get('containers', None)) == 1:
    #     csv['metadata']['annotations']['containerImage'] = (csv.get('spec', None).get('install', None).get('spec', None).get('deployments', None)[0]
    #     .get('spec', None).get('template', None).get('spec', None).get('containers', None)[0].get('image', None))

    return csv

def get_utc_time():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def get_operator_permissions(access):
    result = []
    if access.get('role', None).get('metadata', None).get('name', None) == access.get('binding', None).get('roleRef', None).get('name', None):
        if len(access.get('binding', None).get('subjects', None)) == 1:
            sa = {'serviceAccountName': access.get('binding', None).get('subjects', None)[0].get('name', None),
                'rules': access.get('role', None).get('rules', None)
              }
            result.append(sa)
    return result

def get_owned_resource_types(crd, version_dir):
    name = crd.get('metadata', None).get('name', None)
    kind = crd.get('spec', None).get('names', None).get('kind', None)
    version = crd.get('spec', None).get('version', None)
    crd_filename = os.sep.join([version_dir, ("%s_%s.crd.yaml" % (kind, version)).lower()])
    create_crd_file(crd, crd_filename)
    return {'description': '', 'displayName': '', 'kind': kind, 'name': name, 'version': version}

def get_deployment(doc):
    containers = doc.get('spec', None)
    if containers.get('serviceName', False):
        del containers['serviceName']
    deployment = {'name': doc.get('metadata', None).get('name', None), 'spec': containers}
    deployment['spec']['replicas'] = 1
    return deployment

def main():
    parser = argparse.ArgumentParser(description="Operator CSV Generator")
    parser.add_argument("--manifests-dir", help="Path to kubernetes manifests")
    parser.add_argument("--name", "-n", help="Operator name e.g. cloudoperator")
    parser.add_argument("--version", "-v", help="Operator semantic version e.g. 1.0.0")
    args = parser.parse_args()

    if args.name is not None and args.version is not None:
        version_dir = os.sep.join([args.name, args.version])
        create_operator_dir(args.name, args.version)

    if args.manifests_dir:
        csv = get_operator_csv(args.manifests_dir, version_dir, args.name, args.version)
        if args.name and args.version:
            csvfile = "%s.v%s.clusterserviceversion.yaml" % (args.name, args.version)
            filename = path.sep.join([version_dir, csvfile])
            with open(filename, 'w') as f:
                yaml.dump(csv, f, default_flow_style=False)
                print("The operator CSV has been written to %s" % filename)
        else:
            print(yaml.dump(csv, default_flow_style=False))

if __name__ == "__main__":
    main()
