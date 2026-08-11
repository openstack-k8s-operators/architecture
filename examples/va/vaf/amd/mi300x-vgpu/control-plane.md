# Configure networking and deploy the OpenStack control plane

## Assumptions

- A storage class already exists and supports dynamic provisioning.

## Initialize

Switch to the `openstack` namespace:
```
oc project openstack
```

Change to the `mi300x-vgpu` directory:
```
cd architecture/examples/va/vaf/amd/mi300x-vgpu
```

Edit the network values and service values to match your environment:
```
vi nncp/values.yaml
vi service-values.yaml
```

## Apply node network configuration

Generate the node network configuration CRs:
```
kustomize build nncp > nncp.yaml
```

Apply the NNCP CRs:
```
oc apply -f nncp.yaml
```

Wait for NNCPs to be configured:
```
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

## Apply networking and control-plane configuration

Generate the control-plane and networking CRs:
```
kustomize build . > control-plane.yaml
```

Apply the CRs:
```
oc apply -f control-plane.yaml
```

Wait for the control plane to be ready:
```
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```
