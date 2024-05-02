# Deployed Topology - Alpha

This document contains a list of integration test suites that would be
executed against the below specified topology of Red Hat OpenStack Services
on OpenShift. It also contains a collection of custom resources (CRs) for
deploying the test environment.

## Purpose

This topology is used for executing integration tests that evaluate the
`default` backends of the below mentioned services.

## Environment

### Nodes

| Role              | Machine Type | Count |
| ----------------- | ------------ | ----- |
| Compact OpenShift | vm           | 3     |
| OpenStack Compute | vm           | 2     |
| Networker         | vm           | 3     |
| Test nodes        | vm           | 2     |

### Networks

| Name         | Type     | Interface | CIDR            |
| ------------ | -------- | --------- | --------------- |
| Provisioning | untagged | nic1      | 172.22.0.0/24   |
| Machine      | untagged | nic2      | 192.168.32.0/20 |
| RH OSP       | trunk    | nic3      |                 |
| ironic       | untagged | nic4      | 172.20.1.0/24   |

#### Networks in RH OSP

| Name        | Type        | CIDR              |
| ----------- | ----------- | ----------------- |
| ctlplane    | untagged    | 192.168.122.0/24  |
| internalapi | VLAN tagged | 172.17.0.0/24     |
| storage     | VLAN tagged | 172.18.0.0/24     |
| tenant      | VLAN tagged | 172.19.0.0/24     |
| octavia     | VLAN tagged | 172.23.0.0/24     |
| ironic      | untagged    | 172.20.1.0/24     |

### Services, enabled features and configurations

| Service          | configuration    | Lock-in coverage?  |
| ---------------- | ---------------- | ------------------ |
| Cinder           | LVM/iSCSI/lioadm | Must have          |
| Cinder Backup    | Swift            | Must have          |
| Glance           | Swift            | Must have          |
| Swift            | (default)        | Must have          |
| Octavia          | (amphora)        | Must have          |
| Horizon          | N/A              | Must have          |
| Barbican         | (default)        | Must have          |
| Telemetry        |                  | Must have          |
| Ironic           |                  | Must have          |
| Neutron          | OVN - AZs        | Must have          |

#### Support services

The following table lists services which are not the main focus of the testing
(which may be covered by additional scenarios), but are required for the DT to
work properly and can be deployed with any/default configuration.

| Service          | Reason                     |
| ---------------- |--------------------------- |
| Nova             | needed by scenario testing |
| Keystone         | needed by all services     |
| Ceilometer       | needed by Telemetry        |
| Heat             | needed by Telemetry        |
| Prometheus       | needed by Telemetry        |


### Additional configuration

- Always-on, default services and features: TLSe
- Two additional fake baremetal nodes
- Availability zones for OVN (zone-1 & zone-2)
- Logical volume with the name cinder-volumes exists on a OpenShift node.
- iSCSI service is enabled on all OpenShift nodes.
- Multipath service is enabled on all OpenShift nodes.
- Cluster Observability Operator is installed on the platform.

#### iSCSI

It is assumed *iSCSI* services are enabled in all nodes participating in the
Red Hat OpenShift cluster. If not, a `MachineConfig` similar to the below one
is applied. The node would be *rebooted* after applying the configuration.

```YAML
---
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
    service: cinder
  name: 90-master-cinder-enable-iscsid
spec:
  config:
    ignition:
      version: 3.2.0
    systemd:
      units:
        - enabled: true
          name: iscsid.service
```

#### Multipath

It is assumed *multipath* services are enabled in all nodes particpating in the
Red Hat OpenShift cluster. If not, a `MachineConfig` like the one below must be
applied. The node would be *rebooted* after applying the configuration.

```YAML
---
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
    service: cinder
  name: 91-master-cinder-enable-multipathd
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
        - path: /etc/multipath.conf
          overwrite: false
          # Mode must be decimal, this is 0600
          mode: 384
          user:
            name: root
          group:
            name: root
          contents:
            # Source can be a http, https, tftp, s3, gs, or data as defined in rfc2397.
            # This is the rfc2397 text/plain string format
            source: data:,defaults%20%7B%0A%20%20user_friendly_names%20no%0A%20%20recheck_wwid%20yes%0A%20%20skip_kpartx%20yes%0A%20%20find_multipaths%20yes%0A%7D%0A%0Ablacklist%20%7B%0A%7D
    systemd:
      units:
      - enabled: true
        name: multipathd.service
```

The plain text contents of the multipath configuration file is

```conf
defaults {
  user_friendly_names    no
  recheck_wwid    yes
  skip_kpartx    yes
  find_multipaths  yes
}
blacklist {
}
```

