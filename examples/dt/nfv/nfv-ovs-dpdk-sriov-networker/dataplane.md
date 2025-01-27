# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
TBC

## Create CRs
Create the nodesets CRs
```
TBC
```
Wait for dataplane nodesets setup to finish
```
TBC
```

Start the deployment
```
oc apply -f dataplane-deployment.yaml
```

Wait for dataplane deployment to finish
```
TBC
```
