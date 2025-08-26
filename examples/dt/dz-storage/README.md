# Distributed Zones with BGP and third party storage

This Deployed Topology (DT) is the same as [bgp-l3-xl](../bgp-l3-xl)
but it also has the following:

- Three zones:
  - zone A CoreOS: ocp-worker-0 ocp-worker-1 ocp-worker-2, ocp-master-0
  - zone B CoreOS: ocp-worker-3 ocp-worker-4 ocp-worker-5, ocp-master-1
  - zone C CoreOS: ocp-worker-6 ocp-worker-7 ocp-worker-8, ocp-master-2
  - zone A RHEL: r0-compute-0, r0-compute-1, r0-networker-0, leaf-0, leaf-1
  - zone B RHEL: r1-compute-0, r1-compute-1, r1-networker-0, leaf-2, leaf-3
  - zone C RHEL: r2-compute-0, r2-compute-1, r2-networker-0, leaf-4, leaf-5
- [Toplogy CRDs](https://github.com/openstack-k8s-operators/infra-operator/pull/325) are
  used to either spread pods accross zones or keep them within a zone.
- Self Node Remediation and Node Health Checks
- It is assumed that a Storage Array is physically located in each of the zones.
  This examples uses a NetApp as an iSCSI backend for Cinder and an NFS backend for Manila.
- Glance uses Cinder as its backend and is configured with multiple stores
- There is a separate cinder-volume and manila-share service per zone

The CRs included within this DT should be applied on an environment
where EDPM and OCP nodes are connected through a spine/leaf
network. The BGP protocol should be enabled on those spine and leaf
routers. See [bgp-l3-xl](../bgp-l3-xl) for information about
the BGP Dynamic Routing configuration.

worker-9 is tained so that regular openstack workloads are not
scheduled on it. It is not included into any rack or zone. It
is not connected to any leaves, but to a router connected to
the spines. It exists for running tests from outside.

## Prerequisites

- Chapters 2 and 6 from
[Self Node Remdiation and Node Health Checks](https://docs.redhat.com/en/documentation/workload_availability_for_red_hat_openshift/24.4/html-single/remediation_fencing_and_maintenance)
have been completed so that when the Node Health Check (NHC) Operator
detects an unhealthy node, it creates a Self Node Remediation (SNR) CR
with the `Automatic` strategy (which will taint an unhealthy node so
that its pods are rescheduled).

- A storage class has been created. If [LVMS](https://docs.redhat.com/en/documentation/openshift_container_platform/4.16/html/storage/configuring-persistent-storage#persistent-storage-using-lvms)
is used, then if a node fails, the system does not allow the attached
volume to be mounted on a new node because it is already assigned to
the failed node. This prevents SNR from rescheduling pods with PVCs.

## Considerations

### Networking

See the "Considerations/Constraints" section of [bgp-l3-xl](../bgp-l3-xl)

### Block Storage Access

#### Local Access

In this example there is a storage array in each availability zone and a cinder-volume service pod is deployed on worker nodes in the same zone, i.e. local to that array. For example, in AZ1 the storage array with IP address 10.1.0.6 is on the local storage network 10.1.0.0/24 and a cinder-volume pod for AZ1 is configured on a worker node with access to that storage network. Compute nodes in AZ1 should be on the same network and have access to the same array.

#### Remote Access

It is also necessary for the storage array in each zone to be accessible by worker nodes in remote zones. For example, the glance pod in AZ1 is configured with multiple stores including the cinder-volume service in local AZ1 and the cinder-volume service in remote AZ2. This access is necessary so that an image may be uploaded to the glance store in AZ1 and then copied to the glance store in AZ2. The same access is also required to retype volumes between zones.

The example here uses iSCSI and IP routing can be configured to support the remote access described above. If FC is used in place of iSCSI, then the switches need to be zoned to support the same types of remote and local access.

### File Storage Access

#### Local Access

In this example there is a storage array in each availability zone and a manila-share service pod is deployed on worker nodes local to that array. For example, in AZ1 the storage array with IP address 10.1.0.6 is on the local storage network 10.1.0.0/24 and a manila-share pod for AZ1 is configured on a worker node with access to that storage network. Compute nodes in AZ1 should be on the same network and have access to the same array if they will use the shares hosted on that array.

#### Remote Access

It is also possible for the storage array in each zone to be accessible by  worker nodes in remote zones. For example, access could be granted to a share which is hosted in AZ1 to Nova instances which are hosted in AZ2. It’s possible that network latency between availability zones might affect storage performance. It’s up to the administrator to grant access to shares to ensure only local access or allow remote access.

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Configure taints on the OCP worker](configure-taints.md)
2. [Disable RP filters on OCP nodes](disable-rp-filters.md)
3. [Install the OpenStack K8S operators and their dependencies](../../common/)
4. [Apply metallb customization required to run a speaker pod on the OCP tester node](metallb/)
5. [Define Zones and Toplogies](topology/)
6. [Configure networking and deploy the OpenStack control plane with storage](control-plane.md)
7. [Create BGPConfiguration after controplane is deployed](bgp-configuration.md)
8. [Configure and deploy the dataplane - networker and compute nodes](data-plane.md)
9. [Validate Distributed Zone Storage](validate.md)
