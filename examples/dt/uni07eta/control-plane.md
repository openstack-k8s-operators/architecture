# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.
- Cluster observability operator is already deployed. If not, follow the
  steps found [below](#cluster-observability-operator).

# Apply the cr
oc apply -f subscription.yaml

# Wait for the deployment to be ready
oc wait deployments/observability-operator --for condition=Available \
    --timeout=300s
```
## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to the uni07eta directory

```bash
cd architecture/examples/dt/uni07eta
```

Edit [control-plane/service-values.yaml](control-plane/service-values.yaml) and
[control-plane/networking/nncp/values.yaml](control-plane/networking/nncp/values.yaml).

Apply node network configuration

```bash
pushd control-plane/networking/nncp
kustomize build > nncp.yaml
oc apply -f nncp.yaml
oc wait nncp \
    -l osp/nncm-config-type=standard \
    --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured \
    --timeout=300s
popd
```

## Apply remaining networking configuration

Generate the reminaing networking configuration
```
kustomize build control-plane/networking > networking.yaml
```
Apply the networking CRs
```
oc apply -f networking.yaml
```


Generate the control-plane and networking CRs.

```bash
pushd control-plane
kustomize build > control-plane.yaml
```

## Create CRs

```bash
oc apply -f control-plane.yaml
popd
```

Wait for control plane to be available

```bash
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```

