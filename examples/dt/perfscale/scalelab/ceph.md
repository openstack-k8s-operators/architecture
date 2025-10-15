# Ceph Backend Configuration

This guide describes how to enable Ceph backend for OpenStack services. Ceph support is **optional** and provides storage for Cinder, Glance, and Nova.

## Overview

When enabled, Ceph provides:
- **Cinder Volume**: RBD backend for block storage
- **Glance**: RBD backend for image storage
- **Nova Compute**: RBD backend for ephemeral storage

## Prerequisites

1. A Ceph cluster must be deployed and accessible via storage network.
2. The following Ceph configuration must be available:
   - Ceph configuration file (`ceph.conf`)
   - Ceph client keyring (`ceph.client.openstack.keyring`)
   - Ceph FSID (from `ceph.conf`)
3. Ceph pools must be created:
   - `volumes` - for Cinder volumes
   - `images` - for Glance images
   - `vms` - for Nova ephemeral storage

## Configuration Steps

### 1. Prepare Ceph Configuration Values

Retrieve and encode the Ceph configuration from your Ceph cluster:

```bash
# Get base64-encoded Ceph configuration
CEPH_CONF=$(cat /etc/ceph/ceph.conf | base64 -w 0)
CEPH_KEYRING=$(cat /etc/ceph/ceph.client.openstack.keyring | base64 -w 0)

# Extract FSID from secret/ alternatively can be fetched from ceph.conf
FSID=$(oc get secret ceph-conf-files -o json | jq -r '.data."ceph.conf"' | base64 -d | grep fsid | sed -e 's/fsid = //')
```

### 2. Enable Ceph in Control Plane

Edit `examples/dt/perfscale/scalelab/kustomization.yaml` and uncomment:

```yaml
components:
  - ../../../../dt/perfscale/scalelab/
  # To enable Ceph, uncomment the following line:
  - ../../../../dt/perfscale/scalelab/ceph/          # ← Uncomment this

resources:
  - networking/nncp/values.yaml
  - service-values.yaml
  # To enable Ceph, uncomment the following line:
  - service-values-ceph.yaml                          # ← Uncomment this
```

Edit `service-values-ceph.yaml` and replace the following values:

```yaml
data:
  # Ceph conf and keyring
  ceph:
    conf: CHANGEME_CEPH_CONF          # Replace with $CEPH_CONF
    keyring: CHANGEME_CEPH_KEYRING    # Replace with $CEPH_KEYRING

  # Cinder RBD backend
  cinderVolumes:
    ceph:
      customServiceConfig: |
        [DEFAULT]
        enabled_backends = ceph
        [ceph]
        volume_backend_name = ceph
        volume_driver = cinder.volume.drivers.rbd.RBDDriver
        rbd_ceph_conf = /etc/ceph/ceph.conf
        rbd_user = openstack
        rbd_pool = volumes
        rbd_flatten_volume_from_snapshot = False
        rbd_secret_uuid = CHANGEME    # Replace with $CEPH_FSID
```

### 3. Enable Ceph in Data Plane

Edit `examples/dt/perfscale/scalelab/edpm/nodeset/kustomization.yaml` and uncomment:

```yaml
components:
  - ../../../../../../dt/perfscale/scalelab/edpm/nodeset
  # To enable Ceph, uncomment the following line:
  - ../../../../../../dt/perfscale/scalelab/ceph/edpm-nodeset  # ← Uncomment this

resources:
  - values.yaml
  # To enable Ceph, uncomment the following line:
  - values-ceph.yaml                                           # ← Uncomment this
```

Edit `edpm/nodeset/values-ceph.yaml` and configure:

```yaml
data:
  nova:
    ceph:
      conf: |                         # Replace CHANGEME_NOVA_CEPH_CONF with:
        [libvirt]
        images_type=rbd
        images_rbd_pool=vms
        images_rbd_ceph_conf=/etc/ceph/ceph.conf
        images_rbd_glance_store_name=default_backend
        images_rbd_glance_copy_poll_interval=15
        images_rbd_glance_copy_timeout=600
        rbd_user=openstack
        rbd_secret_uuid=<FSID>        # Replace with $CEPH_FSID
```

## Deployment

After enabling and configuring Ceph, deploy as normal following the main [README.md](README.md):

1. Deploy control plane: [control-plane.md](control-plane.md)
2. Deploy data plane: [dataplane.md](dataplane.md)

The Ceph configuration will be automatically integrated into the generated CRs.

## What Gets Configured

### Control Plane

- **Ceph Secret**: `ceph-conf-files` secret with Ceph configuration and keyring
- **Cinder**: 
  - Ceph volume backend configured
- **Glance**: RBD backend for image storage
- **Extra Mounts**: Ceph configuration files mounted in CinderVolume and GlanceAPI pods

### Data Plane

- **Ceph Client**: Installed and configured on compute nodes
- **Nova**: 
  - Custom service `nova-custom-ceph` replaces standard `nova` service
  - RBD backend for ephemeral storage
  - Ceph configuration mounted in Nova compute containers

## Disabling Ceph

To deploy without Ceph (default Swift backend for Glance):

1. Ensure Ceph lines remain commented in both kustomization.yaml files
2. Do not include `service-values-ceph.yaml` or `values-ceph.yaml` resources
3. Deploy normally - Swift will be used as Glance backend

## Architecture

The Ceph integration uses a modular kustomize component structure:

```
dt/perfscale/scalelab/ceph/                    # Control plane Ceph component
  ├── kustomization.yaml                        # Ceph replacements for control plane
  ├── ceph-secret.yaml                          # Ceph secret template
  └── edpm-nodeset/                             # Data plane Ceph component
      ├── kustomization.yaml                    # Ceph replacements for EDPM
      └── nova-ceph.yaml                        # Nova Ceph service definition

examples/dt/perfscale/scalelab/
  ├── service-values-ceph.yaml                  # Control plane Ceph values
  └── edpm/nodeset/values-ceph.yaml             # Data plane Ceph values
```

This modular design allows Ceph to be enabled/disabled by simply commenting/uncommenting two lines in the kustomization files.

