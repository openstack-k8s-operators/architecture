# Configuring and deploying the post-Ceph dataplane

## Assumptions

- The pre-Ceph [dataplane](dataplane-pre-ceph.md) was already deployed and Ceph was manually installed afterwards

## Initialize post-Ceph

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the osasinfra directory
```
cd architecture/examples/dt/osasinfra
```
Edit the [values.yaml](values.yaml) and [service-values.yaml](service-values.yaml)
files to suit your environment.
```
vi values.yaml
vi service-values.yaml
```
The ceph sections of [values.yaml](values.yaml) should have values like this.
```yaml
data:
    ceph:
        conf: $CONF
        keyring: $KEY

```
Where the values of the variables above can be retrieved by
running the following commands on the Ceph cluster.
```shell
CONF=$(cat /etc/ceph/ceph.conf | base64 -w 0)
KEY=$(cat /etc/ceph/ceph.client.openstack.keyring | base64 -w 0)
```

Generate the post-Ceph dataplane nodeset CR.
```
kustomize build > nodeset-post-ceph.yaml
```
Generate the post-Ceph dataplane deployment CR.
```
kustomize build deployment > deployment-post-ceph.yaml
```

## Create post-Ceph CRs

Create the nodeset CR
```
oc apply -f nodeset-post-ceph.yaml
```
Wait for post-Ceph dataplane nodeset setup to finish
```
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=10m
```
Create the deployment CR
```
oc apply -f deployment-post-ceph.yaml
```

Wait for control plane to be available after updating
```
oc wait osctlplane controlplane --for condition=Ready --timeout=40m
```

Wait for post-Ceph dataplane deployment to finish
```
oc wait osdpd edpm-deployment-post-ceph --for condition=Ready --timeout=1200s
```

## Finalize Nova computes

Ask Nova to discover all compute hosts
```bash
oc rsh nova-cell0-conductor-0 nova-manage cell_v2 discover_hosts --verbose
```
