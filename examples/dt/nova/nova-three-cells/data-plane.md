# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the dt/nova/nova-three-cells/edpm directory
```
cd architecture/examples/dt/nova/nova-three-cells/edpm/
```
Edit the [edpm/nodeset/values.yaml](edpm/nodeset/values.yaml), the [edpm/nodeset2/values.yaml](edpm/nodeset2/values.yaml), and [edpm/deployment/values.yaml](edpm/deployment/values.yaml) files to suit 
your environment.
```
vi nodeset/values.yaml
vi nodeset2/values.yaml
vi deployment/values.yaml
```
Generate the dataplane nodeset CR.
```
kustomize build nodeset > dataplane-nodeset.yaml
```
Generate the dataplane nodeset2 CR.
```
kustomize build nodeset2 > dataplane-nodeset2.yaml
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

Create the second nodeset CR
```
oc apply -f dataplane-nodeset2.yaml
```
Wait for dataplane nodeset setup to finish
```
oc wait osdpns openstack-edpm-2 --for condition=SetupReady --timeout=600s
```

Start the deployment
```
oc apply -f dataplane-deployment.yaml
```

Wait for dataplane deployment to finish
```
oc wait osdpns openstack-edpm --for condition=Ready --timeout=60m
```
