# Nova GPU Passthrough (VFIO) on DCN with CephHCI

This is a collection of CR templates that represent a Red Hat OpenStack Services on OpenShift deployment that has the following characteristics:

- Single Node OpenShift (SNO) cluster with external EDPM compute nodes
- 1-replica Galera database
- RabbitMQ
- OVN networking with spine-and-leaf topology (multi-subnet DCN)
- Baremetal compute nodes with GPU passthrough via VFIO
- CephHCI installed on compute nodes and used by various OSP services
  - Glance using RBD for backend
  - Nova using RBD for ephemeral storage
- Nova configured for PCI device passthrough (NVIDIA GPUs)
  - Host kernel configured with IOMMU and vfio-pci driver
  - GPU PCI alias registered in Placement for scheduling
  - CPU pinning and tuned profile for performance isolation
- Metal3 bare metal provisioning with virtual media

## Considerations

1. These CRs are validated for the overall functionality of the OSP cloud deployed, but they nonetheless require customization for the particular environment in which they are utilized. In this sense they are _templates_ meant to be consumed and tweaked to fit the specific constraints of the hardware available.

2. The CRs are applied against an OpenShift cluster in _stages_. That is, there is an ordering in which each grouping of CRs is fed to the cluster. It is _not_ a case of simply taking all CRs from all stages and applying them all at once.

3. In stage 2 [kustomize](https://kustomize.io/) is used to generate the networking and control plane CRs dynamically. The `control-plane/networking/nncp/values.yaml`, `control-plane/networking/dns/values.yaml` and `control-plane/service-values.yaml` files must be updated to fit your environment. kustomize version 5 or newer required.

4. In stages 3 and 4 [kustomize](https://kustomize.io/) is used to generate the dataplane CRs dynamically. The `edpm-pre-ceph/nodeset/values.yaml`, `values.yaml` and `service-values.yaml` files must be updated to fit your environment. kustomize version 5 or newer required.

5. Between stages 3 and 4, _it is assumed that the user installs Ceph on the compute nodes._ OpenStack K8S CRDs do not provide a way to install Ceph via any sort of combination of CRs.

6. For CI automation, this DT uses `automation/vars/nova05epsilon.yaml` which maps the manual stages above to 9 granular automation steps (NNCP, networking, control-plane, DNS, baremetalhosts, pre-ceph nodeset, pre-ceph deployment, post-ceph nodeset, post-ceph deployment).

## Host Configuration

The following parameters are crucial for host-level GPU passthrough configuration in `edpm-pre-ceph/nodeset/values.yaml`:

- **`edpm_kernel_args`**: Enables IOMMU and binds NVIDIA GPUs to the `vfio-pci` driver at boot time.
  - `intel_iommu=on iommu=pt`: Enables the IOMMU for device passthrough.
  - `vfio-pci.ids=10de:20f1`: Claims GPU(s) by vendor and product IDs.
  - `rd.driver.pre=vfio-pci`: Loads vfio-pci early to avoid race conditions.

- **`edpm_tuned_profile`** and **`edpm_tuned_isolated_cores`**: Configure CPU isolation for performance.

- **`vfio-pci-bind` service**: Blacklists `nouveau` and `nvidia` kernel modules and regenerates initramfs.

## Nova Configuration

A count of `X` PCI devices may be requested through `"pci_passthrough:alias"="nvidia_a2:X"` flavor extra specs:
```
openstack --os-compute-api=2.86 flavor set --property "pci_passthrough:alias"="nvidia_a2:1" device_passthrough
```

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the initial data plane to prepare for Ceph installation](dataplane-pre-ceph.md)
4. [Update the control plane and finish deploying the data plane after Ceph has been installed](dataplane-post-ceph.md)
