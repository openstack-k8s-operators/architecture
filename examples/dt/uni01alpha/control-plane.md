# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.
- Cluster observability operator is already deployed. If not, follow the
  steps found [below](#cluster-observability-operator).

### Cluster observability operator

Cluster Observability Operator must be installed as it is required by OpenStack
Telemetry operator. If not installed, the below steps can be followed

```bash
cat > subscription.yaml << EOF
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: observability-operator
  namespace: openshift-operators
  labels:
    operators.coreos.com/observability-operator.openshift-operators: ""
spec:
  channel: stable
  installPlanApproval: Automatic
  name: cluster-observability-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF

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

Change to the uni01alpha directory

```bash
cd architecture/examples/dt/uni01alpha
```

Edit [service-values.yaml](control-plane/service-values.yaml) and
[control-plane/networking/nncp/values.yaml](control-plane/networking/nncp/values.yaml).

## Apply node network configuration

Generate the node network configuration
```bash
kustomize build control-plane/networking/nncp > nncp.yaml
```
Apply the NNCP CRs
```
oc apply -f nncp.yaml
```
Wait for NNCPs to be available
```
oc wait nncp \
    -l osp/nncm-config-type=standard \
    --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured \
    --timeout=300s
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

## Apply the control-plane configuration.

Generate the control-plane CRs.
```bash
kustomize build control-plane/ > control-plane.yaml
```
Apply the CRs
```bash
oc apply -f control-plane.yaml
```

Wait for control plane to be available

```bash
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```
