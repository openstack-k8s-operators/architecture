# Configuring and deploying EDPM Ceph nodes

## Assumptions

- The [control-plane](control-plane.md) has been created and successfully
  deployed.

## Steps

```bash
# Switch to openstack namespace
$ oc project openstack

# Change the working directory to shiftstack
$ cd architecture/examples/dt/shiftstack

# Modify ceph nodeset values accordingly
$ pushd ceph/nodeset
$ vi values.yaml

# Generate the nodeset CR.
$ kustomize build > ceph-nodeset.yaml

# Apply the resource.
$ oc apply -f ceph-nodeset.yaml

# Wait for the nodeset to be ready state.
$ oc wait osdpns ceph-nodes --for condition=SetupReady --timeout=300s
$ popd

# Generate the deployment plan
$ pushd ceph
$ kustomize build > ceph-deploy.yaml

# Apply the deployment resource.
$ oc apply -f ceph-deploy.yaml

# Wait for the deployment to be completed.
$ oc wait osdpd ceph-deploy --for condition=Ready --timeout=600s
$ popd

# Patch the control-plane to be aware of deployed ceph
$ kustomize build > control-plane-post-ceph.yaml
$ oc apply -f control-plane-post-ceph.yaml

# Wait for the deployment to be completed.
$ oc wait osctlplane controlplane \
    --for condition=Ready \
    --timeout=15m 
```
