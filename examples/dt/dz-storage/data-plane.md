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
Change to the `dz-storage` directory
```
cd architecture/examples/dt/dz-storage/
```

## Networker Nodes

Edit the networker values.yaml files corresponding to each rack (r0, r1 and r2)
to suit your environment:
- [edpm/networkers/r0/values.yaml](edpm/networkers/r0/values.yaml)
- [edpm/networkers/r1/values.yaml](edpm/networkers/r1/values.yaml)
- [edpm/networkers/r2/values.yaml](edpm/networkers/r2/values.yaml)
```
vi values.yaml
```

## Compute Nodes

Edit the compute values.yaml files corresponding to each rack (r0, r1 and r2)
to suit your environment:
- [edpm/computes/r0/values.yaml](edpm/computes/r0/values.yaml)
- [edpm/computes/r1/values.yaml](edpm/computes/r1/values.yaml)
- [edpm/computes/r2/values.yaml](edpm/computes/r2/values.yaml)
```
vi values.yaml
```

## Storage Related Compute Node Overrides

Edit the following file to contain any desired override to the Nova configuration:

- [edpm/computes/nova-extra-config.yaml](edpm/computes/nova-extra-config.yaml)

The file is prepopulated with the following:
```ini
[DEFAULT]
# Triple the default of the following
reimage_timeout_per_gb = 60
```
The configmap can be genereated with the following command.
```
kustomize build edpm/computes/
```

As per [the docs](https://docs.redhat.com/en/documentation/red_hat_openstack_services_on_openshift/18.0/html-single/customizing_the_red_hat_openstack_services_on_openshift_deployment/index#proc_configuring-a-node-set-for-a-feature-or-workload_custom_dataplane),

> The Compute service (nova) provides a default ConfigMap CR named nova-extra-config, where you can add generic configuration that applies to all the node sets that use the default nova service. If you use this default nova-extra-config ConfigMap to add generic configuration to be applied to all the node sets, then you do not need to create a custom service.

The EDPM `nova` service created in the next step will apply the above configuration to all Compute nodes.

## Create Networker and Compute Nodeset CRs

Generate the networkers dataplane nodeset CRs for each rack.
```
kustomize build edpm/networkers/r0 > edpm-r0-networker-nodeset.yaml
kustomize build edpm/networkers/r1 > edpm-r1-networker-nodeset.yaml
kustomize build edpm/networkers/r2 > edpm-r2-networker-nodeset.yaml
```
Generate the computes dataplane nodeset CRs for each rack.
```
kustomize build edpm/computes/r0 > edpm-r0-compute-nodeset.yaml
kustomize build edpm/computes/r1 > edpm-r1-compute-nodeset.yaml
kustomize build edpm/computes/r2 > edpm-r2-compute-nodeset.yaml
```

## Create EDPM  Deployment CR
Generate the dataplane deployment CR.
```
kustomize build edpm/deployment > edpm-deployment.yaml
```

## Apply the Nodeset CRs

Apply the Networker nodeset CRs
```
oc apply -f edpm/networkers/r0/edpm-r0-networker-nodeset.yaml
oc apply -f edpm/networkers/r1/edpm-r1-networker-nodeset.yaml
oc apply -f edpm/networkers/r2/edpm-r2-networker-nodeset.yaml
```
Wait for Networker dataplane nodesets setup to finish
```
oc wait osdpns r0-networker-nodes --for condition=SetupReady --timeout=600s
oc wait osdpns r1-networker-nodes --for condition=SetupReady --timeout=600s
oc wait osdpns r2-networker-nodes --for condition=SetupReady --timeout=600s
```
Apply the Compute nodeset CRs
```
oc apply -f edpm/computes/r0/edpm-r0-compute-nodeset.yaml
oc apply -f edpm/computes/r1/edpm-r1-compute-nodeset.yaml
oc apply -f edpm/computes/r2/edpm-r2-compute-nodeset.yaml
```
Wait for Compute dataplane nodesets setup to finish
```
oc wait osdpns r0-compute-nodes --for condition=SetupReady --timeout=600s
oc wait osdpns r1-compute-nodes --for condition=SetupReady --timeout=600s
oc wait osdpns r2-compute-nodes --for condition=SetupReady --timeout=600s
```

## Apply the deployment
Start the deployment
```
oc apply -f edpm/deployment/edpm-deployment.yaml
```
Wait for dataplane deployment to finish
```
oc wait osdpd edpm-deployment --for condition=Ready --timeout=2400s
```
