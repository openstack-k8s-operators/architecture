# Apply follow up deployment

## Assumptions

- Initial [dataplane](edpm-pre.md) deployment has finalized and is successful

## Reboot EDPM Nodes
The EDPM Nodes will need a final reboot. This will require a new deployment that
will run `reboot-os` on the relevant EDPM Nodes.

The following commands should be executed from your controller.

Change to the post-driver directory.
```
cd architecture/examples/va/nvidia-vfio-passthrough/edpm-post-driver
```

Update [deployment](deployment/values.yaml) values to suit your environment.
```
vi deployment/values.yaml
```

Create and apply deployment.
```
kustomize build deployment > post-driver-deployment.yaml
oc apply -f post-driver-deployment.yaml
```
