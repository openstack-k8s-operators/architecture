# Validated Architecture - Nvidia GPU Passthrough (VFIO)

This document describes the CR's and deployment workflow to create an
environment with EDPM Compute Nodes capable of supplying Nvidia GPUs via
passthrough (VFIO). This setup allows entire physical GPUs on compute nodes to
be passed directly to virtual machines, providing near-native performance.
EDPM Compute node is provisioned by BMO via virtual-media.

## Purpose

This topology is used for e2e verification of environments that provide Nvidia GPU
passthrough and to confirm guests are able to take advantage of the resource
correctly. It should be noted that this type of deployment cannot be simulated
with nested virtualization and requires real baremetal hosts.

## Environment

### Nova

Nova control plane is configured for requesting PCI devices from Placement.

### Guest VM

To use the passthrough GPU, the guest operating system inside the VM must have
the appropriate NVIDIA driver installed. You will need a standard guest NVIDIA
driver or advanced drivers, like GRID. The GPU will appear as a physical
PCI device within the guest.

### Host Configuration (`examples/va/nvidia-vfio-passthrough/edpm/nodeset/values.yaml`)

The following parameters are crucial for host-level configuration:

*   **BareMetalHost configuration**: `baremetalhosts` section contains information required by metal3 to provision baremetal nodes.
    *   `bmc.address`: The IP address of the Baseboard Management Controller (BMC).
    *   `bootMACAddress`: The MAC address of the network interface that the node will use to PXE boot.
    *   `rootDeviceHints`: Hints for metal3 to identify the root device for the OS installation.
    *   `preprovisioningNetworkData`: Static nmstate network config to be applied to a `BaremetalHost` via ironic-python-agent ramdisk during provisioning. The config is embedded in the ISO attached as virtual media via the BMC, so no DHCP is required.
    *   `baremetalHostsNetworkData`: Final nmstate network configuration for EDPM nodes.

*   `edpm_kernel_args`: Appends necessary kernel arguments for VFIO passthrough.
    *   `intel_iommu=on iommu=pt`: Enables the IOMMU for device passthrough.
    *   `vfio-pci.ids=10de:20f1`: Instructs the `vfio-pci` driver to claim the specified GPU(s) by their vendor and product IDs at boot time. The example IDs `10de:20f1` are for an NVIDIA A100 GPU.
    *   `rd.driver.pre=vfio-pci`: Avoids race conditions during boot by loading vfio-pci kernel module early.

*   `edpm_tuned_profile` and `edpm_tuned_isolated_cores`: These parameters configure the `tuned` service.
    *   `edpm_tuned_profile` is set to `cpu-partitioning-powersave` to enable CPU isolation features.
    *   `edpm_tuned_isolated_cores` specifies the cores to be isolated. For CPU isolation we strongly recommend using the Tuned approach rather than `isolcpus` kernel argument.

*   **VFIO-PCI Binding Service**: The `vfio-pci-bind` service in `va/nvidia-vfio-passthrough/edpm/nodeset/nova_gpu.yaml` blacklists the `nouveau` and `nvidia` kernel modules to ensure they do not interfere with the `vfio-pci` driver. The service also regenerates the initramfs and grub configuration to apply these changes. A reboot is required for these changes to take effect.

### Nodes

| Role                        | Machine Type | Count |
| --------------------------- | ------------ | ----- |
| Compact OpenShift           | vm*          | 3     |
| OpenStack Baremetal Compute | Baremetal    | 1     |

\* OCP setup is not covered in this VA, but in the parent nova04delta DT.

#### VLAN networks in RH OSP

| Name        | Type        | CIDR              |
| ----------- | ----------- | ----------------- |
| ctlplane    | untagged    | 192.168.122.0/24  |
| internalapi | VLAN tagged | 172.17.0.0/24     |
| storage     | VLAN tagged | 172.18.0.0/24     |
| storagemgmt | VLAN tagged | 172.20.0.0/24     |
| tenant      | VLAN tagged | 172.19.0.0/24     |
| external    | untagged    | 10.0.0.0/24       |

A network attach definition is not provided for storagemgmt because only
RHEL EDPM nodes are going to use it, while control plane pods on OpenShift do
not need it.

Also the base DT configures the default gateway for external network instead of ctlplane.
It is attached to EDPM and CP to transfer virtual media traffic during BMO setup.

## Stages
All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane/README.md)
3. [Configure and deploy the initial dataplane](data-plane-pre.md)

Note that EDPM host will be rebooted to apply required changes to kernel arguments.