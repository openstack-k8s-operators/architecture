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
  channel: development
  installPlanApproval: Automatic
  name: cluster-observability-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF

# Apply the cr
oc apply -f subscription.yaml

# Wait for the deployment to be ready
oc wait -n openshift-operators deployments/observability-operator \
    --for condition=Available \
    --timeout=300s
```

## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to the uni01alpha directory

```bash
cd architecture/examples/dt/bmo
```

Edit [service-values.yaml](control-plane/service-values.yaml) and
[control-plane/nncp/values.yaml](control-plane/nncp/values.yaml).

Apply node network configuration

```bash
pushd control-plane/nncp
kustomize build > nncp.yaml
oc apply -f nncp.yaml
oc wait nncp \
    -l osp/nncm-config-type=standard \
    --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured \
    --timeout=300s
popd
```

Generate the control-plane and networking CRs.

```bash
pushd control-plane
kustomize build > control-plane.yaml
```

## Create CRs

> **_NOTE:_** Since Cinder is using LVM backend, set 
> `openstack.org/cinder-lvm=` label on one of the nodes:
> 
> `oc label node <nodename> openstack.org/cinder-lvm=`

```bash
oc apply -f control-plane.yaml
popd
```

Wait for control plane to be available

```bash
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```
