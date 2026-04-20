# Configure and deploy the pre-Ceph data plane (Ironic-provisioned)

## Prerequisites

- BareMetalHost CRs must exist in `openshift-machine-api` namespace
  for each compute node.
- The Bare Metal Operator webhook must be healthy
  (`oc get endpoints baremetal-operator-webhook-service -n openshift-machine-api`
  should show at least one address).

## Procedure

### 1. Customize the pre-Ceph nodeset values

Edit
[`edpm-pre-ceph/nodeset/values.yaml`](edpm-pre-ceph/nodeset/values.yaml)
to match your environment.  Key fields:

- `data.preProvisioned`: must be `false`.
- `data.baremetalSetTemplate.osImage`: qcow2 image to provision
  (e.g. `edpm-hardened-uefi.qcow2`).
- `data.baremetalSetTemplate.bmhLabelSelector`: labels to select the
  BareMetalHost CRs for this NodeSet.
- `data.nodeset.nodes`: IP addresses and hostnames for each compute.
- `data.nodeset.ansible.ansibleVars.edpm_bootstrap_command`: commands
  to run on nodes after provisioning (repo setup, user creation, etc.).

### 2. Build and apply the NodeSet

```bash
kustomize build examples/va/hci-ironic/edpm-pre-ceph/nodeset > nodeset-pre-ceph.yaml
oc apply -f nodeset-pre-ceph.yaml
```

### 3. Wait for Ironic provisioning to complete

```bash
oc -n openstack wait osdpns openstack-edpm \
  --for condition=SetupReady --timeout=30m
```

This takes longer than the pre-provisioned variant because Ironic must
boot each node from the qcow2 image via virtual media.

### 4. Continue with the standard HCI pre-Ceph deployment

Once the NodeSet is `SetupReady`, follow the deployment steps from the
standard HCI guide starting at
[Deploy the pre-Ceph data plane](../hci/dataplane-pre-ceph.md).
