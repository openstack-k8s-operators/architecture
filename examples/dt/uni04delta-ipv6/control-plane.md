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
oc wait deployments/observability-operator --for condition=Available \
    --timeout=300s
```


## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to uni04delta-ipv6 directory

```bash
cd architecture/examples/dt/uni04delta-ipv6
```

Apply the required network configurations.

```bash
# Change the Node Network Configuration folder.
pushd control-plane/nncp

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

Generate and apply the control-plane configurations.

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
