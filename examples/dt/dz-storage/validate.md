
# Validate Distributed Zone Storage

This section describes how to:

- Verify storage pods are running in the expected zones
- Use Cinder Types so that Multistore Glance can copy images to specific zones
- Confirm that storage workloads can be scheduled to the desired zone

## Pod Distribution

The generated `OpenStckControlPlane` CR has each pod inherit the `spread-pods` topology, defined in [section 6.4](https://docs.redhat.com/en/documentation/red_hat_openstack_services_on_openshift/18.0/html-single/deploying_a_rhoso_environment_with_distributed_zones/index#proc_create-a-Topology-CR-that-spreads-pods-across-all-zones_distributed-control-plane), except the `cinderVolumes`, `manilaShares` and Glance edge pods, which all use `topologyRef` to run in specific availability zones. Confirm that the pods for these services are running on their expected worker nodes based on the zone those where those worker nodes were tagged.

Observe the Cinder pod distribution.
```shell
$ oc get pods -l service=cinder -o wide
NAME                                    READY   STATUS      RESTARTS   AGE    IP               NODE       NOMINATED NODE   READINESS GATES
cinder-cbca0-api-0                      2/2     Running     0          45h    192.172.40.49    worker-4   <none>           <none>
cinder-cbca0-api-1                      2/2     Running     0          45h    192.172.16.50    worker-7   <none>           <none>
cinder-cbca0-api-2                      2/2     Running     0          45h    192.172.28.26    worker-1   <none>           <none>
cinder-cbca0-scheduler-0                2/2     Running     0          45h    192.172.44.23    worker-5   <none>           <none>
cinder-cbca0-volume-ontap-iscsi-az0-0   2/2     Running     0          100m   192.172.32.51    worker-2   <none>           <none>
cinder-cbca0-volume-ontap-iscsi-az1-0   2/2     Running     0          100m   192.172.44.110   worker-5   <none>           <none>
cinder-cbca0-volume-ontap-iscsi-az2-0   2/2     Running     0          100m   192.172.49.52    worker-8   <none>           <none>
cinder-db-purge-29170081-s4k78          0/1     Completed   0          23h    192.172.40.57    worker-4   <none>           <none>
$
```
Observe the Glance pod distribution.
```shell
$ oc get pods -l service=glance -o wide
NAME                                  READY   STATUS    RESTARTS   AGE    IP               NODE       NOMINATED NODE   READINESS GATES
glance-cbca0-az0-edge-api-0           2/2     Running   0          109m   192.172.32.50    worker-2   <none>           <none>
glance-cbca0-az0-edge-api-1           2/2     Running   0          109m   192.172.24.41    worker-0   <none>           <none>
glance-cbca0-az1-edge-api-0           2/2     Running   0          109m   192.172.44.109   worker-5   <none>           <none>
glance-cbca0-az1-edge-api-1           2/2     Running   0          110m   192.172.40.59    worker-4   <none>           <none>
glance-cbca0-az2-edge-api-0           2/2     Running   0          109m   192.172.49.50    worker-8   <none>           <none>
glance-cbca0-az2-edge-api-1           2/2     Running   0          109m   192.172.36.41    worker-6   <none>           <none>
glance-cbca0-default-external-api-0   2/2     Running   0          110m   192.172.44.106   worker-5   <none>           <none>
glance-cbca0-default-external-api-1   2/2     Running   0          110m   192.172.28.35    worker-1   <none>           <none>
glance-cbca0-default-external-api-2   2/2     Running   0          110m   192.172.49.48    worker-8   <none>           <none>
glance-cbca0-default-internal-api-0   2/2     Running   0          110m   192.172.49.44    worker-8   <none>           <none>
glance-cbca0-default-internal-api-1   2/2     Running   0          110m   192.172.24.39    worker-0   <none>           <none>
glance-cbca0-default-internal-api-2   2/2     Running   0          110m   192.172.44.107   worker-5   <none>           <none>
$
```
Observe the Manila pod distribution.
```shell
$ oc get pods -o wide -l service=manila
NAME                             READY   STATUS      RESTARTS   AGE     IP               NODE       NOMINATED NODE   READINESS GATES
manila-api-0                     2/2     Running     0          6d16h   192.172.45.11    worker-5   <none>           <none>
manila-api-1                     2/2     Running     0          51s     192.172.50.187   worker-8   <none>           <none>
manila-api-2                     2/2     Running     0          51s     192.172.32.54    worker-2   <none>           <none>
manila-db-purge-29185921-6cptm   0/1     Completed   0          2d15h   192.172.49.178   worker-8   <none>           <none>
manila-db-purge-29187361-pq7hl   0/1     Completed   0          39h     192.172.50.23    worker-8   <none>           <none>
manila-db-purge-29188801-rmmpz   0/1     Completed   0          15h     192.172.45.167   worker-5   <none>           <none>
manila-scheduler-0               2/2     Running     0          7d18h   192.172.51.102   worker-8   <none>           <none>
manila-scheduler-1               2/2     Running     0          51s     192.172.45.185   worker-5   <none>           <none>
manila-scheduler-2               2/2     Running     0          29s     192.172.24.54    worker-0   <none>           <none>
manila-share-az0-0               2/2     Running     0          5d2h    192.172.28.44    worker-1   <none>           <none>
manila-share-az1-0               2/2     Running     0          5d2h    192.172.45.37    worker-5   <none>           <none>
manila-share-az2-0               2/2     Running     0          5d2h    192.172.48.173   worker-8   <none>           <none>
$
```

## Cinder Volume Types

When Multistore Glance is configured to use Cinder as its backend each Glance store will specify a unique `cinder_volume_type`.

We do not want these volume types to be exposed to cloud users so the types will be created with the `--private` option. We do want Glance, which runs under the service project, to be able to access these types so we will set the `--project` for each type to the service project ID as identified with the following command.

```
sh-5.1$ openstack project list
+----------------------------------+---------+
| ID                               | Name    |
+----------------------------------+---------+
| 439f0ee839144b4c8640b9153a596a30 | admin   |
| 7a8946c6ec7c4d0488c592f0306eaa35 | service |
+----------------------------------+---------+
sh-5.1$
```

A type will be created for each of the three cinder-volume services in each AZ. Using [RESKEY:availability\_zones](https://opendev.org/openstack/cinder/src/commit/c948b22eace9f6aa299a0af3ac374864ff8ff163/releasenotes/notes/support-az-in-volumetype-8yt6fg67de3976ty.yaml) will result in the AZ being passed to Cinder even though Glance only passes the type when it requests a volume.

Store the service user project ID for Glance in a shell variable.

```
SERVICE_PROJECT_ID=$(openstack project show service -c id -f value)
```

Create each type with its project ID and availability zone.

```
openstack volume type create --private --project "$SERVICE_PROJECT_ID" --property "RESKEY:availability_zones=az0" glance-iscsi-az0
openstack volume type create --private --project "$SERVICE_PROJECT_ID" --property "RESKEY:availability_zones=az1" glance-iscsi-az1
openstack volume type create --private --project "$SERVICE_PROJECT_ID" --property "RESKEY:availability_zones=az2" glance-iscsi-az2
```

### Cinder Volume Type Verification

Confirm you can create volumes by AZ.

```
openstack volume create --size 1 --availability-zone az0 vol_az0
openstack volume create --size 1 --availability-zone az1 vol_az1
openstack volume create --size 1 --availability-zone az2 vol_az2
```

As an administrator, confirm you can create a volume in the desired AZ by passing only the type.

```
openstack volume create --size 1 --type glance-iscsi-az0 vol_az0_by_type
openstack volume create --size 1 --type glance-iscsi-az1 vol_az1_by_type
openstack volume create --size 1 --type glance-iscsi-az2 vol_az2_by_type
```

Make sure the volumes are available and delete them afterwards.

## Multistore Glance backed by Cinder

Observe available stores:

```
$ glance stores-info
+----------+----------------------------------------------------------------------------------+
| Property | Value                                                                            |
+----------+----------------------------------------------------------------------------------+
| stores   | [{"id": "az0", "description": "AZ0 NetApp iscsi cinder backend", "default":      |
|          | "true"}, {"id": "az1", "description": "AZ1 NetApp iscsi cinder backend"}, {"id": |
|          | "az2", "description": "AZ2 NetApp iscsi cinder backend"}]                        |
+----------+----------------------------------------------------------------------------------+
$
```

Create an image without passing any store related parameters and see what happens.

```
sh-5.1$ openstack image create --disk-format qcow2 --container-format bare --public --file ./cirros-0.5.2-x86_64-disk.img cirros-default
+------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| Field            | Value                                                                                                                                              |
+------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| container_format | bare                                                                                                                                               |
| created_at       | 2025-06-18T22:55:21Z                                                                                                                               |
| disk_format      | qcow2                                                                                                                                              |
| file             | /v2/images/10fcfc90-e178-4776-ac76-853a7082844b/file                                                                                               |
| id               | 10fcfc90-e178-4776-ac76-853a7082844b                                                                                                               |
| min_disk         | 0                                                                                                                                                  |
| min_ram          | 0                                                                                                                                                  |
| name             | cirros-default                                                                                                                                     |
| owner            | 439f0ee839144b4c8640b9153a596a30                                                                                                                   |
| properties       | os_hidden='False', owner_specified.openstack.md5='', owner_specified.openstack.object='images/cirros-default', owner_specified.openstack.sha256='' |
| protected        | False                                                                                                                                              |
| schema           | /v2/schemas/image                                                                                                                                  |
| status           | queued                                                                                                                                             |
| tags             |                                                                                                                                                    |
| updated_at       | 2025-06-18T22:55:21Z                                                                                                                               |
| visibility       | public                                                                                                                                             |
+------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
sh-5.1$
```

The image is created in az0 because that's the default.

```
sh-5.1$ openstack image show 10fcfc90-e178-4776-ac76-853a7082844b | grep stores
| properties       | os_hash_algo='sha512', os_hash_value='6b813aa46bb90b4da216a4d19376593fa3f4fc7e617f03a92b7fe11e9a3981cbe8f0959dbebe36225e5f53dc4492341a4863cac4ed1ee0909f3fc78ef9c3e869', os_hidden='False', owner_specified.openstack.md5='', owner_specified.openstack.object='images/cirros-default', owner_specified.openstack.sha256='', stores='az0' |
sh-5.1$
```

Create an image and pass a parameter so it goes directly into store az0.

```
$ glance image-create --disk-format raw --container-format bare --name cirros-test --file cirros-0.5.2-x86_64-disk.img --store az0
+------------------+----------------------------------------------------------------------------------+
| Property         | Value                                                                            |
+------------------+----------------------------------------------------------------------------------+
| checksum         | b874c39491a2377b8490f5f1e89761a4                                                 |
| container_format | bare                                                                             |
| created_at       | 2025-06-18T22:47:10Z                                                             |
| disk_format      | raw                                                                              |
| id               | 5073f3f0-e4ac-4cca-9883-fecade29a1f3                                             |
| min_disk         | 0                                                                                |
| min_ram          | 0                                                                                |
| name             | cirros-test                                                                      |
| os_hash_algo     | sha512                                                                           |
| os_hash_value    | 6b813aa46bb90b4da216a4d19376593fa3f4fc7e617f03a92b7fe11e9a3981cbe8f0959dbebe3622 |
|                  | 5e5f53dc4492341a4863cac4ed1ee0909f3fc78ef9c3e869                                 |
| os_hidden        | False                                                                            |
| owner            | 439f0ee839144b4c8640b9153a596a30                                                 |
| protected        | False                                                                            |
| size             | 16300544                                                                         |
| status           | active                                                                           |
| stores           | az0                                                                              |
| tags             | []                                                                               |
| updated_at       | 2025-06-18T22:48:00Z                                                             |
| virtual_size     | 16300544                                                                         |
| visibility       | shared                                                                           |
+------------------+----------------------------------------------------------------------------------+
$
```

Import it into az1

```
$ glance image-import 5073f3f0-e4ac-4cca-9883-fecade29a1f3 --stores az1 --import-method copy-image
+-----------------------+----------------------------------------------------------------------------------+
| Property              | Value                                                                            |
+-----------------------+----------------------------------------------------------------------------------+
| checksum              | b874c39491a2377b8490f5f1e89761a4                                                 |
| container_format      | bare                                                                             |
| created_at            | 2025-06-18T22:47:10Z                                                             |
| disk_format           | raw                                                                              |
| id                    | 5073f3f0-e4ac-4cca-9883-fecade29a1f3                                             |
| min_disk              | 0                                                                                |
| min_ram               | 0                                                                                |
| name                  | cirros-test                                                                      |
| os_glance_import_task | 7a141f7f-409a-4ea9-b66f-0658a83e907b                                             |
| os_hash_algo          | sha512                                                                           |
| os_hash_value         | 6b813aa46bb90b4da216a4d19376593fa3f4fc7e617f03a92b7fe11e9a3981cbe8f0959dbebe3622 |
|                       | 5e5f53dc4492341a4863cac4ed1ee0909f3fc78ef9c3e869                                 |
| os_hidden             | False                                                                            |
| owner                 | 439f0ee839144b4c8640b9153a596a30                                                 |
| protected             | False                                                                            |
| size                  | 16300544                                                                         |
| status                | active                                                                           |
| stores                | az0                                                                              |
| tags                  | []                                                                               |
| updated_at            | 2025-06-18T22:48:00Z                                                             |
| virtual_size          | 16300544                                                                         |
| visibility            | shared                                                                           |
+-----------------------+----------------------------------------------------------------------------------+
$
```

Observe that the image is in the stores for az0 and az1.

```
sh-5.1$ openstack image show 5073f3f0-e4ac-4cca-9883-fecade29a1f3 | grep stores
| properties       | os_glance_failed_import='', os_glance_importing_to_stores='', os_hash_algo='sha512', os_hash_value='6b813aa46bb90b4da216a4d19376593fa3f4fc7e617f03a92b7fe11e9a3981cbe8f0959dbebe36225e5f53dc4492341a4863cac4ed1ee0909f3fc78ef9c3e869', os_hidden='False', stores='az0,az1' |
sh-5.1$
```

Observe the Cinder volumes in az0 and az1 which store the image ID from the previous step.

```
sh-5.1$ openstack volume list --all | grep 5073f3f0-e4ac-4cca-9883-fecade29a1f3
| 713f25b2-accc-4f4f-b5ba-8c71e2fac3aa | image-5073f3f0-e4ac-4cca-9883-fecade29a1f3 | available |    1 |                                 |
| b1917ec2-2d8e-42cc-b58c-55db48f1e054 | image-5073f3f0-e4ac-4cca-9883-fecade29a1f3 | available |    1 |                                 |
sh-5.1$ 
```

Confirm the availability zone, type and host of each volume backing the image.

```
sh-5.1$ openstack volume show b1917ec2-2d8e-42cc-b58c-55db48f1e054 -c type -c availability_zone -c os-vol-host-attr:host
+-----------------------+---------------------------------------------------------------+
| Field                 | Value                                                         |
+-----------------------+---------------------------------------------------------------+
| availability_zone     | az0                                                           |
| os-vol-host-attr:host | cinder-cbca0-volume-ontap-iscsi-az0-0@ontap#cinder_iscsi_pool |
| type                  | glance-iscsi-az0                                              |
+-----------------------+---------------------------------------------------------------+
sh-5.1$ openstack volume show 713f25b2-accc-4f4f-b5ba-8c71e2fac3aa -c type -c availability_zone -c os-vol-host-attr:host
+-----------------------+---------------------------------------------------------------+
| Field                 | Value                                                         |
+-----------------------+---------------------------------------------------------------+
| availability_zone     | az1                                                           |
| os-vol-host-attr:host | cinder-cbca0-volume-ontap-iscsi-az1-0@ontap#cinder_iscsi_pool |
| type                  | glance-iscsi-az1                                              |
+-----------------------+---------------------------------------------------------------+
sh-5.1$ 
```

## Validate Nova’s use of Glance and Cinder 3rd party storage per Zone

We assume that there are compute nodes in all three zones and that they have been put into their own aggregates using a script like the following.

```shell
function make_aggregate() {
    OS="oc rsh openstackclient openstack"
    AZ=az$1
    RACK=r$1
    $OS aggregate create $AZ
    $OS aggregate set --zone $AZ $AZ
    for I in $(seq 0 2); do
        $OS aggregate add host $AZ ${RACK}-compute-${I}.ctlplane.example.com
    done
    $OS compute service list -c Host -c Zone
}

make_aggregate 0
make_aggregate 1
make_aggregate 2
```

Create an ephemeral VM in AZ0 using the image created earlier

```
openstack server create --flavor c1 --image 3ae0d8d8-18f5-452e-a58e-63fb7aba308a --nic net-id=private --availability-zone az0 vm-az0
```

Observe the VM

```
sh-5.1$ openstack server list
+--------------------------------------+--------+--------+----------------------+------------------+--------+
| ID                                   | Name   | Status | Networks             | Image            | Flavor |
+--------------------------------------+--------+--------+----------------------+------------------+--------+
| c1f8b608-41d4-422a-ab89-82762353a784 | vm-az0 | ACTIVE | private=192.168.0.21 | cirros-priv-type | c1     |
+--------------------------------------+--------+--------+----------------------+------------------+--------+
```

Create a volume from an image in AZ1 using the image which was imported into AZ1 earlier

```
openstack volume create --size 8 vm_root_az1 --image 3ae0d8d8-18f5-452e-a58e-63fb7aba308a --availability-zone az1
```

Observe the volume

```
sh-5.1$ openstack volume list
+--------------------------------------+-------------+-----------+------+-------------+
| ID                                   | Name        | Status    | Size | Attached to |
+--------------------------------------+-------------+-----------+------+-------------+
| 119958b1-0fca-4412-81d1-1d9b856ce85a | vm_root_az1 | available |    8 |             |
+--------------------------------------+-------------+-----------+------+-------------+
```

Create a VM in AZ1 whose root volume is the cinder volume from the previous step

```
openstack server create --flavor c1 --volume 119958b1-0fca-4412-81d1-1d9b856ce85a --nic net-id=private --availability-zone az1 vm-az1
```

Observe the VMs

```
sh-5.1$ openstack server list
+--------------------------------------+--------+--------+-----------------------+--------------------------+--------+
| ID                                   | Name   | Status | Networks              | Image                    | Flavor |
+--------------------------------------+--------+--------+-----------------------+--------------------------+--------+
| 54e1a625-08d1-4df5-838c-c8ea676d2e06 | vm-az1 | ACTIVE | private=192.168.0.138 | N/A (booted from volume) | c1     |
| c1f8b608-41d4-422a-ab89-82762353a784 | vm-az0 | ACTIVE | private=192.168.0.21  | cirros-priv-type         | c1     |
+--------------------------------------+--------+--------+-----------------------+--------------------------+--------+
sh-5.1$
```

## Manila Verification

### Driver Handles Share Servers (DHSS)

When DHSS is enabled, the driver manages the creation of share servers (Storage Virtual Machines or SVMs in ONTAP) for each tenant network, rather than having Manila handle it.

The generated `OpenStackControlPlane` CR has `driver_handles_share_servers = False` so DHSS is disabled. Set it true to enable it if desired. Below are verification steps depending on if this option is enabled or disabled.

### Testing with DHSS Disabled

Create a share type (as the OpenStack admin).

```
openstack share type create nfs-multiaz False --extra-specs share_backend_name=nfs_az
```

Observe the share type.

```
$ openstack share type list
+--------------------------------------+--------------+------------+------------+--------------------------------------+-----------------------------+-------------+
| ID                                   | Name         | Visibility | Is Default | Required Extra Specs                 | Optional Extra Specs        | Description |
+--------------------------------------+--------------+------------+------------+--------------------------------------+-----------------------------+-------------+
| a63ecc00-33f5-4bd8-9d93-a1fb31f2fe79 | nfs-multiaz  | public     | False      | driver_handles_share_servers : False | share_backend_name : nfs_az | None        |
+--------------------------------------+--------------+------------+------------+--------------------------------------+-----------------------------+-------------+
$
```

The remaining commands can be run as a normal project user.

Create a share per AZ.

```
openstack share create nfs 1 --name nfsaz0 --availability-zone az0
openstack share create nfs 1 --name nfsaz1 --availability-zone az1
openstack share create nfs 1 --name nfsaz2 --availability-zone az2
```

Note that the `openstack share create` command did not need to pass `--share-type nfs-multiaz` because of the following from the configuration section.

```
      manilaAPI:
        customServiceConfig: |
          [DEFAULT]
          storage_availability_zone = az0,az1,az2
          default_share_type = nfs-multiaz
```

If the `default_share_type` is not set, then `--share-type nfs-multiaz` should be passed with the `openstack share create` command.

Observe the shares and their AZs.

```
$ openstack share list
+--------------------------------------+--------+------+-------------+-----------+-----------+-----------------+-------------------------------+-------------------+
| ID                                   | Name   | Size | Share Proto | Status    | Is Public | Share Type Name | Host                          | Availability Zone |
+--------------------------------------+--------+------+-------------+-----------+-----------+-----------------+-------------------------------+-------------------+
| ef1fa319-4661-4d18-880b-a24b5e708234 | nfsaz0 |    1 | NFS         | available | False     | nfs-multiaz     | hostgroup@nfs_az0#n2_nvme_15T | az0               |
| f91e1e59-e101-4e1f-8b92-fb49edd706cf | nfsaz1 |    1 | NFS         | available | False     | nfs-multiaz     | hostgroup@nfs_az1#n2_nvme_15T | az1               |
| 09c9f709-1cf6-4279-ba39-8c80669b118a | nfsaz2 |    1 | NFS         | available | False     | nfs-multiaz     | hostgroup@nfs_az2#n2_nvme_15T | az2               |
+--------------------------------------+--------+------+-------------+-----------+-----------+-----------------+-------------------------------+-------------------+
$
```

Get the NFS path(s) of a share

```
openstack share show nfsaz0
```

For example:

```
$ openstack share show nfsaz0 | grep path
|                                       | path = 10.0.0.42:/share_9afcc8c4_2a09_4d05_8cdc_f28eb58a3dff        |
```

Grant access to the appropriate IP range based on the Nova instance to access the share:

```
openstack share access create nfsaz0 ip 10.0.0.0/24 --access-level rw
```

Mount the share from the nova instance at the desired path.

```
mount -t nfs 10.0.0.42:/share_<UUID> /mnt/share
```

### Testing with DHSS Enabled

If DHSS is enabled, then `--share-network` becomes mandatory when running `openstack share create`. The share network is used to set up the share server networking and allocate the port.

As the Open Stack administrator, create the share.

```
openstack share type create nfs-multiaz true --extra-specs share_backend_name='nfs_az'
```

As the project administrator, create a network and subnet for manila to use.

```
openstack network create --project rhoso --provider-network-type vlan manila_net
openstack subnet create --network manila_net --subnet-range <subnet> --dns-nameserver <dns> manila-subnetaz1
```

As a project user, create the share network using the values from the previous step and define a share for each availability zones.

```
openstack share network create --name share_net --neutron-net-id <net_id> --neutron-subnet-id <sub_net_id>
openstack share create nfs 1 --name nfsaz0 --share-network share_net --availability-zone az0
openstack share create nfs 1 --name nfsaz1 --share-network share_net --availability-zone az1
openstack share create nfs 1 --name nfsaz2 --share-network share_net --availability-zone az2
```

In this example, the created share network does not have an availability zone set, meaning that it will result in a default share network subnet being created, which spans all availability zones.

It is also possible to create neutron networks and subnets for each availability zone and restrain shares on the given zones to be created on the corresponding neutron networks and subnets. To achieve such isolation level, create multiple share network subnets within the Manila share network, each one with their respective neutron network, subnet and availability zone.

Note that the `openstack share create` command did not need to pass `--share-type nfs-multiaz` because of the following in the OpenStackControlPlane.

```
      manilaAPI:
        customServiceConfig: |
          [DEFAULT]
          storage_availability_zone = az0,az1,az2
          default_share_type = nfs-multiaz
```

If the `default_share_type` is not set, then `--share-type nfs-multiaz` should be passed with the `openstack share create` command.

Get the NFS path(s) of a share

```
openstack share show nfsaz0
```

For example:

```
$ openstack share show nfsaz0 | grep 10.0.0.42
|                                       | path = 10.0.0.42:/share_9afcc8c4_2a09_4d05_8cdc_f28eb58a3dff        |
```

Grant access to the appropriate IP range based on the Nova instance to access the share:

```
openstack share access create nfsaz0 ip 10.0.0.0/24 --access-level rw
```

Mount the share from the virtual machine at the desired path.

```
mount -t nfs 10.0.0.42:/share_<UUID> /mnt/share
```
