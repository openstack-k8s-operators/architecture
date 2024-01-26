# Deploying the OpenStack dataplane

## Assumptions

- The [control plane](control-plane.md) has been successfully deployed.

## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to the alpha's directory

```bash
cd architecture/examples/dt/uni01alpha
```

Modify the [values.yaml](values.yaml) with the following information

- SSH keys to be used for accessing the deployed compute nodes.
- SSH keys to be use for Nova migration.

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

## CRs

Generate the dataplane CRs.

```bash
kustomize build > data-plane.yaml
```

## Create CRs

```bash
oc apply -f data-plane.yaml
```

Wait for dataplane deployment to finish

```bash
oc wait osdpd edpm-deployment --for condition=Ready --timeout=1200s
```
