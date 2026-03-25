# Configure and deploy the data planes

## Assumptions

- Both the central (`openstack`) and leaf (`openstack2`) control planes are
  deployed and Ready (see [control-plane.md](control-plane.md)).
- The cross-region CA bundle and Barbican transport URL have been configured
  by the post-deploy hooks.

## Initialize

Change to the multi-namespace-skmo directory
```
cd architecture/examples/va/multi-namespace-skmo
```

## Central region dataplane (openstack namespace)

### Prepare CRs

Edit the dataplane values files to suit your environment
```
vi ../multi-namespace/edpm/nodeset/values.yaml
vi ../multi-namespace/edpm/values.yaml
```
Generate the dataplane nodeset CR
```
kustomize build ../multi-namespace/edpm/nodeset > nodeset.yaml
```
Generate the dataplane deployment CR
```
kustomize build ../multi-namespace/edpm > deployment.yaml
```

### Apply CRs

Create the nodeset CR
```
oc apply -f nodeset.yaml
```
Wait for dataplane nodeset setup to finish
```
oc -n openstack wait osdpns openstack-edpm --for condition=SetupReady --timeout=10m
```
Start the deployment
```
oc apply -f deployment.yaml
```

## Leaf region dataplane (openstack2 namespace)

The leaf dataplane can be deployed in parallel with the central dataplane.

### Prepare CRs

Edit the leaf dataplane values files to suit your environment
```
vi ../multi-namespace/edpm2/nodeset/values.yaml
vi ../multi-namespace/edpm2/values.yaml
```
Generate the leaf dataplane nodeset CR
```
kustomize build ../multi-namespace/edpm2/nodeset > nodeset2.yaml
```
Generate the leaf dataplane deployment CR
```
kustomize build ../multi-namespace/edpm2 > deployment2.yaml
```

### Apply CRs

Create the leaf nodeset CR
```
oc apply -f nodeset2.yaml
```
Wait for both dataplanes to finish setup
```
oc -n openstack wait osdpns openstack-edpm --for condition=SetupReady --timeout=10m
oc -n openstack2 wait osdpns openstack-edpm --for condition=SetupReady --timeout=10m
```
Start the leaf deployment
```
oc apply -f deployment2.yaml
```
Wait for both dataplane deployments to complete
```
oc -n openstack wait osdpns openstack-edpm --for condition=Ready --timeout=60m
oc -n openstack2 wait osdpns openstack-edpm --for condition=Ready --timeout=60m
```
