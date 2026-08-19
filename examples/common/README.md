# Common CRs

All VAs and DTs assume that these CRs have been created.

## OpenStack Secrets (osp-secret)

The control plane references a Kubernetes Secret named `osp-secret` that
contains passwords for all OpenStack service and database accounts. The
base template at `lib/control-plane/base/osp-secrets.env` ships with
`CHANGEME_REQUIRED` sentinel values that **must** be replaced with securely
generated passwords before deployment.

Generate a production-ready secrets env file:
```bash
cd architecture/examples

# Keys that require hex-encoded values (encryption keys, not passwords)
HEX_KEYS="HeatAuthEncryptionKey"

# Generate a unique random value for each CHANGEME_REQUIRED entry
while IFS='=' read -r key value; do
  if [ "$value" != "CHANGEME_REQUIRED" ]; then
    echo "${key}=${value}"
  elif echo "$HEX_KEYS" | grep -qw "$key"; then
    echo "${key}=$(openssl rand -hex 32)"
  else
    echo "${key}=$(openssl rand -hex 16)"
  fi
done < ../lib/control-plane/base/osp-secrets.env > osp-secrets.env
```

Create the secret manually before deploying the control plane:
```bash
oc create secret generic osp-secret \
  --from-env-file=osp-secrets.env \
  -n openstack
```

> **NOTE**: `BarbicanSimpleCryptoKEK` is not included in `osp-secrets.env`.
> It is injected at deploy time by ci-framework or generated separately for
> install_yamls flows.

> **WARNING**: The `CHANGEME_REQUIRED` sentinel values are placeholders.
> Replace every value with a securely generated password before deploying.

## Dataplane Secrets (libvirt-secret)

The dataplane nodeset references a Kubernetes Secret named `libvirt-secret`
that contains the libvirt password. The base template at
`lib/dataplane/nodeset/libvirt-secret.env` ships with a `CHANGEME_REQUIRED`
sentinel that **must** be replaced with a securely generated password before
deployment.

Generate a production-ready libvirt secrets env file:
```bash
cd architecture
echo "LibvirtPassword=$(openssl rand -hex 16)" \
  > lib/dataplane/nodeset/libvirt-secret.env
```

Create the secret manually before deploying the dataplane:
```bash
oc create secret generic libvirt-secret \
  --from-env-file=lib/dataplane/nodeset/libvirt-secret.env \
  -n openstack
```

> **WARNING**: The `CHANGEME_REQUIRED` sentinel value is a placeholder.
> Replace it with a securely generated password before deploying.

## OLM
The [olm](olm) directory contains a kustomization which will generate
Namespace, OperatorGroup, and Subscription CRs. Creating these CRs
will install the base OpenStack K8s operator.

Observe CRs which will be generated.
```
kustomize build examples/common/olm/
```
Create the CRs.
```
oc apply -k examples/common/olm/
```
The following commands can be used to confirm that each step of this
procedure is complete.
```
while ! (oc get pod --no-headers=true -l openstack.org/operator-name=openstack-init -n openstack-operators | grep -E "(controller-operator|operator-controller)"); do sleep 10; done
oc wait pod -n openstack-operators --for condition=Ready -l openstack.org/operator-name=openstack-init --timeout=300s
while ! (oc get pod --no-headers=true -l name=cert-manager-operator -n cert-manager-operator | grep "cert-manager-operator"); do sleep 10; done
oc wait pod -n cert-manager-operator --for condition=Ready -l name=cert-manager-operator --timeout=300s
while ! (oc get pod --no-headers=true -l app=cainjector -n cert-manager | grep "cert-manager-cainjector"); do sleep 10; done
oc wait pod -n cert-manager -l app=cainjector --for condition=Ready --timeout=300s
while ! (oc get pod --no-headers=true -l app=webhook -n cert-manager | grep "cert-manager-webhook"); do sleep 10; done
oc wait pod -n cert-manager -l app=webhook --for condition=Ready --timeout=300s
while ! (oc get pod --no-headers=true -l app=cert-manager -n cert-manager | grep "cert-manager"); do sleep 10; done
oc wait pod -n cert-manager -l app=cert-manager --for condition=Ready --timeout=300s

timeout 300 bash -c "while ! (oc get pod --no-headers=true -l control-plane=controller-manager -n metallb-system | grep metallb-operator-controller); do sleep 10; done"
oc wait pod -n metallb-system --for condition=Ready -l control-plane=controller-manager --timeout=300s
timeout 300 bash -c "while ! (oc get pod --no-headers=true -l component=webhook-server -n metallb-system | grep metallb-operator-webhook); do sleep 10; done"
oc wait pod -n metallb-system --for condition=Ready -l component=webhook-server --timeout=300s

timeout 300 bash -c "while ! (oc get deployments/nmstate-operator -n openshift-nmstate); do sleep 10; done"
oc wait deployments/nmstate-operator -n openshift-nmstate --for condition=Available --timeout=300s
```

# MetalLB

Observe CRs which will be generated.
```
kustomize build examples/common/metallb/
```
Create the CRs.
```
oc apply -k examples/common/metallb/
```
The following commands can be used to confirm that each step of this
procedure is complete.
```
timeout 300 bash -c "while ! (oc get pod --no-headers=true -l component=speaker -n metallb-system | grep speaker); do sleep 10; done"
oc wait pod -n metallb-system -l component=speaker --for condition=Ready --timeout=300s
```

# NMState

Observe CRs which will be generated.
```
kustomize build examples/common/nmstate/
```
Create the CRs.
```
oc apply -k examples/common/nmstate/
```
The following commands can be used to confirm that each step of this
procedure is complete.
```
timeout 300 bash -c "while ! (oc get pod --no-headers=true -l component=kubernetes-nmstate-handler -n openshift-nmstate| grep nmstate-handler); do sleep 10; done"
oc wait pod -n openshift-nmstate -l component=kubernetes-nmstate-handler --for condition=Ready --timeout=300s
timeout 300 bash -c "while ! (oc get deployments/nmstate-webhook -n openshift-nmstate); do sleep 10; done"
oc wait deployments/nmstate-webhook -n openshift-nmstate --for condition=Available --timeout=300s
```

# OpenStack

The [openstack](openstack) directory contains a kustomization which will generate
the `OpenStack` initialization CR.  Creating this CR will install the remaining
OpenStack K8s operators.

Observe CRs which will be generated.
```
kustomize build examples/common/openstack/
```
Create the CRs.
```
oc apply -k examples/common/openstack/
```
The following command can be used to confirm that each step of this
procedure is complete.
```
oc wait -n openstack-operators openstack openstack --for condition=Ready --timeout=300s
```