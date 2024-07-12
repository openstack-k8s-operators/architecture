# Configuring and deploying Ceph nodes

## Assumptions

- The [control plane](control-plane.md) has been created and successfully
  deployed.

## Steps

```bash
# 1. Switch to openstack namespace

    $ oc project openstack

# 2. Change the working directory to uni04delta-ipv6/edpm-pre-ceph/nodeset

    $ pushd architecture/examples/dt/uni04delta-ipv6/edpm-pre-ceph/nodeset

# 3. Modify [values.yaml](values.yaml) file to suit your environment.

    $ vi values.yaml

# 4. Generate the Ceph nodeset deployment plan.

    $ kustomize build > nodeset-pre-ceph.yaml

# 5. Create the CRs

    $ oc apply -f nodeset-pre-ceph.yaml

# 6. Wait for Ceph nodeset deployment to complete

    $ oc wait osdpns ceph-nodes --for condition=SetupReady --timeout=600s
    $ popd

# 7. Change the working directory to uni04delta-ipv6/edpm-pre-ceph

    $ pushd architecture/examples/dt/uni04delta-ipv6/edpm-pre-ceph

# 8. Generate the Ceph data plane deployment plan.

    $ kustomize build > deployment-pre-ceph.yaml

# 9. Create the CRs

    $ oc apply -f deployment-pre-ceph.yaml

# 10. Wait for Ceph data plane deployment to complete

    $ oc wait osdpd edpm-deployment-pre-ceph --for condition=Ready --timeout=1500s
    $ popd

# 11. Install Ceph

    Use ci-framework/playbooks/ceph.yml and
    ci-framework-data/artifacts/zuul_inventory.yml

```
