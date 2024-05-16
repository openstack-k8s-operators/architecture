# Configuring and deploying the dataplane - networker and compute nodes

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed
- An infrastructure of spine/leaf routers exists, is properly connected to the
  pre-provisioned EDPM nodes and the routers are configured to support BGP.

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the bgp_dt01/ directory
```
cd architecture/examples/dt/bgp/bgp_dt01/
```
Edit the [edpm/networkers/values.yaml](edpm/networkers/values.yaml) file to suit
your environment.
```
vi values.yaml
```
Edit the [edpm/networkers/values.yaml](edpm/computes/values.yaml) file to suit
your environment.
```
vi values.yaml
```

## Create Networker and Compute Nodeset CRs

Generate the networkers dataplane nodeset CR.
```
kustomize build edpm/networkers > edpm-networker-nodeset.yaml
```
Generate the computes dataplane nodeset CR.
```
kustomize build edpm/computes > edpm-compute-nodeset.yaml
```

## Create EDPM  Deployment CR
Generate the dataplane deployment CR.
```
kustomize build edpm/deployment > edpm-deployment.yaml
```

## Apply the Nodeset CRs

Apply the Networker nodeset CR
```
oc apply -f edpm-networker-nodeset.yaml
```
Wait for Networker dataplane nodeset setup to finish
```
oc wait osdpns networker-nodes --for condition=SetupReady --timeout=600s
```
Apply the Compute nodeset CR
```
oc apply -f edpm-compute-nodeset.yaml
```
Wait for Compute dataplane nodeset setup to finish
```
oc wait osdpns compute-nodes --for condition=SetupReady --timeout=600s
```

## Apply the deployment
Start the deployment
```
oc apply -f edpm-deployment.yaml
```
Wait for dataplane deployment to finish
```
oc wait osdpd edpm-deployment --for condition=Ready --timeout=2400s
```
