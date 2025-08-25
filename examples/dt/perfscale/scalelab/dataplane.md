# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed
- The EDPM nodes are pre-deployed with RHEL 9.4 and the keys are added with ctlplane ip

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the perfscale/scalelab/edpm directory
```
cd architecture/examples/dt/perfscale/scalelab/edpm
```
Edit the [nodeset/values.yaml](edpm/nodeset/values.yaml) and [deployment/values.yaml](edpm/deployment/values.yaml) files to suit
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