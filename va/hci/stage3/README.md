# Stage 3

Configure OCP cluster networking for OSP

## Steps

1. Create NNCPs
```bash
oc apply -f ocp_node_0_nncp.yaml -f ocp_node_1_nncp.yaml -f ocp_node_2_nncp.yaml
# CHANGEME: Set "osp/interface" below to the interface you are using as your OSP NIC
oc wait nncp -l osp/interface=enp7s0 --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```
2. Create NetAttachs
```bash
oc apply -f netattach_ctlplane.yaml -f netattach_internalapi.yaml -f netattach_storage.yaml -f netattach_tenant.yaml
```
3. Create MetalLB resources

```bash
oc apply -f metallb_ipaddresspools.yaml -f metallb_l2advertisement.yaml
```

A NetworkAttachmentDefinition is not required for storage management
network since that network is used by OpenStackDataPlane nodes but not
OpenStack pods hosted on OpenShift in this architecture.
