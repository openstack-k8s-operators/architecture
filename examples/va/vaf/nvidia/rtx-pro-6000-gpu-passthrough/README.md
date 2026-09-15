# Validated Architecture — NVIDIA RTX PRO 6000 GPU Passthrough (VFIO)

This example VA helps you to install Red Hat OpenStack Services on OpenShift (RHOSO)
with NVIDIA RTX PRO 6000 Blackwell Data Center GPUs assigned whole to tenant VMs
using full-device VFIO PCI passthrough on a BMO-provisioned RHEL 9.6 EDPM host.
Tenant VMs request a GPU via the `rtx-pro-6000` PCI alias.

## Overview

| Item | Value |
|---|---|
| GPU | NVIDIA RTX PRO 6000 Blackwell DC |
| Driver | None on host — `vfio-pci` claims the device |
| Passthrough mechanism | Full physical device (type-PF) |
| Nova PCI alias | `rtx-pro-6000` |
| GPU vendor/product | 10de:2bb5 |
| EDPM provisioning | BMO-provisioned (BareMetalHost / Metal3 via iDRAC virtual-media) |
| Reference hardware | Dell PowerEdge XE7740 |
| Control plane | OCP 4.18 |
| Storage | LVM Storage Operator |

## Architecture

Full-device passthrough assigns the entire physical GPU to a single guest. `nouveau` and `nvidia` are
blacklisted on the host and must not bind to the GPU; the device is claimed by
`vfio-pci` at boot (`vfio-pci.ids=10de:2bb5`) so Nova and libvirt can hand the
whole PF to a tenant instance. **No NVIDIA driver is installed on the host** — the
NVIDIA driver is installed inside the guest VM only.

This VA builds on the [nova04delta](../../../../dt/nova/nova04delta/) DT, which provides the control-plane composition (nova, neutron, glance,
swift, telemetry) and the EDPM GPU-passthrough services (`vfio-pci-bind`,
`nova-custom-gpu`).

## Pre-requisites

### 1. Host requirements on the EDPM node

Nothing to pre-install on the host for passthrough — the `vfio-pci-bind` EDPM
service and kernel args take care of claiming the GPU.

| What | Done by |
|---|---|
| Blacklist `nouveau` / `nvidia` | `vfio-pci-bind` EDPM service |
| Auto-load `vfio`, `vfio-pci` at boot | `vfio-pci-bind` EDPM service |
| Bind GPU to `vfio-pci` at boot | `edpm_kernel_args` (`vfio-pci.ids`, `rd.driver.pre=vfio-pci`) |
| Enable IOMMU | `edpm_kernel_args` (`intel_iommu=on iommu=pt`) |
| Regenerate initramfs + GRUB | `vfio-pci-bind` EDPM service |

After deploy, verify on the host that the GPU is bound to vfio-pci:

```bash
lspci -nnk -d 10de:2bb5   # Kernel driver in use: vfio-pci
```

### 2. Kustomize / oc CLI

Requires `oc` CLI ≥ 4.14 (which bundles kustomize v5).

### 3. StorageClass

Create a `StorageClass` before applying the control plane. For that, you can deploy an
`LVMCluster` CR targeting an unformatted partition — see
[Configuring LVM cluster and related CRs](../../../../dt/perfscale/scalelab/lvm-cluster.md).
List the resulting StorageClass with:

```bash
oc get storageclass
```

Then use its name instead of `CHANGEME_STORAGE_CLASS` in the next step.

### 4. Fill in CHANGEME values

Edit the following files and replace `CHANGEME*` markers before building with kustomize:

| File | What to set |
|---|---|
| `control-plane/networking/nncp/values.yaml` | OCP node name/IP, network CIDRs, VLANs, MetalLB ranges, DNS, RabbitMQ IPs |
| `control-plane/networking/dns/values.yaml` | ctlplane DNS zone and upstream resolver(s) |
| `control-plane/service-values.yaml` | Nova PCI alias, scheduler config, Neutron ML2, OVN mappings, Glance, Swift |
| `edpm/baremetalhosts/values.yaml` | BMC/iDRAC address, boot MAC, root device hints, host labels |
| `edpm/baremetalhosts/bmc-secret.env` | iDRAC username/password |
| `edpm/nodeset/values.yaml` | SSH keys, baremetalSetTemplate, NIC MACs, GPU PCI addresses, kernel args |

## Stages

1. [Install the OpenStack K8S operators and their dependencies](../../../../common/)
2. [Configure networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the dataplane](dataplane.md)
4. Create flavor and VM instance
5. Install guest driver.

## Workloads

Create a passthrough flavor, for example:

```bash
# Flavor with 1 RTX PRO 6000 GPU
openstack flavor create rtx-pro-6000-1 \
  --ram 32768 --vcpus 8 --disk 100 \
  --property "pci_passthrough:alias"="rtx-pro-6000:1"
```

Create a VM and verify the GPU is visible inside:

```bash
lspci -nn | grep 10de:2bb5   # → RTX PRO 6000
```

Install the NVIDIA driver in the guest.
The GPU appears as a physical PCI device inside the VM.
