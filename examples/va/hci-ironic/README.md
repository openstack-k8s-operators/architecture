# Hyperconverged OpenStack and Ceph with Ironic-Provisioned Compute Nodes

This is a variant of the [HCI validated architecture](../hci/README.md)
where all compute nodes are provisioned via Ironic rather than being
pre-provisioned.  It is intended for validating `edpm-hardened-uefi` qcow2
images through a complete deployment cycle using virtual baremetal
(Sushy-emulated BareMetalHost resources).

## Differences from the standard HCI VA

| Aspect | Standard HCI | HCI-Ironic |
|--------|-------------|------------|
| Compute provisioning | Pre-provisioned (`preProvisioned: true`) | Ironic-provisioned (`preProvisioned: false`) |
| NodeSet | Uses `lib/dataplane/nodeset` | Uses `lib/dataplane/nodeset` + `lib/dataplane/nodeset-baremetal` |
| OS image | Host OS from reproducer VM image | Configurable `baremetalSetTemplate.osImage` (e.g. `edpm-hardened-uefi.qcow2`) |
| BareMetalHost CRs | Not required | Required (created by `deploy_bmh` role with `cifmw_config_bmh: true`) |
| Values | `examples/va/hci/edpm-pre-ceph/nodeset/values.yaml` | `examples/va/hci-ironic/edpm-pre-ceph/nodeset/values.yaml` |

All other stages (NNCP, networking, control plane, pre-ceph deployment,
Ceph bootstrap, post-ceph nodeset/deployment) are identical to the
standard HCI VA and reuse the same paths under `examples/va/hci/`.

## Stages

All stages must be executed in the order listed below.

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Configuring networking and deploy the OpenStack control plane](../hci/control-plane.md)
3. [Configure and deploy the pre-Ceph data plane with Ironic provisioning](dataplane-pre-ceph.md)
4. [Update the control plane and finish deploying the data plane after Ceph has been installed](../hci/dataplane-post-ceph.md)

## Pre-Ceph Data Plane (Ironic variant)

Stage 3 differs from the standard HCI flow.  The `edpm-pre-ceph/nodeset`
values include:

- `preProvisioned: false` -- tells the dataplane operator to provision
  nodes via Ironic instead of assuming they are already running.
- `baremetalSetTemplate` -- configures the Ironic provisioning parameters:
  - `osImage`: the qcow2 image name from the `edpm-hardened-uefi` container
    (e.g. `edpm-hardened-uefi.qcow2` for RHEL 9.4 or
    `edpm-hardened-uefi-9.6.qcow2` for RHEL 9.6).
  - `bmhLabelSelector`: selects which BareMetalHost CRs to claim.
  - `bmhNamespace`: namespace where BareMetalHost CRs reside.

BareMetalHost CRs must exist before the NodeSet is applied.  In CI this
is handled by the `deploy_bmh` role (enabled via `cifmw_config_bmh: true`).

### Build the pre-Ceph NodeSet CR

```bash
kustomize build examples/va/hci-ironic/edpm-pre-ceph/nodeset > nodeset-pre-ceph.yaml
```

Review and apply:

```bash
oc apply -f nodeset-pre-ceph.yaml
oc -n openstack wait osdpns openstack-edpm --for condition=SetupReady --timeout=30m
```

The longer timeout (30m vs 10m for pre-provisioned) accounts for Ironic
node provisioning time.

After the NodeSet is ready, continue with the standard HCI pre-Ceph
deployment and subsequent stages as documented in the
[HCI dataplane-pre-ceph guide](../hci/dataplane-pre-ceph.md#deploy-the-pre-ceph-data-plane).
