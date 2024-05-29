# OpenStack on Highly Available OpenShift Cluster

This is a collection of CR templates that represent a validated Red Hat OpenStack Services on OpenShift deployment that has the following characteristics:

- 3 masters plus 3 workers OpenShift cluster
- 1 worker dedicated to run testOperator taint-tolerant pods, see [test-operator](https://github.com/openstack-k8s-operators/test-operator)
- 3-replica Galera database
- 3-replica RabbitMQ
- OVN networking
- Network isolation over a single NIC
- 3 compute nodes
- Swift enabled and used as Glance backend


# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the pidone directory
```
cd architecture/examples/va/pidone
```
Edit the [nncp/values.yaml](nncp/values.yaml) and
[service-values.yaml](service-values.yaml) files to suit
your environment.
```
vi nncp/values.yaml
vi service-values.yaml
```

## Apply node network configuration

Generate the node network configuration
```
kustomize build nncp > nncp.yaml
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

## Apply dataplane nodeset and deployment configuration

Generate the dataplane nodeset CR.
```
kustomize build edpm/nodeset > nodeset.yaml
```
Apply the CR
```
oc apply -f nodeset.yaml
```

Wait for the nodeset to reach the SetupReady condition
```
oc -n openstack wait openstackdataplanenodeset openstack-edpm --for condition=SetupReady --timeout=600s
```

Generate the dataplane deployment CR.
```
kustomize build edpm/deployment > deployment.yaml
```
Apply the CR
```
oc apply -f deployment.yaml
```

Wait for the dataplanedeployment to reach the "Ready" condition
```
oc -n openstack wait openstackdataplanedeployment edpm-deploymenti --for condition=Ready --timeout=40m
```
