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

Due to the distributed zones architecture, each availability zone requires its own Nova configuration to use the local Glance endpoint. Instead of using a single global `nova-extra-config`, we use **AZ-specific EDPM custom services**.

### AZ-specific ConfigMaps

Each AZ has its own Nova configuration file:

- [edpm/computes/r0/nova-extra-config-az0.yaml](edpm/computes/r0/nova-extra-config-az0.yaml) - points to `glance-az0-internal.openstack.svc:9292`
- [edpm/computes/r1/nova-extra-config-az1.yaml](edpm/computes/r1/nova-extra-config-az1.yaml) - points to `glance-az1-internal.openstack.svc:9292`
- [edpm/computes/r2/nova-extra-config-az2.yaml](edpm/computes/r2/nova-extra-config-az2.yaml) - points to `glance-az2-internal.openstack.svc:9292`

Each file contains:
```ini
[DEFAULT]
# Triple the default of the following
reimage_timeout_per_gb = 60
[glance]
endpoint_override = https://glance-azX-internal.openstack.svc:9292
valid_interfaces = internal
[cinder]
cross_az_attach = False
catalog_info = volumev3:cinderv3:internalURL
```

### EDPM Custom Services

Each AZ uses its own EDPM custom service that references the appropriate ConfigMap:

- [edpm/computes/r0/nova-custom-az0.yaml](edpm/computes/r0/nova-custom-az0.yaml)
- [edpm/computes/r1/nova-custom-az1.yaml](edpm/computes/r1/nova-custom-az1.yaml)
- [edpm/computes/r2/nova-custom-az2.yaml](edpm/computes/r2/nova-custom-az2.yaml)

### Deployment Process

The ConfigMaps and custom services are automatically included when generating the nodeset CRs from each rack's directory. Each r0, r1, r2 directory contains its own AZ-specific configurations and generates the complete CRs including ConfigMaps and custom services.

### Nodeset Configuration

Each compute nodeset references its AZ-specific custom service:

- r0 nodesets use `nova-custom-az0` service
- r1 nodesets use `nova-custom-az1` service  
- r2 nodesets use `nova-custom-az2` service

This ensures that Nova compute services in each AZ connect to their local Glance endpoints for optimal performance and proper distributed zones functionality.

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
