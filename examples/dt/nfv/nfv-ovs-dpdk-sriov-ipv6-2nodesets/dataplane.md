# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nfv/nfv-ovs-dpdk-sriov-2nodesets/edpm directory

> **Note**: The IPv6 2-nodesets scenario reuses the dataplane configuration from the standard
> nfv-ovs-dpdk-sriov-2nodesets scenario, as there are no differences in the EDPM configuration
> between IPv4 and IPv6 deployments. The IPv6 networking is configured at the
> control plane level (NNCP and service values).

```
cd examples/dt/nfv/nfv-ovs-dpdk-sriov-2nodesets/edpm
```
Edit the [nodeset/values.yaml](edpm/nodeset/values.yaml), [nodeset2/values.yaml](edpm/nodeset2/values.yaml)
and [deployment/values.yaml](deployment/values.yaml) files to suit your environment.
```
vi nodeset/values.yaml
vi nodeset2/values.yaml
vi deployment/values.yaml
```
Generate the dataplane nodesets CRs.
```
kustomize build nodeset > dataplane-nodeset.yaml
kustomize build nodeset2 > dataplane-nodeset2.yaml
```
Generate the dataplane deployment CR.
```
kustomize build deployment > dataplane-deployment.yaml
```

## Create CRs
Create the nodesets CRs
```
oc apply -f dataplane-nodeset.yaml
oc apply -f dataplane-nodeset2.yaml
```
Wait for dataplane nodesets setup to finish
```
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=600s
oc wait osdpns openstack-edpm-2 --for condition=SetupReady --timeout=600s
```

Start the deployment
```
oc apply -f dataplane-deployment.yaml
```

Wait for dataplane deployment to finish
```
oc wait osdpns openstack-edpm --for condition=Ready --timeout=40m
```
