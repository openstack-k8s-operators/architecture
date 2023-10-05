# Openstack K8S Validated Architecture One

**Based on OpenStack K8S operators from the "main" branch of the github.com/openstack-k8s-operators/openstack-operator repo on Sept 29th, 2023**

This is a collection of CR templates that represent a validated Red Hat OpenStack Services on OpenShift deployment that has the following characteristics:

- 3 master/worker combo-node OpenShift cluster with Metal3 and a provisioning network
- 3-replica Galera database
- RabbitMQ
- OVN networking
- Network isolation over a single NIC
- 3 compute nodes (available as Metal3 BaremetalHosts)
- CephHCI installed on compute nodes and used by various OSP services
    - Cinder Volume using RBD for backend
    - Cinder Backup using RGW for backend
    - Glance using RBD for backend
    - Manila using CephFS for backend
    - Nova using RBD for ephemeral storage

## Considerations

1. These CRs are validated for the overall functionality of the OSP cloud deployed, but they nonetheless require customization for the particular environment in which they are utilized.  In this sense they are _templates_ meant to be consumed and tweaked to fit the specific constraints of the hardware available.  
2. The CRs are applied against an OpenShift cluster in _stages_.  That is, there is an ordering in which each grouping of CRs is fed to the cluster.  It is _not_ a case of simply taking all CRs from all stages and applying them all at once.
3. YAML comments are placed throughout the CRs to aid in the process of customizing the CRs.  Fields that _must_ (or most likely need to be) changed are commented with "# CHANGEME" either on the field itself or somewhere nearby.  Other comments are added to explain fields that can be changed and, sometimes, to explain additions that can be made.
4. Each stage directory contains an overview README describing what is being accomplished by that set of CRs.
5. Between stages 5 and 6, _it is assumed that the user installs CephHCI on the 3 OSP compute nodes._  OpenStack K8S CRDs do not provide a way to install CephHCI via any sort of combination of CRs.

## Stages

1. Install dependencies for the OpenStack K8S operators
2. Install the OpenStack K8S operators
3. Configuring networking on the OCP nodes
4. Configure and deploy the control plane
5. Configure and deploy the initial data plane to prepare for CephHCI installation
6. Update the control plane and finish deploying the data plane after CephHCI has been installed
