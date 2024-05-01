# Configuring and deploying OpenStack compute nodes

## Assumption

- The [control-plane](control-plane.md) has been successfully deployed.
- The [edpm-ceph](ceph.md) has been successfully deployed.

## Configuration

Ensure the following files are modified according to the deployed environment

- [values.yaml](compute/values.yaml) with the following information
  - SSH keys for accessing the deployed compute nodes
  - SSH keys to be used for Nova migration
  - MAC addresses of the compute systems

## Deployment

```bash
# Switch to openstack namespace
$ oc project openstack

# Change to shiftonstack directory
$ cd architecture/examples/dt/shiftstack

# Modify nodeset values accordingly
$ pushd compute
$ vi values.yaml

# Generate the nodeset CR.
$ kustomize build > compute-nodeset.yaml

# Apply the resource.
$ oc apply -f compute-nodeset.yaml

# Wait for the nodeset to be ready state.
$ oc wait osdpns compute-nodes --for condition=SetupReady --timeout=300s
$ popd

# Generate the deployment plan
$ popd
$ kustomize build > compute-deploy.yaml

# Apply the deployment resource.
$ oc apply -f compute-deploy.yaml

# Wait for the deployment to be completed.
$ oc wait osdpd compute-deploy --for condition=Ready --timeout=600s
```
