# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed
- An infrastructure of spine/leaf routers exists, is properly connected to the
  pre-provisioned EDPM nodes and the routers are configured to support BGP.

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the bgp/edpm directory
```
cd architecture/examples/dt/bgp/edpm
```
Edit the [edpm/nodeset/values.yaml](edpm/nodeset/values.yaml) file to suit
your environment.
```
vi values.yaml
```
Generate the dataplane nodeset CR.
```
kustomize build edpm/nodeset > dataplane-nodeset.yaml
```
Generate the dataplane deployment CR.
```
kustomize build edpm/deployment > dataplane-deployment.yaml
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
oc wait osdpd edpm-deployment --for condition=Ready --timeout=1200s
```
