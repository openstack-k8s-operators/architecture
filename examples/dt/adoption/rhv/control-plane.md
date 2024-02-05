# Configuring networking and deploy the OpenStack control plane
This topology uses the copy of control-plane CR present in adoption repo.

## Assumptions

- A storage class called `local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to the adoption directory

```bash
cd data-plane-adoption/tests/config/base/
```

Generate the control-plane CRs.

```bash
kustomize build > openstack_control_plane.yaml
```

## Create CRs

```bash
oc apply -f openstack_control_plane.yaml
```

Wait for control plane to be available

```bash
oc wait osctlplane openstack --for condition=Ready --timeout=600s
```
