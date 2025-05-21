# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to the uni-beta directory

```bash
cd architecture/examples/dt/uni02beta
```

Edit [control-plane/service-values.yaml](control-plane/service-values.yaml) and
[control-plane/networking/nncp/values.yaml](control-plane/networking/nncp/values.yaml).

Apply node network configuration

```bash
pushd control-plane/networking/nncp
kustomize build > nncp.yaml
oc apply -f nncp.yaml
oc wait nncp \
    -l osp/nncm-config-types=standard \
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

Verify that control-plane.yaml includes the sensitive access credentials for NetApp storage
by confirming the information is applied to the output file.

```bash
oc apply -f control-plane.yaml
popd
```

Wait for control plane to be available

```bash
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```
