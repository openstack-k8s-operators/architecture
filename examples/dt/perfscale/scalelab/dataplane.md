# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed
- The EDPM nodes are pre-deployed with RHEL 9.4 and the SSH public keys are added with ctlplane IP

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the perfscale/scalelab/edpm directory
```
cd architecture/examples/dt/perfscale/scalelab/edpm
```
Edit the [nodeset/values.yaml](edpm/nodeset/values.yaml) file to suit your environment.
```
vi nodeset/values.yaml
```

### Optional: Enable Ceph backend

To enable Ceph backend for Nova ephemeral storage on compute nodes, see the [Ceph Configuration Guide](ceph.md).
If enabling Ceph, uncomment the Ceph lines in [edpm/nodeset/kustomization.yaml](edpm/nodeset/kustomization.yaml) and edit
[edpm/nodeset/values-ceph.yaml](edpm/nodeset/values-ceph.yaml).
```
vi nodeset/kustomization.yaml  # Uncomment Ceph component and resource
vi nodeset/values-ceph.yaml
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

**Note:** If Ceph is enabled, the dataplane will include Ceph client configuration and Nova will use RBD for ephemeral storage.