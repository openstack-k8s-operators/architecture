# Define Zones and Toplogies

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the `dz-storage` directory
```
cd architecture/examples/dt/dz-storage
```
Observe CRs which will be generated to define zones and topologies
```
kustomize build topology
```

## Examine Toplogies

The Distributed Zones architecture schedules pods either in a specific
zone or ensures that a pod's replicas are spread by the scheduler
across all zones. The `OpenStackControlPlane` CRD supports a
`topologyRef` which may be applied to its pods. The `topologyRef`
references a
[Toplogy CRD](https://github.com/openstack-k8s-operators/infra-operator/pull/325)
which should be defined before deploying he `OpenStackControlPlane`.

An example of a Topology CRD which spreads pods across all zones
is [default-spread-pods.yaml](default-spread-pods.yaml)

An example of three Toplogy CRDs which schedule a pod in a specific zone
(either A, B or C) are [azone-node-affinity.yaml](azone-node-affinity.yaml),
[bzone-node-affinity.yaml](bzone-node-affinity.yaml) and
[czone-node-affinity.yaml](czone-node-affinity.yaml)

Adjust these toplogies to suit your needs. See the
[Controlling pod placement onto nodes (scheduling)](https://docs.redhat.com/en/documentation/openshift_container_platform/4.16/html/nodes/controlling-pod-placement-onto-nodes-scheduling)
guide for examples.

## Examine Zones

The toplogies from the previous section assume that the OCP nodes have
been labeled with zones. Create a variation of the example
[node-zone-labels.yaml](node-zone-labels.yaml) in the `topology`
directory so that your nodes are assigned into different zones.

The
[Node labels section](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/#node-labels)
of the upstream Pod Topology Spread Constraints documentation
has more details. See also
[kubernetes/api/core/v1/well_known_labels.go](https://github.com/kubernetes/api/blob/master/core/v1/well_known_labels.go#L26).

## Define Zones and Toplogies

Once you are satisfied with the zones and toplogies apply them.
```
oc apply -k topology
```
