# Deploying the OpenStack dataplane


## Assumptions

- The [control plane](control-plane.md) has been successfully deployed.
- The pre-Ceph [dataplane](dataplane-pre-ceph.md) was already deployed
  and Ceph was manually installed afterwords.


## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to the Epsilon's directory

```bash
cd architecture/examples/dt/uni05epsilon
```

Modify the [values.yaml](values.yaml)
and [service-values.yaml](service-values.yaml)
with the following information:

- SSH keys to be used for accessing the deployed compute nodes.
- SSH keys to be use for Nova migration.
- Ceph configuration and keyring details.

> All values must be in base64 encoded format!


### Compute access

1. Set `data['ssh_keys']['authorized']` with the value of all OpenStack Compute
   host SSH keys.
2. Set `data['ssh_keys']['private']` with the contents of the SSH private key
   to be used for accessing the dataplane compute nodes.
3. Set `data['ssh_keys']['public']` with the contents of the SSH public key
   used for accessing the dataplane compute nodes.


### Nova migration

1. Set `data['nova']['migration']['ssh_keys']['private']` with the content of
  the SSH private key to be used for potential future migration.
2. Set `data['nova']['migration']['ssh_keys']['public']` with the content of
  the SSH public key to be used for potential future migration.


### Ceph configuration

The ceph sections of [values.yaml](values.yaml) should have values like this.
```yaml
data:
  ceph:
    conf: $CONF
    keyring: $KEY
```

The values of the two variables above can be retrieved by
running the following commands on the Ceph cluster.
```bash
CONF=$(cat /etc/ceph/ceph.conf | base64 -w 0)
KEY=$(cat /etc/ceph/ceph.client.openstack.keyring | base64 -w 0)
```


## CRs nodeset

Generate the nodeset CRs.
```bash
kustomize build > nodeset-post-ceph.yaml
```


## Create CRs nodeset

Create the nodeset CR.
```bash
oc apply -f nodeset-post-ceph.yaml
```

Wait for post-Ceph dataplane nodeset setup to finish.
```bash
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=10m
```


## CRs deployment

Change to the deployment folder.
```bash
cd deployment
```

Generate the deployment CRs.
```bash
kustomize build > deployment-post-ceph.yaml
```


## Create CRs deployment

Create the dataplane CR.
```bash
oc apply -f deployment-post-ceph.yaml
```

Wait for post-Ceph dataplane deployment to finish.
```bash
oc wait osdpd edpm-deployment-post-ceph --for condition=Ready --timeout=40m
```
