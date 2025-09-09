# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane/README.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nova/nova04delta directory
```
cd architecture/examples/va/nova/nova04delta/edpm
```
Edit the [nodeset/values.yaml](nodeset/values.yaml), [nodeset2/values.yaml](nodeset/values.yaml)
and [deployment/values.yaml](deployment/values.yaml) files to suit
your environment.
```
vi nodeset/values.yaml
vi nodeset2/values.yaml
vi deployment/values.yaml
```
Generate the dataplane nodeset CRs.
```
kustomize build nodeset > dataplane-nodeset.yaml
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
oc apply -f dataplane-nodeset2.yaml
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

## Generate yamls necessary to finialize Nvidia GPU installation
After the Nvidia drivers have been blacklisted on the EDPM nodes, the computes need
to be rebooted. Below explains the necessary steps to apply a reboot on the necessary nodesets.

Change to the nova/nova04delta/edpm-post-driver directory
```
cd architecture/examples/dt/nova/nova04delta/edpm-post-driver/
```
Edit the [deployment/values.yaml](edpm-post-driver/deployment/values.yaml) files to suit
your environment.
```
vi deployment/values.yaml
```
Generate the dataplane deployment CR.
```
kustomize build deployment > dataplane-post-driver-deployment.yaml
```

## Create CRs to finalize GPU installation
Start the deployment
```
oc apply -f dataplane-post-driver-deployment.yaml
```

Wait for dataplane deployment to finish
```
oc wait osdpd edpm-deployment-post-driver --for condition=Ready --timeout=20m
```