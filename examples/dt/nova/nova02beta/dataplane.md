# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nova/nova02beta/edpm directory
```
cd architecture/examples/dt/nova/nova02beta/edpm/
```
Edit the [nodeset/values.yaml](edpm/nodeset/values.yaml), the [nodeset2/values.yaml](edpm/nodeset2/values.yaml), 
and [deployment/values.yaml](edpm/deployment/values.yaml) files to suit 
your environment.
```
vi nodeset/values.yaml
vi nodeset2/values.yaml
vi deployment/values.yaml
```
Generate the dataplane nodeset CR's.
```
kustomize build nodeset > dataplane-nodeset.yaml
kustomize build nodeset2 > dataplane-nodeset2.yaml
```
Generate the dataplane deployment CR.
```
kustomize build deployment > dataplane-deployment.yaml
```

## Apply Initial CRs
Create the first nodeset CR
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
oc wait osdpns openstack-edpm --for condition=Ready --timeout=40m
```

## Generate yamls necessary to finialize Nvidia GPU installation
After the Nvidia drivers have been installed on the EDPM nodes, the computes need
to be rebooted in order to finalize the GPU installation. Below explains the
necessary steps to apply a reboot on the necessary nodesets.

Change to the nova/nova02beta/edpm-post-driver directory
```
cd architecture/examples/dt/nova/nova02beta/edpm-post-driver/
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

## Create Provider.yaml
Change to the nova/nova02beta/edpm-deploy-provider directory
```
cd architecture/examples/dt/nova/nova02beta/edpm-deploy-provider/
```
Edit the [nodeset/values.yaml](edpm-deploy-provider/nodeset/values.yaml) files to suit 
your environment.
```
vi nodeset/values.yaml
```
Edit the [deployment/values.yaml](edpm-deploy-provider/deployment/values.yaml) files to suit 
your environment.
```
vi deployment/values.yaml
```
Generate the dataplane service CR that will provide the provider.yaml.
```
kustomize build dataplaneservice > dataplane-provider-service.yaml
```
Generate the deployment that will leverage the dataplane service CR.
```
kustomize build deployment > dataplane-provider-deployment.yaml
```

## Create CRs for the provider.yaml
Create the OSPDS for the provider.yaml
```
oc apply -f dataplane-provider-service.yaml
```
Wait for dataplane service to finish
```
oc wait osdpns openstack-edpm --for condition=SetupReadyy --timeout=60m
```
Start the deployment
```
oc apply -f dataplane-provider-deployment.yaml
```
Wait for dataplane deployment to finish
```
oc wait osdpd edpm-deployment-provider --for condition=Ready --timeout=20m
```