# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to uni04delta-ipv6 directory

```bash
cd architecture/examples/dt/uni04delta-ipv6
```

# Apply the required node network configurations.
```bash
vi control-plane/networking/nncp/values.yaml
```

```bash
# Change the Node Network Configuration folder.
pushd control-plane/networking/nncp

# Generate the configuration
kustomize build > nncp.yaml

# Apply the generated configuration
oc apply -f nncp.yaml

# Wait till the network configuration is applied.
oc wait nncp -l osp/nncm-config-type=standard \
    --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured \
    --timeout=300s

# change the working directory
popd
```
# Apply remainig networking configuration

Generate the remaining networking configuration
```bash
kustomize build control-plane/networking > networking.yaml
```
Apply the networking CRs
```bash
oc apply -f networking.yaml
```

# Generate and apply the control-plane configurations.

```bash
# Navigate to control-panel
pushd control-plane

# Generate the CR
kustomize build > control-plane.yaml

# Apply the CR
oc apply -f control-plane.yaml

# Wait till the control plane is ready.
oc wait openstackcontrolplane --for condition=Ready --timeout=600s

# change the work_dir
popd
```
