# Configure networking and deploy the OpenStack control plane

## Assumptions

A StorageClass already exists and supports dynamic provisioning.

## Initialize

Switch to the `openstack` namespace:
```
oc project openstack
```

Change to the `rtx-pro-6000-gpu-passthrough/control-plane` directory:
```
cd architecture/examples/va/vaf/nvidia/rtx-pro-6000-gpu-passthrough/control-plane
```

Edit the network values, DNS values and service values to match your environment:
```
vi networking/nncp/values.yaml
vi networking/dns/values.yaml
vi service-values.yaml
```

## Apply node network configuration

Generate the node network configuration CRs:
```
kustomize build networking/nncp > nncp.yaml
```

Apply the NNCP CRs:
```
oc apply -f nncp.yaml
```

Wait for NNCPs to be configured:
```
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

## Apply networking configuration

Generate the networking CRs (MetalLB, NetConfig, NetworkAttachmentDefinitions):
```
kustomize build networking > networking.yaml
```

Apply the CRs:
```
oc apply -f networking.yaml
```

## Apply control-plane configuration

Generate the control-plane CRs:
```
kustomize build > control-plane.yaml
```

Apply the CRs:
```
oc apply -f control-plane.yaml
```

Wait for the control plane to be ready:
```
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```

## Apply OpenShift DNS configuration for the ctlplane DNS zone

Generate the `dns.operator/default` CR to update the ctlplane resolver for the
DNSMasq instance created during control-plane configuration:
```
kustomize build networking/dns > dns.yaml
```

Apply the CRs:
```
oc apply -f dns.yaml
```
