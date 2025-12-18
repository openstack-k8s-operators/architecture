# Configuring and deploying the pre-Ceph dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize pre-Ceph

Switch to the "openstack" namespace

```shell
oc project openstack
```

Change to the dcn directory

```shell
cd architecture/examples/dt/dcn
```

Edit the [edpm-pre-ceph/nodeset/values.yaml](edpm-pre-ceph/nodeset/values.yaml) file to suit
your environment.

```shell
vi edpm-pre-ceph/nodeset/values.yaml
```

Generate the pre-Ceph dataplane nodeset CR.

```shell
kustomize build edpm-pre-ceph/nodeset > dataplane-nodeset-pre-ceph.yaml
```

Generate the pre-Ceph dataplane deployment CR.

```shell
kustomize build edpm-pre-ceph/deployment > dataplane-deployment-pre-ceph.yaml
```

## Create pre-Ceph CRs

Create the nodeset CR

```shell
oc apply -f dataplane-nodeset-pre-ceph.yaml
```

Wait for pre-Ceph dataplane nodeset setup to finish

```shell
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=600s
```

Start the deployment

```shell
oc apply -f dataplane-deployment-pre-ceph.yaml
```

Wait for pre-Ceph dataplane deployment to finish

```shell
oc wait osdpd edpm-deployment-pre-ceph --for condition=Ready --timeout=1200s
```
