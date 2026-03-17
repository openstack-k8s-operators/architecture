# Update the control plane and finish deploying the data plane after Ceph has been installed

## Assumptions

- The [pre-ceph data plane](dataplane-pre-ceph.md) has been deployed
- Ceph has been installed on the compute nodes

## Initialize

Switch to the "openstack" namespace

```shell
oc project openstack
```

Change to the nova05epsilon directory

```shell
cd architecture/examples/dt/nova/nova05epsilon
```

Edit the [values.yaml](values.yaml) and [service-values.yaml](service-values.yaml)
files to suit your environment. In particular, update the Ceph configuration
placeholders in `values.yaml`:

- **`data.ceph_conf`** (DCN convention): A dict mapping Ceph filenames to
  base64-encoded content. For a single-site deployment, use plain filenames.
  For multi-AZ DCN, use az-prefixed filenames (e.g. `az0.conf`, `az1.conf`).
  - `ceph.client.openstack.keyring`: `base64 -w0 /etc/ceph/ceph.client.openstack.keyring`
  - `ceph.conf`: `base64 -w0 /etc/ceph/ceph.conf`
- **`CHANGEME_NOVA_CEPH_CONF`**: Nova compute Ceph configuration in INI
  format. This configures libvirt RBD for ephemeral disks and Glance
  copy-on-write. A typical value looks like:

```ini
[libvirt]
images_type=rbd
images_rbd_pool=vms
images_rbd_ceph_conf=/etc/ceph/ceph.conf
images_rbd_glance_store_name=default_backend
images_rbd_glance_copy_poll_interval=15
images_rbd_glance_copy_timeout=600
rbd_user=openstack
rbd_secret_uuid=<ceph-fsid>
```

Replace `<ceph-fsid>` with the Ceph cluster FSID (from `ceph fsid`).

```shell
vi values.yaml
vi service-values.yaml
```

## Update the control plane and deploy the post-ceph dataplane

Generate the post-ceph CRs (this includes both the updated control plane
and the post-ceph nodeset):

```shell
kustomize build > dataplane-nodeset.yaml
```

Apply the CRs:

```shell
oc apply -f dataplane-nodeset.yaml
```

Wait for control plane to be available:

```shell
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```

Wait for the nodeset setup to complete:

```shell
oc wait osdpns gpu-computes-edpm --for condition=SetupReady --timeout=600s
```

Generate and apply the post-ceph deployment:

```shell
kustomize build deployment > dataplane-deployment.yaml
oc apply -f dataplane-deployment.yaml
```

Wait for deployment to finish:

```shell
oc wait osdpd edpm-deployment-post-ceph --for condition=Ready --timeout=40m
```

## Verify GPU passthrough

After deployment, verify that GPU PCI devices are reported in Placement:

```shell
oc rsh nova-api-0 nova-manage placement audit
```

Create a flavor with GPU passthrough:

```shell
openstack --os-compute-api=2.86 flavor create --ram 8192 --vcpus 4 --disk 40 gpu-passthrough
openstack --os-compute-api=2.86 flavor set --property "pci_passthrough:alias"="nvidia_a2:1" gpu-passthrough
```
