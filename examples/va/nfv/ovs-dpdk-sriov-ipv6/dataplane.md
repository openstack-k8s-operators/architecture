# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nfv/ovs-dpdk-sriov/edpm directory

> **Note**: The IPv6 scenario reuses the dataplane configuration from the standard
> ovs-dpdk-sriov scenario, as there are no differences in the EDPM configuration
> between IPv4 and IPv6 deployments. The IPv6 networking is configured at the
> control plane level (NNCP and service values).

```
cd architecture/examples/va/nfv/ovs-dpdk-sriov/edpm
```
Edit the [nodeset/values.yaml](nodeset/values.yaml) and [deployment/values.yaml](deployment/values.yaml) files to suit
your environment.
```
vi nodeset/values.yaml
vi deployment/values.yaml
```
Generate the dataplane nodeset CR.
```
kustomize build nodeset > dataplane-nodeset.yaml
```
Generate the dataplane deployment CR.
```
kustomize build deployment > dataplane-deployment.yaml
```

## Create CRs
Create the nodeset CR
```
oc apply -f dataplane-nodeset.yaml
```
Wait for dataplane nodeset setup to finish
```
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=600s
```

Start the deployment
```
oc apply -f dataplane-deployment.yaml
```

Wait for dataplane deployment to finish
```
oc wait osdpns openstack-edpm --for condition=Ready --timeout=40m
```