#### Cinder backend - LVM

It is assumed that worker nodes or the master nodes have extra disks and there
exists a logical volume with the name *cinder_volumes*. If not, a
`MachineConfig` like the one below must be applied.

```YAML
---
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  name: 92-create-logical-volume
  labels:
    machineconfiguration.openshift.io/role: master
    service: cinder
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      disks:
        - device: "/dev/sdb"
          wipeTable: true
        - device: "/dev/sdc"
          wipeTable: true
      files:
        - path: /usr/local/bin/lv-cinder-volumes.sh
          overwrite: false
          mode: 493
          user:
            name: root
          group:
            name: root
          contents:
            source: data:text/plain;charset=utf-8;base64,{{ _replaced_ }}
    systemd:
      units:
        - name: lv-cinder-volumes.service
          enabled: true
          contents: |
            [Unit]
            Description=Create logical volume with name cinder-volumes.
            After=var.mount systemd-udev-settle.service

            [Service]
            Type=oneshot
            ExecStart=/usr/local/bin/lv-cinder-volumes.sh
            RemainAfterExit=yes

            [Install]
            WantedBy=multi-user.target
```

*{{ _replaced_ }}* should be replaced with the base64 encoding of the below script.

```bash
#! /usr/bin/bash
set -euo pipefail

if [[ $(vgdisplay cinder-volumes) ]]; then
    echo "cinder-volumes vg exists."
    exit 0
fi

disks=$(lsblk -o NAME,TYPE | awk '{ if ($2 == "disk" && $1 != "sda") print "/dev/"$1}')
disk_str=''

for disk in ${disks}; do
    pvcreate ${disk}
    disk_str="${disk_str} ${disk}"
done

vgcreate cinder-volumes ${disk_str}
```

##### Notes

The LVM backend for Cinder is a special case as the storage data is on the
OpenShift node and has no external storage systems. This has several
implications

- To prevent issues with exported volumes, cinder-operator automatically uses
  the host network. The backend is configured to use the host's VLAN IP
  address. This means that the cinder-volume service doesn't need any
  networkAttachments.
- There can only be one node with the label `openstack.org/cinder-lvm=`. Apply
  the label using the command
  `oc label node <nodename> openstack.org/cinder-lvm=`

### Octavia

Octavia is enabled with the appropriate network attachments configured to
deploy Octavia. It manages amphorae VMs through a self-service tenant network.
The Octavia Amphora controllers get access to it through a Neutron externally
routed flat provider network configured as a SNAT-less gateway for a neutron
router linked to the tenant networks. Host routes on the tenant network's
subnet and routes on the network attachment provide the required `next hop`
routing to establish the necessary bidirectional routing.

This arrangement requires a network attachment for connecting the OVN and
Amphora Controller pods (octavia-housekeeping, octavia-healthmanager,
octavia-worker). Because Neutron ML2/OVN implements provider networks by
bridging the relevant physical interface - in this case the network-attachment,
there is an additional requirement that this attachment function when
bridged. As the default macvlan attachments do not function when bridged, a
bridge network attachment is used.

Bridge attachments do not directly provide connectivity outside of the OCP
node. To implement this, the NodeNetworkConfigurationPolicy creates an VLAN
interface as is typical for the other networks, but does not configure an IP
pool as it is not needed. It is also not configured for metallb as it is solely
as part of a way to establish a L2 network link between nodes. The
NodeNetworkConfigurationPolicy also configures an octbr linux bridge which is
configured as the bridge for the network attachment mentioned above. It is also
configured to add the VLAN interface as a port, effectively linking the nodes
and the network attachments.

```YAML
spec:
  octavia:
    enabled: true
    template:
      octaviaAPI:
        networkAttachments:
          - internalapi
      octaviaHousekeeping:
        networkAttachments:
          - octavia
      octaviaWorker:
        networkAttachments:
          - octavia
      octaviaHealthManager:
        networkAttachments:
          - octavia

  ovn:
    template:
      ovncontroller:
        nicMappings:
          datacentre: ospbr
          octavia: octbr
```

### Ironic

Ironic service is enabled and appropriate network configuration is applied
to configure Baremetal-as-a-Service. It manages baremetal nodes and enables
baremetal nova instances.

A dedicated network is required for baremetal node management, such as
provisioning, cleaning and inspection. This network should be connected
to the OCP worker nodes, networker node and the test VMs (Virtual Baremetal).

The appropriate bridge mappings must be configured in Neutron (OVN).

