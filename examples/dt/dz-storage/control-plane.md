# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.
- An infrastructure of spine/leaf routers exists, is properly connected to the
  OCP nodes and the routers are configured to support BGP.

## Initialize

Switch to the "openstack" namespace
```shell
oc project openstack
```
Change to the dz-storage/control-plane directory
```
cd architecture/examples/dt/dz-storage/control-plane
```
Edit the [networking/nncp/values.yaml](control-plane/networking/nncp/values.yaml) and
[service-values.yaml](control-plane/service-values.yaml) files to suit
your environment.
```shell
vi networking/nncp/values.yaml
vi service-values.yaml
```

Do not directly edit the secret files for Cinder matching
`cinder-volume-secrets-az*.yaml` or Manila matching
`manila-share-secrets-az*.yaml`. Instead edit the
`service-values.yaml` to contain the secret content
for Cinder and Manila to connect to the storage arrays.
When `kustomize` is run it will then insert these values.

In the `service-values.yaml` file, look for
the sections `cinder-volume-secrets-az0`, `cinder-volume-secrets-az1`,
`cinder-volume-secrets-az2`, `osp-secret-manila-az0`,
`osp-secret-manila-az1`, and `osp-secret-manila-az2` and replace the
`_replaced_` placeholders with your actual credentials and
configuration values. Additionally, update the `netapp_server_hostname`
values in the `cinderVolumes` sections (ontap-iscsi-az0, ontap-iscsi-az1,
ontap-iscsi-az2) by replacing `_replaced_` with your actual NetApp
cluster IP addresses. The example values use a NetApp
but may be adjusted for other storage arrays.

## Apply node network configuration

Generate the node network configuration
```shell
kustomize build networking/nncp > nncp.yaml
```
Apply the NNCP CRs
```shell
oc apply -f nncp.yaml
```
Wait for NNCPs to be available
```shell
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

## Apply the remaining networking configuration

Generate the networking CRs.
```shell
kustomize build networking > networking.yaml
```
Apply the CRs
```shell
oc apply -f networking.yaml
```

## Apply control-plane configuration

Generate the control-plane CRs and their secrets:
```shell
kustomize build > control-plane.yaml
```
Apply the CRs
```shell
oc apply -f control-plane.yaml
```

Wait for control plane to be available
```shell
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```
