# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to the bmo01 directory

```bash
cd architecture/examples/dt/bmo01
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