```yaml
spec:
  ironic:
    enabled: true
    template:
      databaseInstance: openstack
      ironicAPI:
        override:
          service:
            internal:
              metadata:
                annotations:
                  metallb.universe.tf/address-pool: internalapi
                  metallb.universe.tf/allow-shared-ip: internalapi
                  metallb.universe.tf/loadBalancerIPs: 172.17.0.80
              spec:
                type: LoadBalancer
        replicas: 1
      ironicConductors:
      - customServiceConfig: |
          [neutron]
          cleaning_network = provisioning
          provisioning_network = provisioning
          rescuing_network = provisioning
        networkAttachments:
        - ironic
        provisionNetwork: ironic
        replicas: 1
        storageRequest: 10G
      ironicInspector:
        inspectionNetwork: ironic
        networkAttachments:
        - ironic
        replicas: 1
      ironicNeutronAgent:
        replicas: 1
      secret: osp-secret

  nova:
    template:
      cellTemplates:
        cell1:
          cellDatabaseAccount: nova-cell1
          cellDatabaseInstance: openstack-cell1
          cellMessageBusInstance: rabbitmq-cell1
          hasAPIAccess: true
          novaComputeTemplates:
            compute-ironic:
              computeDriver: ironic.IronicDriver

  ovn:
    template:
      ovnController:
        nicMappings:
          datacentre: ocpbr
          ironic: ironic
```

#### Ironic cloud configuration

##### Provisioning network

```bash
openstack network create provisioning \
  --share --provider-physical-network ironic \
  --provider-network-type flat \
  --availability-zone-hint zone-1
openstack subnet create provisioning-subnet \
  --network provisioning \
  --subnet-range 172.20.254.0/24 \
  --gateway 172.20.254.1 \
  --allocation-pool start=172.20.254.100,end=172.20.254.200
```

##### Nova flavor

```shell
sh-5.1$ openstack flavor create baremetal
  --ram 1024 --vcpus 1 --disk 15 \
  --property resources:VCPU=0 \
  --property resources:MEMORY_MB=0 \
  --property resources:DISK_GB=0 \
  --property resources:CUSTOM_BAREMETAL=1 \
  --property capabilities:boot_mode=uefi
```

##### Enroll nodes

```shell
$ cat nodes.yaml
---
nodes:
  - name: ironic-0
    driver: ipmi
    ports:
      - address: "52:54:00:71:7e:6c"
    driver_info:
      ipmi_address: 10.1.200.16
      ipmi_port: 6260
      ipmi_username: admin
      ipmi_password: password
  - name: ironic-1
    driver: ipmi
    ports:
      - address: "52:54:00:e3:64:98"
    driver_info:
      ipmi_address: 10.1.200.16
      ipmi_port: 6261
      ipmi_username: admin
      ipmi_password: password

sh-5.1$ openstack baremetal create nodes.yaml
sh-5.1$ openstack baremetal node list
+--------------------------------------+----------+---------------+-------------+--------------------+-------------+
| UUID                                 | Name     | Instance UUID | Power State | Provisioning State | Maintenance |
+--------------------------------------+----------+---------------+-------------+--------------------+-------------+
| 887726a6-3e69-4038-98d8-4d5047213d5a | ironic-0 | None          | None        | enroll             | False       |
| 4a510c68-703d-46b3-b31c-0f873e1f20f2 | ironic-1 | None          | None        | enroll             | False       |
+--------------------------------------+----------+---------------+-------------+--------------------+-------------+
sh-5.1$ openstack baremetal node manage ironic-0
sh-5.1$ openstack baremetal node manage ironic-1
sh-5.1$ openstack baremetal node list
+--------------------------------------+----------+---------------+-------------+--------------------+-------------+
| UUID                                 | Name     | Instance UUID | Power State | Provisioning State | Maintenance |
+--------------------------------------+----------+---------------+-------------+--------------------+-------------+
| 887726a6-3e69-4038-98d8-4d5047213d5a | ironic-0 | None          | None        | verifying          | False       |
| 4a510c68-703d-46b3-b31c-0f873e1f20f2 | ironic-1 | None          | None        | verifying          | False       |
+--------------------------------------+----------+---------------+-------------+--------------------+-------------+
```


## Testing

| Test framework   | When to run          | Special configuration |
| ---------------- | -------------------- | ----------------------|
| relevant volume tests | tempest stage |           |
| relevant image tests  | tempest stage |           |
| relevant object-storage tests  | tempest stage |           |
| relevant octavia tests | tempest stage |           |
| horizon integration   | own stage (post-tempest)|           |

## Workflow

1. [Install the OpenStack K8S operators and their dependencies](../../common/README.md)
2. [Configure and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the OpenStack networker deployment](networker.md)
4. [Configure and deploy the OpenStack data plane](data-plane.md)
