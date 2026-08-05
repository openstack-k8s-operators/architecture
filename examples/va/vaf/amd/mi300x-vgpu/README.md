# Validated Architecture — AMD Instinct MI300X vGPU (GIM SR-IOV)

This example VA helps you to install Red Hat OpenStack Services on OpenShift (RHOSO)
with AMD Instinct MI300X accelerators exposed to tenant VMs as vGPU slices using the
AMD GIM (Guest Isolated Mode) SR-IOV driver on a pre-provisioned RHEL 9.6 EDPM host.
Tenant VMs access MI300X vGPU slices via the `mi300x-vf` PCI alias.

## Overview

| Item | Value |
|---|---|
| GPU | AMD Instinct MI300X |
| Driver | AMD GIM — gim.ko |
| vGPU mechanism | SR-IOV Virtual Functions (type-VF) |
| Nova PCI alias | `mi300x-vf` |
| VF vendor/product | 1002:74b5 |
| EDPM provisioning | Pre-provisioned (no BareMetalHost/Metal3) |
| Control plane | OCP 4.18 |
| Storage | LVM Storage Operator |

## Architecture

GIM manages the MI300X Physical Function (PF, 1002:74a1). It creates SR-IOV Virtual
Functions (VFs, 1002:74b5) — one hardware-partitioned vGPU slice per VF. `amdgpu` is
blacklisted and must not bind to any PF or VF. VFs are bound to `vfio-pci` so Nova and
libvirt can assign them to tenant instances.

## Pre-requisites

### 1. AMD GIM driver requirements on the EDPM host

Manually install the GIM kernel module (`gim.ko`) on the EDPM host before
applying the dataplane nodeset using your organisation's delivery method
(see [amd/MxGPU-Virtualization](https://github.com/amd/MxGPU-Virtualization)).

| What | Done by |
|---|---|
| Blacklist `amdgpu` | `vfio-pci-bind` EDPM service |
| Auto-load `gim`, `vfio`, `vfio-pci` at boot | `vfio-pci-bind` EDPM service |
| Set `gim vf_num` option | `vfio-pci-bind` EDPM service |
| Kernel args | `configure-os` / `run-os` via `edpm_kernel_args` |
| Regenerate initramfs + GRUB | `vfio-pci-bind` EDPM service |

Verify the module is available before deploying:

```bash
modinfo gim
```

To have EDPM install the GIM RPM automatically, add `install-amd-gim` to
the nodeset services list before `vfio-pci-bind`, and configure
`edpm_accel_drivers_nvidia_custom_url` or `edpm_accel_drivers_nvidia_repo_*`
and `edpm_accel_drivers_nvidia_package_name` in `edpm/nodeset/values.yaml`.
Ignore the nvidia-specific variables names - it works the same way for AMD
in RHOSO 18.0.17 (FR5) / OpenStack Operator 1.0.20.

> **NOTE**: there is no validated RPM source for RHEL 9.6 that you can use with `install-amd-gim`
> service today. Installing with DKMS or building drivers on the EDPM host is unsupported.

### 2. Kustomize / oc CLI

Requires `oc` CLI ≥ 4.14 (which bundles kustomize v5).

### 3. Fill in CHANGEME values

Edit the following files and replace `CHANGEME*` markers before building with kustomize:

| File | What to set |
|---|---|
| `nncp/values.yaml` | OCP node name/IP, network CIDRs, VLANs, MetalLB ranges, DNS, RabbitMQ IPs |
| `service-values.yaml` | Nova PCI alias, scheduler config, Neutron ML2, OVN mappings, Glance, Swift |
| `edpm/nodeset/values.yaml` | SSH keys, host FQDN, ansibleHost IP, NIC MACs, PCI slot BDFs, kernel args |

### 4. StorageClass

Create `StorageClass` before applying the control plane. For that, you can deploy an `LVMCluster` CR
targeting an unformatted partition. Verify results with:

```bash
oc get storageclass lvms-vg1
```

Then use this `lvms-vg1` name instead of `CHANGEME_STORAGE_CLASS`.

## Stages

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Configure networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the dataplane](dataplane.md)
4. Create flavor and VM instance
5. Install guest drivers.

## Workloads

Create a vGPU flavor, for example:

```bash
# Flavor with 1 MI300X VF
openstack flavor create mi300x-vf-1 \
  --ram 32768 --vcpus 8 --disk 100 \
  --property "pci_passthrough:alias"="mi300x-vf:1"
```

Create a VM and verify the VF is visible inside:

```bash
lspci -nn | grep 1002:74b5   # → MI300X VF
```

Install ROCm or AMD compute drivers as needed for GPU workloads.
