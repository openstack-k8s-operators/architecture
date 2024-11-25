# OpenShift on OpenStack (IPv6)

This is a collection of CR templates that represent a validated Red Hat
OpenStack Services on OpenShift deployment following the recommendations from
the [OpenShift on OpenStack reference
architecture](https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.2/html-single/reference_architecture_for_deploying_red_hat_openshift_container_platform_on_red_hat_openstack_platform/index). It has the following characteristics:

- 3 master/worker combo-node OpenShift cluster
- 3-replica Galera database
- RabbitMQ
- OVN networking
- Network isolation over a single NIC
- 3 compute nodes
- CephHCI installed on compute nodes and used by various OSP services
    - Cinder Volume using RBD for backend
    - Cinder Backup using RBD for backend
    - Glance using RBD for backend
    - Object Storage via Rados GW
    - Manila using CephFS through NFS (ganesha) for backend
- Nova ephemeral using local storage
- Octavia with Amphora provider


## Considerations

1. These CRs are validated for the overall functionality of the OSP cloud deployed, but they nonetheless require customization for the particular environment in which they are utilized.  In this sense they are _templates_ meant to be consumed and tweaked to fit the specific constraints of the hardware available.

2. The CRs are applied against an OpenShift cluster in _stages_.  That is, there is an ordering in which each grouping of CRs is fed to the cluster.  It is _not_ a case of simply taking all CRs from all stages and applying them all at once.

3. In stages 1 and 2 [kustomize](https://kustomize.io/) is used to genereate the control plane CRs dynamically. The `control-plane/nncp/values.yaml` file(s) must be updated to fit your environment. kustomize version 5 or newer required.

4. In stages 3 and 4 [kustomize](https://kustomize.io/) is used to generate the dataplane CRs dynamically. The `edpm-pre-ceph/values.yaml`, `values.yaml` and `service-values.yaml` files must be updated to fit your environment. kustomize version 5 or newer required.

5. Between stages 3 and 4, _it is assumed that the user installs Ceph on the 3 OSP compute nodes._  OpenStack K8S CRDs do not provide a way to install Ceph via any sort of combination of CRs.

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the initial data plane to prepare for Ceph installation](dataplane-pre-ceph.md)
4. [Update the control plane and finish deploying the data plane after Ceph has been installed](dataplane-post-ceph.md)
