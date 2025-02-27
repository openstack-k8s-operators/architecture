# Configuring and deploying the dataplane and networker

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nfv/ovs-dpdk-networker/networker directory
```
cd architecture/examples/va/nfv/ovs-dpdk-networker/networker
```
Edit the [nodeset/values.yaml](networker/nodeset/values.yaml) file to suit
your environment.
```
vi nodeset/values.yaml
```
Generate the networker nodesets CRs.
```
kustomize build nodeset > networker-nodeset.yaml
```

Change to the nfv/ovs-dpdk-networker/edpm directory
```
cd architecture/examples/va/nfv/ovs-dpdk-networker/edpm
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
