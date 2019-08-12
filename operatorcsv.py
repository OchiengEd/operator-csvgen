#!/usr/bin/env python
from os import listdir, path
from datetime import datetime
import argparse
import yaml

def get_operator_csv(manifest_path):
    crds = []
    rbac = None
    access = {'role': None, 'binding': None}
    deploys = []
    
    for manifest in listdir(manifest_path):
        if manifest.endswith(".yaml"):
            with open(path.join(manifest_path, manifest), 'r') as f:
                try:
                    documents = yaml.load_all(f, Loader=yaml.SafeLoader)
                    for doc in documents:
                        if doc.get('kind', None) == "CustomResourceDefinition":
                            crds.append(get_owned_resource_types(doc))
                        elif doc.get('kind', None) == 'StatefulSet' or doc.get('kind', None) == 'Deployment':
                            deploys.append(get_deployment(doc))
                        elif doc.get('kind', None) == 'ClusterRoleBinding' \
                            or doc.get('kind', None) == 'RoleBinding' \
                            or doc.get('kind', None) == 'ClusterRole' \
                            or doc.get('kind', None) == 'Role':

                            if doc.get('kind', None) == 'ClusterRoleBinding' \
                                or doc.get('kind', None) == 'RoleBinding':
                                access['binding'] = doc
                            elif doc.get('kind', None) == 'ClusterRole' \
                                or doc.get('kind', None) == 'Role':
                                access['role'] = doc

                            if access['role'] is not None and access['binding'] is not None:
                                rbac = get_operator_permissions(access)
                except yaml.YAMLError as ye:
                    print(ye)

    csv = {
        'apiVersion': 'operators.coreos.com/v1alpha1', 
        'kind': 'ClusterServiceVersion',
        'metadata': {
            'name': 'operator-name.v0.0.1',
            'namespace': 'placeholder', 
            'annotations': {
                'categories': 'categoryY',
                'containerImage': 'quay.io/repository/image:v1.0.1',
                'description': '',
                'support': 'companyX',
                'certified': False, 
                'alm-examples': '',
                'repository': '',
                'createdAt': get_utc_time()
                }},
        'spec': {
            'keywords': ['word 1', 'word 2', 'word 3'], 
            'version': '1.0.1',
            'description': '',
            'customresourcedefinitions': {
                'owned': crds
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
                    {'permissions': rbac,
                    'deployments': deploys
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

    if len(csv.get('spec', None).get('install', None).get('spec', None).get('deployments', None)) == 1 and len(csv.get('spec', None).get('install', None).get('spec', None).get('deployments', None)[0].get('spec', None).get('template', None).get('spec', None).get('containers', None)) == 1:
        csv['metadata']['annotations']['containerImage'] = (csv.get('spec', None).get('install', None).get('spec', None).get('deployments', None)[0]
        .get('spec', None).get('template', None).get('spec', None).get('containers', None)[0].get('image', None))
    
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

def get_owned_resource_types(crd):
    name = crd.get('metadata', None).get('name', None)
    kind = crd.get('spec', None).get('names', None).get('kind', None)
    version = crd.get('spec', None).get('version', None)
    return {'description': '', 'displayName': '', 'kind': kind, 'name': name, 'version': version}

def get_deployment(doc):
    containers = doc.get('spec', None)
    if containers['serviceName']:
        del containers['serviceName']
    deployment = {'name': doc.get('metadata', None).get('name', None), 'spec': containers}
    deployment['spec']['replicas'] = 1
    return deployment

def main():
    parser = argparse.ArgumentParser(description="Operator CSV Generator")
    parser.add_argument("--manifests-dir", help="Path to kubernetes manifests")
    parser.add_argument("--output", help="Path to write resulting Operator CSV e.g. operatorname.v0.1.0.clusterserviceversion.yaml")
    args = parser.parse_args()
    
    if args.manifests_dir:
        csv = get_operator_csv(args.manifests_dir)
        if args.output:
            with open(args.output, 'w') as f:
                yaml.dump(csv, f, default_flow_style=False)
                print("The operator CSV has been written to %s" % args.output)
        else:
            print(yaml.dump(csv))

if __name__ == "__main__":
    main()