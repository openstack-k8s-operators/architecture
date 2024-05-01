# Configuring networking and deploying the OpenStack Control Plane

## Assumption

- A storage class called `local-storage` exists.

## Network configuration

```bash
# Switch to the openstack namespace
$ oc project openstack

# Change the working directory
$ cd architecture/examples/dt/shiftstack

# Ensure the network values are modified based on the environment.
$ pushd control-plane/nncp
$ vi values.yaml

# Apply network configuration
$ kustomize build > nncp.yaml
$ oc apply -f nncp.yaml

# Wait for the network configurations to be applied.
$ oc wait nncp \
    -l osp/nncm-config-type=standard \
    --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured \
    --timeout=300s
# Ensure the service values are accurate
$ popd

# Apply the control-plane customizations
$ pushd control-plane
$ kustomize build > control-plane.yaml
$ oc apply -f control-plane.yaml

# Wait for the control-plane setup to be ready.
$ oc wait osctlplane controlplane --for condition=Ready --timeout=600s
$ popd
```
