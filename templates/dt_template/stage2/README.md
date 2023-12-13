# Stage 2

Install the Red Hat OpenStack Services on OpenShift operators

## Steps

1. Create Namespaces
```bash
oc apply -f namespaces.yaml
```
2. Create OperatorGroup
```bash
oc apply -f operatorgroup.yaml
```
3. Create CatalogSource
```bash
oc apply -f catalogsource.yaml
```
4. Create Subscription
```bash
oc apply -f subscription.yaml
timeout 300 bash -c 'until $(oc get csv -l operators.coreos.com/openstack-operator.openstack-operators -n openstack-operators | grep -q Succeeded); do sleep 5; done'
```
