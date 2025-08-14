# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nvidia-mdev-passthrough directory
```
cd architecture/examples/va/nvidia-mdev-passthrough
```
Edit the [edpm/nodeset/values.yaml](edpm/nodeset/values.yaml) and [edpm/deployment/values.yaml](edpm/deployment/values.yaml) files to suit your environment.
```
vi edpm/nodeset/values.yaml
vi edpm/deployment/values.yaml
```
Generate the dataplane nodeset CR.
```
kustomize build edpm/nodeset > dataplane-nodeset.yaml
```
Generate the dataplane deployment CR.
```
kustomize build edpm/deployment > dataplane-deployment.yaml
```

## Create CRs and do initial deployment
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
oc wait osdpns openstack-edpm --for condition=Ready --timeout=60m
```
