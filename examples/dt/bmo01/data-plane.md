# Deploying the OpenStack dataplane

## Assumptions

- The [control plane](control-plane.md) has been successfully deployed.

## Initialize

Switch to the "openstack" namespace

```bash
oc project openstack
```

Change to the dataplane directory

```bash
cd architecture/examples/dt/bmo01/dataplane
```

### Configure BMO - Provisioning to watch all namespaces

```
oc patch provisioning provisioning-configuration --type merge -p '{"spec":{"watchAllNamespaces": true }}'
```

### Configure BMO - Provisioning to use external network for virtual-media

```
oc patch provisioning provisioning-configuration --type merge -p '{"spec":{"virtualMediaViaExternalNetwork": true }}'
```

### Create the BareMetalHost CRs

```
pushd baremetalhosts
```

Modify the [values.yaml](dataplane/baremetalhosts/values.yaml), for each of the nodes (`leaf0-0`, `leaf0-1`, `leaf1-0` and `leaf1-1`) set:
- `bmc.address`
- `bootMACAddress`
- `rootDeviceHints`
- `preprovisioningNetworkData`

Modify the [bmc-secret.env](dataplane/baremetalhosts/bmc-secret.env) *env* with the BMC `username` and `password`, for example:
```
username=root
password=S3cr3t
```

```
kustomize build > baremetalhosts.yaml
oc apply -f baremetalhosts.yaml
```

Wait for BareMetalHosts to reach state: `active`

```
oc get bmh -w

NAME      STATE        CONSUMER   ONLINE   ERROR   AGE
leaf1-0   preparing               false            1m38s
leaf1-1   preparing               false            1m38s
leaf0-1   preparing               false            1m38s
leaf0-0   preparing               false            1m38s
leaf1-0   available               false            2m38s
leaf0-1   available               false            2m38s
leaf0-0   available               false            2m38s
leaf1-1   available               false            2m38s
```

```
popd
```

## Create the dataplane secrets

```
pushd secrets
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

### Generate the dataplane-secrets CRs.

```bash
kustomize build > dataplane-secrets.yaml
```

### Create CRs the dataplane-secrets CRs.

```bash
oc apply -f dataplane-secrets.yaml
```

```
popd
```

## Create the dataplane-nodeset CRs

Generate the dataplane CRs.

```
pushd nodesets
```

```bash
kustomize build > dataplane-nodesets.yaml
```

## Create CRs

```bash
oc apply -f dataplane-nodesets.yaml
```

Wait for dataplane deployment to finish

```bash
oc wait osdpd edpm-deployment --for condition=Ready --timeout=1200s
```
