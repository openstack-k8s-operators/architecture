# Apply follow up deployment

## Assumptions

- Initial [dataplane](edpm-pre.md) deployment has finalized and is successful

## Apply necessary configurations to EDPM Nodes
The following commands should be executed from your controller.

Change to the post-driver directory.
```
cd architecture/examples/va/nvidia-mdev-passthrough/edpm-post-driver
```

### Optional: Create a provider.yaml
Create a configmap for the provider.yaml to map CUSTOM_TRAITS to the relevant
resource providers and their GPUs, then create the corresponding service that
will apply the configMap.

Update the post [nodeset](nodeset/values.yaml) values to how
you wish to map resource provider to traits.

```
vi nodeset/values.yaml
kustomize build nodeset > compute-provider-service.yaml
oc apply -f compute-provider-service.yaml
```

## Reboot EDPM Nodes and optionally apply provider.yaml
The EDPM Nodes will need a final reboot. This will require a new deployment that
will run `reboot-os` on the relevant EDPM Nodes.

Update [deployment](deployment/values.yaml) values to suit your environment and
to include provider.yaml if using.
```
vi deployment/values.yaml
```

Create and apply deployment.
```
kustomize build deployment > post-driver-deployment.yaml
oc apply -f post-driver-deployment.yaml
```
