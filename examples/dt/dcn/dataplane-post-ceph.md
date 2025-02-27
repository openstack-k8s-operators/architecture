# Configuring and deploying the post-Ceph dataplane

## Assumptions

- The pre-Ceph [dataplane](dataplane-pre-ceph.md) was already deployed and Ceph was manually installed afterwords

## Initialize post-Ceph

Switch to the "openstack" namespace

```shell
oc project openstack
```

Change to the dcn directory

```shell
cd architecture/examples/dt/dcn
```

Edit the [values.yaml](values.yaml) and [service-values.yaml](service-values.yaml)
files to suit your environment.

```shell
vi values.yaml
vi service-values.yaml
```

Generate the post-Ceph dataplane nodeset CR.

```shell
kustomize build > nodeset-post-ceph.yaml
```

Generate the post-Ceph dataplane deployment CR.

```shell
kustomize build deployment > deployment-post-ceph.yaml
```

## Create post-Ceph CRs

Create the nodeset CR

```shell
oc apply -f nodeset-post-ceph.yaml
```

Wait for post-Ceph dataplane nodeset setup to finish

```shell
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=1200s
```

Create the deployment CR

```shell
oc apply -f deployment-post-ceph.yaml
```

Wait for control plane to be available after updating

```shell
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```

Wait for post-Ceph dataplane deployment to finish

```shell
oc wait osdpd edpm-deployment-post-ceph --for condition=Ready --timeout=2800s
```

## Finalize Nova computes

Ask Nova to discover all compute hosts

```shell
oc rsh nova-cell0-conductor-0 nova-manage cell_v2 discover_hosts --verbose
```

Create Host Aggregates. For example, to create a host aggregate with the name az0, use the following command:

```shell
oc rsh openstackclient openstack aggregate create --zone az0 az0
```

Add compute host to aggregate. To add a compute host to the aggregate, use the following command:

```shell
oc rsh openstackclient openstack aggregate add host az0 edpm-compute-0.ctlplane.example.com
```

## Additional Availability Zones

The above will result in `az0` with 3 compute nodes and one ceph cluster being deployed. To deploy additional AZs, e.g. `az1` and `az2`, each with 3 more compute nodes and one more ceph cluster, create updated values files and re-apply the kustomizations. An Ansible role which does this in our CI system for testing is available to be reviewed for details.

<https://github.com/openstack-k8s-operators/ci-framework/tree/main/roles/ci_dcn_site>

## Availability Zone scale down

This DT includes an example of how to scale down one of the deployed AZs. The example 
values in examples/dt/dcn/control-plane/scaledown/service-values.yaml have an example
of how to DTs should look when AZ1 is removed. To view them run the following command.

```shell
kustomize build architecture/examples/dt/dcn/control-plane/scaledown/
```