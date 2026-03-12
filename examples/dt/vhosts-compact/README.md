# Vhosts-Compact: RabbitMQ Vhost-Based Service Isolation

This is a collection of CR templates that represent a validated Red Hat OpenStack Services on OpenShift deployment that has the following characteristics:

- 3 master+worker combo OpenShift nodes
- 3-replica Galera database
- 3-replica RabbitMQ with per-service vhost and user isolation for RPC
- Dedicated `rabbitmq-notifications` cluster for all notifications
- OVN networking
- Network isolation over a single NIC
- 3 compute nodes
- CephHCI deployed on compute nodes
- Ceph RBD used as Glance and Cinder backend
- CephFS via NFS used as Manila backend
- Swift enabled

## Messaging Architecture

This DT tests RabbitMQ vhost-based service isolation using the `spec.messagingBus` and `spec.notificationsBus` top-level CRD fields:

- **RPC:** A single `rabbitmq` cluster is shared by all services. Each service gets a dedicated vhost and user named after itself (e.g., `vhost: nova`, `user: nova`).
- **Notifications:** A single `rabbitmq-notifications` cluster handles all service notifications using the default user (configured via top-level `spec.notificationsBus`).
- **Nova cells:** cell0 and cell1 both use the shared `rabbitmq` cluster with vhosts `nova-cell0`/`nova-cell1` and users `nova-cell0`/`nova-cell1`.

### Services Enabled

barbican, cinder, designate, glance, heat, ironic, keystone, manila, neutron, nova, octavia, telemetry (ceilometer, cloudkitty), watcher, swift

## Assumptions

- A storage class called `local-storage` should already exist.

## Prerequisites

[Install the OpenStack K8S operators and their dependencies](https://github.com/openstack-k8s-operators/architecture/blob/main/examples/common)

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the vhosts-compact directory
```
cd architecture/examples/dt/vhosts-compact
```
Edit the [control-plane/nncp/values.yaml](control-plane/nncp/values.yaml) and
[control-plane/service-values.yaml](control-plane/service-values.yaml) files to suit
your environment.
```
vi control-plane/nncp/values.yaml
vi control-plane/service-values.yaml
```

## Apply node network configuration

Generate the node network configuration
```
kustomize build control-plane/nncp > nncp.yaml
```
Apply the NNCP CRs
```
oc apply -f nncp.yaml
```
Wait for NNCPs to be available
```
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

## Apply networking and control-plane configuration

Generate the control-plane and networking CRs.
```
kustomize build control-plane > control-plane.yaml
```
Apply the CRs
```
oc apply -f control-plane.yaml
```

Wait for control plane to be available
```
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```

## Apply pre-Ceph dataplane configuration

Generate the dataplane nodeset CR.
```
kustomize build edpm-pre-ceph/nodeset > nodeset-pre-ceph.yaml
```
Apply the CR
```
oc apply -f nodeset-pre-ceph.yaml
```

Wait for the nodeset to reach the SetupReady condition
```
oc -n openstack wait openstackdataplanenodeset openstack-edpm --for condition=SetupReady --timeout=600s
```

Generate the dataplane deployment CR.
```
kustomize build edpm-pre-ceph/deployment > deployment-pre-ceph.yaml
```
Apply the CR
```
oc apply -f deployment-pre-ceph.yaml
```

Wait for the dataplanedeployment to reach the "Ready" condition
```
oc -n openstack wait openstackdataplanedeployment edpm-deployment-pre-ceph --for condition=Ready --timeout=40m
```

## Deploy Ceph

Install Ceph on the compute nodes. After Ceph is deployed, retrieve the
configuration and update `values.yaml`:
```
CONF=$(cat /etc/ceph/ceph.conf | base64 -w 0)
KEY=$(cat /etc/ceph/ceph.client.openstack.keyring | base64 -w 0)
```
Update `values.yaml` replacing `CHANGEME_CEPH_CONF` and `CHANGEME_CEPH_KEYRING`
with the base64-encoded values. Also update `rbd_secret_uuid` in
`service-values.yaml` with the Ceph FSID.

## Apply post-Ceph configuration

This step updates the control plane with Ceph-backed storage (Cinder RBD,
Glance RBD, Manila CephFS) and redeploys the dataplane with the `ceph-client`
service.

Generate the post-Ceph nodeset CR.
```
kustomize build > nodeset-post-ceph.yaml
```
Apply the CR
```
oc apply -f nodeset-post-ceph.yaml
```

Wait for the nodeset to reach the SetupReady condition
```
oc -n openstack wait openstackdataplanenodeset openstack-edpm --for condition=SetupReady --timeout=600s
```

Generate the post-Ceph deployment CR.
```
kustomize build deployment > deployment-post-ceph.yaml
```
Apply the CR
```
oc apply -f deployment-post-ceph.yaml
```

Wait for the dataplanedeployment to reach the "Ready" condition
```
oc -n openstack wait openstackdataplanedeployment edpm-deployment-post-ceph --for condition=Ready --timeout=40m
```
