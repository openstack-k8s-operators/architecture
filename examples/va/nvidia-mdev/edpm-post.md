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
reboot. The example deployment runs `reboot-os`, followed by `validate-nvidia`,
before applying `compute-provider` configuration to the relevant EDPM nodes.

Keep `validate-nvidia` immediately after the reboot, including when customizing
`servicesOverride` in CI. It loads the NVIDIA/vGPU modules without force options,
starts the vGPU services, checks `nvidia-smi -L`, and requires the configured mdev
profiles (or at least one NVIDIA profile when no list is configured). It applies
to both RPM and `.run` installations and fails the deployment before Nova provider
configuration or guest tests if the driver cannot operate after reboot. Compiling
a kernel interface is not by itself proof of supported vGPU operation.

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
