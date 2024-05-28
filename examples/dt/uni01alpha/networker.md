# Configuring and deploying Networker nodes

## Assumptions

- The [control plane](control-plane.md) has been created and successfully
  deployed.

## Steps

```bash
# 1. Switch to openstack namespace

    $ oc project openstack

# 2. Change the working directory to uni-alpha

    $ pushd architecture/examples/dt/uni01alpha

# 3. Modify [networker/values.yaml](networker/values.yaml) file to suit your
#    environment.

    $ pushd networker
    $ vi values.yaml

# 4. Generate the networker data plane deployment plan.

    $ kustomize build  > edpm-networker.yaml

# 5. Create the CRs

    $ oc apply -f edpm-networker.yaml

# 6. Wait for Networker data plane deployment to complete

    $ oc wait osdpd networker-deploy --for condition=Ready --timeout=1200s
    $ popd
```
