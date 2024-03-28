# Configuring networking and deploy the OpenStack control plane
This topology uses the copy of control-plane CR present in adoption repo.

## Assumptions

- A storage class called `local-storage` should already exist.
- This topology uses the copy of control-plane CR present in adoption repo (https://github.com/openstack-k8s-operators/data-plane-adoption) and does not depend on architecture repo to generate Controlplane and Dataplane CR's.

## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to the adoption directory

```bash
cd data-plane-adoption/tests/
```

Control-plane CRs will be created as part of test-minimal test suite execution.
```bash
make test-minimal
```

Wait for control plane to be available

```bash
oc wait osctlplane openstack --for condition=Ready --timeout=600s
oc wait osdpd openstack --for condition=Ready --timeout=1800s
```
