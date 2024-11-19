# Common Design Pitfalls

This document lists common pitfalls that have been observed in the process of
creating and modifying VAs and DTs.

## Accidental OpenStackControlPlane Overwrites

In general, it is a best practice to keep all kustomizations (`patches`,
`replacements`, etc) for a particular resource in one `kustomization.yaml`
file.

In some cases it is necessary to only perform a subset of
`OpenStackControlPlane` kustomizations at a certain stage of the deployment
process. For instance, you might not want to kustomize an
`OpenStackControlPlane` CR with certain data during its initial creation stage
because that data is not yet available for use. In the case of a multi-stage
deployment, it would make sense to have a separate `kustomization.yaml` file to
add those kustomizations once the requisite data is available (perhaps during
the data plane deployment stage).

**What is crucial to keep in mind is that any kustomizations to a resource in
an earlier stage will be lost/overwritten in later stages where that same
resource is modified _if_ those stages do not reference the same
`kustomization.yaml` that the earlier stage utilized.**

It is best to have a base `kustomization.yaml` for a given resource for all
kustomizations common to all stages -- and all those stages should reference
that `kustomization.yaml`. If later stages need specific changes for that
resource, a separate `kustomization.yaml` can used to apply those additional
kustomizations beyond the base ones.

The use of common base files is preferred to creating two nearly-identical
`kustomization.yaml` files; one for the earlier stage and one for a later
stage. Keeping things DRY by using a common base will make future potential
changes to the `kustomization.yaml` files less prone to error, as changes to
the common file will automatically be picked up by all deployment stages.

As an illustrative example of the best practice mentioned above, consider the
following directory structure:

```
some_dt_or_va/control_plane/kustomization.yaml
some_dt_or_va/data_plane/kustomization.yaml
```

If the `data_plane/kustomization.yaml` needs to modify the
`OpenStackControlPlane`, then it should reference
`../control_plane/kustomization.yaml` as a `Component` and then add additional
`replacements` and/or `patches` as needed. 

If it were to instead reference this repositories
[lib/control-plane](../../lib/control-plane) directory as its base
`OpenStackControlPlane` `Component`, then the
`../control_plane/kustomization.yaml` kustomizations would be lost, since the
`OpenStackControlPlane` CR would be generated and applied without them.

The kustomizations for an `OpenStackControlPlane` resource should be within a
single `kustomization.yaml` that contains the kustomizations for the initial
creation stage. You want to avoid the use of multiple files, such as creating
an additional sub-directory within the same base directory containing the
configuration. The following would be an example to avoid:

```
some_dt_or_va/control_plane/kustomization.yaml
some_dt_or_va/control_plane/some_subdir/kustomization.yaml
some_dt_or_va/data_plane/kustomization.yaml
```

In some cases having an additional nested directory may be valid, in the case a
subdirectory was modifying some other resource like
`NodeNetworkConfigurationPolicy`.

If later stages do not want to accidentally overwrite earlier
`OpenStackControlPlane` kustomizations, those later stages need to reference
both `../control_plane/kustomization.yaml` and
`../control_plane/some_subdir/kustomization.yaml` so that those stages are
modifying the `OpenStackControlPlane`.

It would be better for the two directories to be collapsed into one, such that
a single `kustomization.yaml` can be referenced as a `Component` to include all
the previous stage's kustomizations and not inadvertently overwrite them.
