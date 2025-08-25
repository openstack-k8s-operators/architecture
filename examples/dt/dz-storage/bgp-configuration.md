# Create BGPConfiguration after controplane is deployed

An empty BGPConfiguration Openshift resource needs to be created.
The infra-operator will detect this resource is created and will automatically
apply the required Openshift BGP configuration.
OCP 4.18 release is necessary for this.

The following CR needs to be applied:
```
apiVersion: network.openstack.org/v1beta1
kind: BGPConfiguration
metadata:
  name: bgpconfiguration
  namespace: openstack
spec: {}
```
