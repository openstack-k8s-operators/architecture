# Configuring networking and deploy the OpenStack control plane


## Assumptions

- A storage class called `local-storage` should already exist.


## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to the uni05epsilon directory

```bash
cd architecture/examples/dt/uni05epsilon
```

Edit [control-plane/service-values.yaml](control-plane/service-values.yaml) and
[control-plane/nncp/values.yaml](control-plane/nncp/values.yaml).

Apply node network configuration

```bash
# Change to the Node Network Configuration folder.
pushd control-plane/nncp

# Generate the configuration
kustomize build > nncp.yaml

# Apply the generated configuration
oc apply -f nncp.yaml

# Wait till the network configuration is applied.
oc wait nncp \
    -l osp/nncm-config-type=standard \
    --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured \
    --timeout=300s

# Change back the working directory
popd
```

Generate and apply the control-plane configurations.

```bash
# Navigate to control-panel
pushd control-plane

# Generate the CR
kustomize build > control-plane.yaml

# Verify that control-plane.yaml includes the valid access credentials
# for the NetApp storage and provide the information if missing.

# Apply the CR
oc apply -f control-plane.yaml

# Wait for control plane to be available
oc wait osctlplane controlplane --for condition=Ready --timeout=600s

# Change back the working directory
popd
```
