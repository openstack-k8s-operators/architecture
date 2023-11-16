# Stage 1

Install the dependencies for Red Hat OpenStack Services on OpenShift operators

## Notes

Requires an OpenShift 4.12+ cluster with 3 master/worker combo-nodes, with Metal3 and a provisioning network available

## Steps

1. Create Namespaces
```bash
oc apply -f cert_manager_namespace.yaml -f metallb_namespace.yaml -f nmstate_namespace.yaml
```
2. Create OperatorGroups
```bash
oc apply -f cert_manager_operatorgroup.yaml -f metallb_operatorgroup.yaml -f nmstate_operatorgroup.yaml
```
3. Create Subscriptions
```bash
oc apply -f cert_manager_subscription.yaml -f metallb_subscription.yaml -f nmstate_subscription.yaml

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
4. Create Deploys
```bash
# MetalLB
oc apply -f metallb_deploy.yaml
timeout 300 bash -c "while ! (oc get pod --no-headers=true -l component=speaker -n metallb-system | grep speaker); do sleep 10; done"
oc wait pod -n metallb-system -l component=speaker --for condition=Ready --timeout=300s

# NMState
oc apply -f nmstate_deploy.yaml
timeout 300 bash -c "while ! (oc get pod --no-headers=true -l component=kubernetes-nmstate-handler -n openshift-nmstate| grep nmstate-handler); do sleep 10; done"
oc wait pod -n openshift-nmstate -l component=kubernetes-nmstate-handler --for condition=Ready --timeout=300s
timeout 300 bash -c "while ! (oc get deployments/nmstate-webhook -n openshift-nmstate); do sleep 10; done"
oc wait deployments/nmstate-webhook -n openshift-nmstate --for condition=Available --timeout=300s
```