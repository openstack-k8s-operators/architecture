# Configuring and deploying Ceph nodes

## Assumptions

- The [control plane](control-plane.md) has been created and successfully
  deployed.

## Steps

```bash
# 1. Switch to openstack namespace

    $ oc project openstack

# 2. Change the working directory to uni-delta

    $ pushd architecture/examples/dt/uni-delta

# 3. Modify [ceph/values.yaml](ceph/values.yaml) file to suit your environment.

    $ pushd ceph
    $ vi values.yaml

# 4. Generate the Ceph data plane deployment plan.

    $ kustomize build --load-restrictor LoadRestrictionsNone > edpm-ceph.yaml

# 5. Create the CRs

    $ oc apply -f edpm-ceph.yaml

# 6. Wait for Ceph data plane deployment to complete

    $ oc wait osdpd edpm-ceph --for condition=Ready --timeout=1200s
    $ popd
```
