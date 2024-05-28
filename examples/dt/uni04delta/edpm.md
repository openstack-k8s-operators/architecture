# Deploying the OpenStack dataplane

## Assumptions

- The [control plane](control-plane.md) has been successfully deployed.
- The [ceph](edpm-pre-ceph.md) has been successfully deployed and ceph has been installed.

## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to the delta's edpm directory

```bash
cd architecture/examples/dt/uni04delta
```

Modify the [values.yaml](values.yaml) with the following information

- SSH keys to be used for accessing the deployed compute nodes.
- SSH keys to be use for Nova migration.
- Ceph Configuration information

> All values must be in base64 encoded format.

### Compute access

1. Set `data['authorized']` with the value of all OpenStack Compute host SSH
  keys.
2. Set `data['private']` with the contents of the SSH private key to be used
  for accessing the dataplane compute nodes.
3. Set `data['public']` with the contents of the SSH public key used for
  accessing the dataplane compute nodes.

### Nova migration

1. Set `data['nova']['migration']['ssh_keys']['private']` with the content of
  the SSH private key to be used for potential future migration.
2. Set `data['nova']['migration']['ssh_keys']['public']` with the content of
  the SSH public key to be used for potential future migration.

## CRs nodeset

Generate the nodeset CRs.

```bash
kustomize build > edpm-nodeset.yaml
```

## Create CRs nodeset

```bash
oc apply -f edpm-nodeset.yaml
```

Wait for nodeset deployment to finish

```bash
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=1200s
```

## CRs deployment

Change to the deployment folder

```bash
cd deployment
```
Generate the deployment CRs.

```bash
kustomize build > edpm.yaml
```

## Create CRs deployment

```bash
oc apply -f edpm.yaml
```

Wait for deployment to finish

```bash
oc wait osdpd edpm-deployment --for condition=Ready --timeout=2400s
```

