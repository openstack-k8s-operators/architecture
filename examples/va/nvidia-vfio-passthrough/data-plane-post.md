# Apply follow up deployment

// FIXME(bogdando): use edpm_reboot_strategy=force to avoid this extra step?

## Assumptions

- Initial [dataplane](data-plane-pre.md) deployment has finalized and is successful

## Reboot EDPM Nodes
The EDPM Nodes will need a final reboot in order to apply changes done by the
vfio-pci-bind service for blacklisted host drivers. This will require a new
deployment that will run `reboot-os` on the relevant EDPM Nodes.

The following commands should be executed from your controller.

Change to the post-driver directory.
```
cd architecture/examples/va/nvidia-vfio-passthrough/edpm-post-driver
```

Update [deployment](edpm-post-driver/deployment/values.yaml) values to suit your environment.
```
vi deployment/values.yaml
```

Create and apply deployment.
```
kustomize build deployment > post-driver-deployment.yaml
oc apply -f post-driver-deployment.yaml
```
