# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `lvms-local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace

```shell
oc project openstack
```

Change to the dcn directory

```shell
cd architecture/examples/dt/dcn
```

Edit the [control-plane/networking/nncp/values.yaml](control-plane/networking/nncp/values.yaml) file to suit your environment.

```shell
vi control-plane/networking/nncp/values.yaml
```

The example in `examples/dt/dcn/` assumes that Ceph will be
the storage backend and that the storage management network
will only be used by EDPM nodes as the
[Ceph cluster network](https://docs.ceph.com/en/latest/rados/configuration/network-config-ref).
Since no Ceph services run on OpenShift in such a configuration,
the storage management network is not connected to OCP nodes and
thus not included in the `NodeNetworkConfigurationPolicy` (NNCP)
definition by default.

It's possible to include the storage management network in the NNCP
definition by doing the following:

1. Uncomment the `nncp-storagemgmt` component in
   [control-plane/networking/nncp/kustomization.yaml](control-plane/networking/nncp/kustomization.yaml)
2. Uncomment `storagemgmt_ip` for each node in
   [control-plane/networking/nncp/values.yaml](control-plane/networking/nncp/values.yaml)

The above is not necessary if you are using Ceph.

## Apply node network configuration

Generate the node network configuration

```shell
kustomize build control-plane/networking/nncp > nncp.yaml
```

Apply the NNCP CRs

```shell
oc apply -f nncp.yaml
```

Wait for NNCPs to be available

```shell
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

## Apply networking configuration

Generate the networking CRs.

```shell
kustomize build control-plane/networking > networking.yaml
```

Apply the networking CRs

```shell
oc apply -f networking.yaml
```

Wait for MetalLB to be available

```shell
oc -n metallb-system wait pod -l app=metallb -l component=speaker --for condition=Ready --timeout=5m
```

## Apply control-plane configuration

Generate the control-plane CRs.

```shell
kustomize build control-plane > control-plane.yaml
```

Apply the CRs

```shell
oc apply -f control-plane.yaml
```

Wait for control plane to be available

```shell
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```
