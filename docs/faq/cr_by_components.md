# Creating Smaller CRs

## Question

The kustomize command builds and results in the OpenStack control
plane definitions and its dependent Custom Resources (CR).
```bash
kustomize build architecture/examples/va/hci > control-plane.yaml
```
The `control-plane.yaml` file contains CRs for the
`NodeNetworkConfigurationPolicy` (NNCP), the
`NetworkAttachmentDefinition`, MetalLB resources and
OpenStack resources. Is it possible to create a CR file with less
custom resources?

## Answer

Yes, it's possible to create CR files with less components and wait
before applying each CR file. E.g. the file `nncp.yaml` would contain
only `NodeNetworkConfigurationPolicy` CRs and
`NetworkAttachmentDefinition` and other CRs could exist in another
file like `networking.yaml`. The following process may be used to
generate these files using kustomize.

- Modify the
[va/hci/kustomization.yaml](https://github.com/openstack-k8s-operators/architecture/blob/main/va/hci/kustomization.yaml)
file so that the components list only has the nncp component:
```yaml
components:
- ../../lib/nncp
```
- Generate a file with only NNCP CRs:
```bash
kustomize build architecture/examples/va/hci > nncp.yaml
```
- Modify the
[va/hci/kustomization.yaml](https://github.com/openstack-k8s-operators/architecture/blob/main/va/hci/kustomization.yaml)
file so that the components list only has the networking component:
```yaml
components:
- ../../lib/networking
```
- Generate a file with only Networking CRs:
```bash
kustomize build architecture/examples/va/hci > networking.yaml
```

The above process may be continued for each component.

Note that [va/hci/kustomization.yaml](https://github.com/openstack-k8s-operators/architecture/blob/main/va/hci/kustomization.yaml)
is not the same file as
[examples/va/hci/kustomization.yaml](https://github.com/openstack-k8s-operators/architecture/blob/main/examples/va/hci/kustomization.yaml).
`/example/va/hci` is a specific example of a given VA where as
`/va/hci` is a generic HCI VA that may be customised and shared in
multiple examples or composed to make a larger VA.

This process will work for VAs (and DTs) besides HCI, but the paths
may be different. E.g.
[examples/va/nfv/sriov/kustomization.yaml](https://github.com/openstack-k8s-operators/architecture/blob/main/examples/va/nfv/sriov/kustomization.yaml)
differs from
[va/nfv/sriov/kustomization.yaml](https://github.com/openstack-k8s-operators/architecture/blob/main/va/nfv/sriov/kustomization.yaml)
and the later is in an `nfv` subdirectory
so each component is referred to using
`- ../../../lib/` instead of `- ../../lib/`.
