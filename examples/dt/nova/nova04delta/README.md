# Nova GPU Passthrough (VFIO)

This directory contains the necessary configurations to deploy OpenStack with Nova configured for full GPU device passthrough (VFIO). This setup allows entire physical GPUs on compute nodes to be passed directly to virtual machines, providing near-native performance. Nova control plane is configured for requesting PCI devices from Placement.

## Overview

This configuration performs the following actions:

1.  **Host Kernel Configuration**: It configures the compute node's kernel to enable IOMMU and bind specific GPUs to the `vfio-pci` driver, preventing the host from using them.
2.  **Nova Scheduler Configuration**: It configures the Nova scheduler to be aware of the PCI devices available for passthrough.
3.  **Nova Compute Configuration**: It whitelists the passthrough-capable GPUs in Nova on the compute nodes.

Unlike SR-IOV or mdev (mediated device) setups, this configuration does not require installing the NVIDIA driver on the host. The driver is only installed inside the guest VM that consumes the GPU.

## Host Configuration (`examples/dt/nova/nova04delta/edpm/nodeset/values.yaml`)

The following parameters are crucial for host-level configuration:

*   **BareMetalHost configuration**: `baremetalhosts` section contains information required by metal3 to provision baremetal nodes.
    *   `bmc.address`: The IP address of the Baseboard Management Controller (BMC).
    *   `bootMACAddress`: The MAC address of the network interface that the node will use to PXE boot.
    *   `rootDeviceHints`: Hints for Metal3 to identify the root device for the OS installation.
    *   `preprovisioningNetworkData`: Static nmstate network config to be applied to a `BaremetalHost` via ironic-python-agent ramdisk during provisioning. The config is embedded in the ISO attached as virtual media via the BMC, so no DHCP is required.
    *   `baremetalHostsNetworkData`: Final nmstate network configuration for EDPM nodes.

*   `edpm_kernel_args`: Appends necessary kernel arguments for VFIO passthrough.
    *   `intel_iommu=on iommu=pt`: Enables the IOMMU for device passthrough.
    *   `vfio-pci.ids=10de:20f1`: Instructs the `vfio-pci` driver to claim the specified GPU(s) by their vendor and product IDs at boot time. The example IDs `10de:20f1` are for an NVIDIA A100 GPU.
    *   `rd.driver.pre=vfio-pci`: Avoids race conditions during boot by loading vfio-pci kernel module early.

*   `edpm_tuned_profile` and `edpm_tuned_isolated_cores`: These parameters configure the `tuned` service.
    *   `edpm_tuned_profile` is set to `cpu-partitioning-powersave` to enable CPU isolation features.
    *   `edpm_tuned_isolated_cores` specifies the cores to be isolated. For CPU isolation we strongly recommend using the Tuned approach rather than `isolcpus` kernel argument.

*   **VFIO-PCI Binding Service**: The `vfio-pci-bind` service in `dt/nova/nova04delta/edpm/nodeset/nova_gpu.yaml` blacklists the `nouveau` and `nvidia` kernel modules to ensure they do not interfere with the `vfio-pci` driver. The service also regenerates the initramfs and grub configuration to apply these changes. A reboot is required for these changes to take effect.

## Nova Configuration

A count of `X` PCI devices may be requested through `"pci_passthrough:alias"="nvidia_a2:X"` flavor extra specs:
```
$ openstack --os-compute-api=2.86 flavor set --property "pci_passthrough:alias"="nvidia_a2:1" device_passthrough
```

### Control Plane (`examples/dt/nova/nova04delta/control-plane/service-values.yaml`)

See [README.md](control-plane/README.md) for deployment instructions.
There are most essential configuration values to define:

*   `[pci]alias`: Creates an alias for a specific GPU type. This allows users to request a GPU by a friendly name (e.g., `nvidia_a2`) when creating a VM. This configuration should match the configuration found on the compute nodes.
    ```yaml
    nova:
      apiServiceTemplate:
        customServiceConfig: |
          [pci]
          alias = { "vendor_id":"10de", "product_id":"20f1", "device_type":"type-PF", "name":"nvidia_a2" }
    ```
*   `[filter_scheduler]pci_in_placement`: Enables PCI in Placement. It should only be enabled after all the computes in the system become configured to report PCI inventory in Placement via enabling `[pci]report_in_placement` in EDPM nodesets configuration. However, this order must be ensured during major upgrades only, where the dataplane deployment to upate EDPM computes configurataion must come before reconfiguring control plane resources.
*   `device_type` in the alias is dependent on the actual hardware:
    *   `type-PF`: The device supports SR-IOV and is the parent or root device.
    *   `type-VF`: The device is a child device of a device that supports SR-IOV.
    *   `type-PCI`: The device does not support SR-IOV.

### Compute Node (`examples/dt/nova/nova04delta/edpm/nodeset/values.yaml`)

See [dataplane section](data-plane.md) for deployment instructions.
There are most essential configuration values to define:

*   `[pci]report_in_placement`: Required for PCI in placement to work.
*   `[pci]device_spec`: Whitelists the physical GPUs that are available for passthrough. You must create a `device_spec` entry for each physical GPU you want to make available. For example:
    ```yaml
    nova:
      pci:
        conf: |
          [pci]
          device_spec = { "vendor_id":"10de", "product_id":"20f1", "address": "0000:04:00.0" }
          device_spec = { "vendor_id":"10de", "product_id":"20f1", "address": "0000:82:00.0" }
          alias = { "vendor_id":"10de", "product_id":"20f1", "device_type":"type-PF", "name":"nvidia_a2" }
    ```

In addition to PCI device configuration, the `nova.compute.conf` section includes parameters for resource management on the compute node:

*   `[DEFAULT]reserved_host_memory_mb`: Specifies the amount of memory (in megabytes) to reserve for the host operating system and other non-OpenStack services. This memory will not be available for allocation to virtual machines.
*   `[compute]cpu_shared_set`: A list of physical CPUs that are available for host processes and for virtual machines that do not have dedicated CPUs (i.e., unpinned VMs). These should be the CPUs that are **not** isolated by `edpm_tuned_isolated_cores`.
*   `[compute]cpu_dedicated_set`: A list of physical CPUs that are exclusively reserved for virtual machines with dedicated CPU pinning policies. To ensure performance isolation, this list should correspond directly to the CPUs isolated using `edpm_tuned_isolated_cores` parameter.
*   `[DEFAULT]reserved_huge_pages`: Defines the number and size of huge pages to reserve for the host, making them unavailable for guest VMs. This configuration works in conjunction with the `hugepages` and `hugepagesz` kernel arguments, which define the total pool of huge pages on the host.

**Note**: In a full device passthrough scenario, the `[devices]enabled_vgpu_types` option in Nova's configuration is not used. This option is specific to mediated device (mdev) configurations.

## Guest VM

To use the passthrough GPU, the guest operating system inside the VM must have the appropriate native NVIDIA driver installed. You will need a standard NVIDIA driver. Do not use vGPU-enabled guest drivers. The GPU will appear as a physical PCI device within the guest.
