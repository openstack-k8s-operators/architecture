# Configuring and deploying the dataplanes

## Assumptions

- The [control plane](control-plane.md) for both OSP clouds have been created and successfully deployed

## Initialize

Change to the multi-namespace directory
```
cd architecture/examples/va/multi-namespace
```

## Dataplane one

### Prepare CRs
Edit the [edpm/nodeset/values.yaml](edpm/nodeset/values.yaml) and [edpm/values.yaml](edpm/values.yaml) files to suit 
your environment.
```
vi edpm/nodeset/values.yaml
vi edpm/values.yaml
```
Generate the dataplane nodeset CR.
```
kustomize build edpm/nodeset > nodeset.yaml
```
Generate the dataplane deployment CR.
```
kustomize build edpm > deployment.yaml
```

### Apply CRs
Create the nodeset CR
```
oc apply -f nodeset.yaml
```
Wait for dataplane nodeset setup to finish
```
oc wait -n openstack osdpns openstack-edpm --for condition=SetupReady --timeout=600s
```

Start the deployment
```
oc apply -f deployment.yaml
```

Wait for dataplane deployment to finish
```
oc wait -n openstack osdpns openstack-edpm --for condition=Ready --timeout=40m
```

## Dataplane two

### Prepare CRs
Edit the [edpm2/nodeset/values.yaml](edpm2/nodeset/values.yaml) and [edpm2/values.yaml](edpm2/values.yaml) files to suit 
your environment.
```
vi edpm/2nodeset/values.yaml
vi edpm2/values.yaml
```
Generate the dataplane nodeset CR.
```
kustomize build edpm2/nodeset > nodeset2.yaml
```
Generate the dataplane deployment CR.
```
kustomize build edpm2 > deployment2.yaml
```

### Apply CRs
Create the nodeset CR
```
oc apply -f nodeset2.yaml
```
Wait for dataplane nodeset setup to finish
```
oc wait -n openstack2 osdpns openstack-edpm --for condition=SetupReady --timeout=600s
```

Start the deployment
```
oc apply -f deployment2.yaml
```

Wait for dataplane deployment to finish
```
oc wait -n openstack2 osdpns openstack-edpm --for condition=Ready --timeout=40m
```
