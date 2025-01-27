# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace:
```
oc project openstack
```

Change to the `nfv/nfv-ovs-dpdk-sriov-networker/edpm directory:

```
cd examples/dt/nfv/nfv-ovs-dpdk-sriov-networker
```

Edit the [edpm/computes/values.yaml](edpm/computes/values.yaml), 
[edpm/networkers/values.yaml](edpm/networkers/values.yaml) and
[edpm/deployment/values.yaml](edpm/deployment/values.yaml) files to suit your
environment.

Generate the dataplane nodesets CRs:
```
kustomize build edpm/networkers > edpm/networkers/edpm-networker-nodeset.yaml
kustomize build edpm/computes > edpm/computes/edpm-compute-nodeset.yaml
```

Generate the dataplane deployment CR:
```
kustomize build edpm/deployment > edpm/deployment/edpm-deployment.yaml
```

## Apply the CRs
Apply the nodesets CRs:
```
oc apply -f edpm/networkers/edpm-networker-nodeset.yaml
oc apply -f edpm/computes/edpm-compute-nodeset.yaml
```

Wait for dataplane nodesets setup to finish:
```
oc wait osdpns compute-nodes --for condition=SetupReady --timeout=45m
oc wait osdpns networker-nodes --for condition=SetupReady --timeout=45m
```

Apply the deployment:
```
oc apply -f edpm/deployment/edpm-deployment.yaml
```

Wait for dataplane deployment to finish
```
oc wait osdpns networker-nodes --for condition=Ready --timeout=90m
oc wait osdpns compute-nodes --for condition=Ready --timeout=90m
```
