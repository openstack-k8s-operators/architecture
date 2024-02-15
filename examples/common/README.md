# Common CRs

All VAs and DTs assume that these CRs have been created.

## OLM

The [olm](olm) directory contains a kustomization which will generate
Namespace, OperatorGroup, and Subscription CRs. Creating these CRs
will install the OpenStack K8S operators and their dependencies.

Observe CRs which will be generated.
```
kustomize build examples/common/olm/
```
Create the CRs.
```
oc apply -k examples/common/olm/
```
Watch the OpenStack operator pods start.
```
oc get pods -w -n openstack-operators
```
The following commands can be used to confirm that each step of this
procedure is complete.
```
while ! (oc get pod --no-headers=true -l name=cert-manager-operator -n cert-manager-operator| grep "cert-manager-operator"); do sleep 10; done
oc wait pod -n cert-manager-operator --for condition=Ready -l name=cert-manager-operator --timeout=300s
while ! (oc get pod --no-headers=true -l app=cainjector -n cert-manager | grep "cert-manager-cainjector"); do sleep 10; done
oc wait pod -n cert-manager -l app=cainjector --for condition=Ready --timeout=300s
while ! (oc get pod --no-headers=true -l app=webhook -n cert-manager | grep "cert-manager-webhook"); do sleep 10; done
oc wait pod -n cert-manager -l app=webhook --for condition=Ready --timeout=300s
while ! (oc get pod --no-headers=true -l app=cert-manager -n cert-manager | grep "cert-manager"); do sleep 10; done
oc wait pod -n cert-manager -l app=cert-manager --for condition=Ready --timeout=300s

timeout 300 bash -c "while ! (oc get pod --no-headers=true -l control-plane=controller-manager -n metallb-system | grep metallb-operator-controller); do sleep 10; done"
oc wait pod -n metallb-system --for condition=Ready -l control-plane=controller-manager --timeout=300s
timeout 300 bash -c "while ! (oc get pod --no-headers=true -l component=webhook-server -n metallb-system | grep metallb-operator-webhook); do sleep 10; done"
oc wait pod -n metallb-system --for condition=Ready -l component=webhook-server --timeout=300s

timeout 300 bash -c "while ! (oc get deployments/nmstate-operator -n openshift-nmstate); do sleep 10; done"
oc wait deployments/nmstate-operator -n openshift-nmstate --for condition=Available --timeout=300s
```

# MetalLB

Observe CRs which will be generated.
```
kustomize build examples/common/metallb/
```
Create the CRs.
```
oc apply -k examples/common/metallb/
```
The following commands can be used to confirm that each step of this
procedure is complete.
```
timeout 300 bash -c "while ! (oc get pod --no-headers=true -l component=speaker -n metallb-system | grep speaker); do sleep 10; done"
oc wait pod -n metallb-system -l component=speaker --for condition=Ready --timeout=300s
```

# NMState

Observe CRs which will be generated.
```
kustomize build examples/common/nmstate/
```
Create the CRs.
```
oc apply -k examples/common/nmstate/
```
The following commands can be used to confirm that each step of this
procedure is complete.
```
timeout 300 bash -c "while ! (oc get pod --no-headers=true -l component=kubernetes-nmstate-handler -n openshift-nmstate| grep nmstate-handler); do sleep 10; done"
oc wait pod -n openshift-nmstate -l component=kubernetes-nmstate-handler --for condition=Ready --timeout=300s
timeout 300 bash -c "while ! (oc get deployments/nmstate-webhook -n openshift-nmstate); do sleep 10; done"
oc wait deployments/nmstate-webhook -n openshift-nmstate --for condition=Available --timeout=300s
```
