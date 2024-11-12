# Common Design Pitfalls

This document lists common pitfalls that have been observed in the process of creating 
and modifying VAs and DTs.

## Accidental OpenStackControlPlane Overwrites

In general, it is a best practice to keep all kustomizations (`patches`, `replacements`, etc) 
for a particular resource in one `kustomization.yaml` file.  Sometimes, however, it is 
necessary to only perform a subset of `OpenStackControlPlane` kustomizations at a certain stage 
of the deployment process.  For instance, you might not want to kustomize an `OpenStackControlPlane`
CR with certain data during its initial creation stage because that data is not yet available
for use.  Thus it would make sense to have a later stage and `kustomization.yaml` file to
add those kustomzations once the requisite data is available (perhaps during the data plane
deployment stage).

**What is crucial to keep in mind is that any kustomizations to a resource in an earlier stage
will be lost/overwritten in later stages where that same resource is modified _if_ those stages
do not reference the same `kustomization.yaml` that the earlier stage utilized.**  Thus it is
best to have a base `kustomization.yaml` for a given resource for all kustomizations common to
all stages -- and all those stages should thus reference that `kustomization.yaml`.  Then, if
later stages need specific changes for that resource, a separate `kustomization.yaml` can be also
used to apply those additional kustomizations beyond the base ones.  This approach is also
preferred to creating two somewhat-or-mostly duplicate `kustomization.yaml`s, one for the earlier
stage and one for a later stage.  Keeping things DRY by using a common base will make future
potential changes to the `kustomization.yaml`s less prone to error, as changes to the common file
will automatically be picked up by all deployment stages.

As an illustrative example of the best practice mentioned above, consider the following directory
structure:

```
some_dt_or_va/control_plane/kustomization.yaml
some_dt_or_va/data_plane/kustomization.yaml
```

If the `data_plane/kustomization.yaml` needs to modify the `OpenStackControlPlane`, then it should
reference `../control_plane/kustomization.yaml` as a `Component` and then add additional `replacements`
and/or `patches` as needed.  If it were to instead reference this repo's [lib/control-plane](../../lib/control-plane)
directory as its base `OpenStackControlPlane` `Component`, then the `../control_plane/kustomization.yaml` 
kustomizations would be lost, since the `OpenStackControlPlane` CR would be generated and applied without 
them.

It also follows in this scenario that, as mentioned above, the `OpenStackControlPlane` kustomizations for
its initial creation stage should be located in one and only one `kustomization.yaml`.  Thus you would
want to avoid something like this...

```
some_dt_or_va/control_plane/kustomization.yaml
some_dt_or_va/control_plane/some_subdir/kustomization.yaml
some_dt_or_va/data_plane/kustomization.yaml
```

..._if_ `some_dt_or_va/control_plane/some_subdir/kustomization.yaml` has further kustomizations to the
`OpenStackControlPlane` beyond `some_dt_or_va/control_plane/kustomization.yaml`.  (It would be fine, for
instance, if that subdirectory was modifying some other resource like `NodeNetworkConfigurationPolicy`).
The reason for this is again that, if later stages do not want to accidentally overwrite earlier
`OpenStackControlPlane` kustomizations, those later stages will need to reference both
`../control_plane/kustomization.yaml` and `../control_plane/some_subdir/kustomization.yaml` in the case
that those stages are modifying the `OpenStackControlPlane`.  It would be better for the two directories
to be collapsed into one, such that a single `kustomization.yaml` can be referenced as a `Component` to
include all the previous stage's kustomizations and not inadvertently overwrite them.
