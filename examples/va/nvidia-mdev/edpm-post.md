# Reboot EDPM Nodes and optionally apply provider.yaml

## Assumptions

- Initial [dataplane](edpm-pre.md) deployment has finalized and is successful

## Create a post deployment to finalize Nvidia configuration
Log out of EDPMs and return to architecture repo on the controller.

```
cd architecture/examples/va/nvidia-mdev/edpm-post-driver
```

### Optional: Create a provider.yaml
Create a configmap for the ```provider.yaml``` to map ```CUSTOM_TRAITS``` to
the relevant resource providers and their MDevs, then create the corresponding
service that will apply the configMap.

Update the post [nodeset](edpm-post-driver/nodeset/values.yaml) values to how
you wish to map resource provider to traits.

```
vi nodeset/values.yaml
kustomize build nodeset > compute-provider-service.yaml
oc apply -f compute-provider-service.yaml
```

## Update post deployment configration and apply
In order to finish Nvidia Driver installation the EDPM Nodes will need a final
reboot. This will require a new deployment that will run ```reboot-os``` on the
relevant EDPM Nodes.

If applying the ```provider.yaml``` configuration via OSPDS from the previous
optional step, then include the service ```compute-provider``` to the list of
services as well.

Update [deployment](edpm-post-driver/deployment/values.yaml) values to suit
your environment and to include provider.yaml if using.
```
vi deployment/values.yaml
```

Create and apply deployment.
```
kustomize build deployment > post-driver-deployment.yaml
oc apply -f post-driver-deployment.yaml
```
