# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nova/nova04delta directory
```
cd architecture/examples/dt/nova/nova04delta/control-plane
```
Edit the [networking/nncp/values.yaml](networking/nncp/values.yaml),
[networking/dns/values.yaml](networking/dns/values.yaml) and
[service-values.yaml](service-values.yaml) files to suit
your environment.
```
vi networking/nncp/values.yaml
vi networking/dns/values.yaml
vi service-values.yaml
```

## Apply node network configuration

Generate the node network configuration
```
kustomize build networking/nncp > nncp.yaml
```
Apply the NNCP CRs
```
oc apply -f nncp.yaml
```
Wait for NNCPs to be available
```
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

## Apply networking and control-plane configuration

Generate the control-plane and networking CRs.
```
kustomize build > control-plane.yaml
```
Apply the CRs
```
oc apply -f control-plane.yaml
```

Wait for control plane to be available
```
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```

## Apply Openshift DNS configuration for ctlplane DNS zone

Generate the `dns.operator/default` CR to update the ctlplane resolver
for the DNSMasq instance created during control-plane configuration.
```
kustomize build networking/dns > dns.yaml
```
Apply the CRs
```
oc apply -f dns.yaml
```