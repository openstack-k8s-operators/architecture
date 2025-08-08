# Configuring LVM cluster and related CRs

## Assumptions

- OCP is deployed on baremetal scalelab machines using jetlag

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the perfscale/scalelab/lvms directory
```
cd architecture/examples/dt/perfscale/scalelab/lvms
```
Edit the [lvms/lvm-cluster/values.yaml](edpm/nodeset/values.yaml) file to suit your environment.
```
vi lvm-cluster/values.yaml
```
Generate the openshift-storage namespace, operatorgroup and subscription CR.
```
kustomize build . > lvms.yaml
```
Generate the lvm cluster CR.
```
kustomize build lvm-cluster > lvm-cluster.yaml
```

## Create CRs
Create the ns, og and subscription CRs
```
oc apply -f lvms.yaml
```
Wait for all resource setup to finish.
```
# Wait for Namespace 'openshift-storage'
timeout 300 bash -c "while ! (oc get ns openshift-storage >/dev/null 2>&1); do sleep 5; done"

# Wait for OperatorGroup 'openshift-storage-operatorgroup'
timeout 300 bash -c "while ! (oc get operatorgroup openshift-storage-operatorgroup -n openshift-storage >/dev/null 2>&1); do sleep 5; done"

# Wait for LVMCluster CR to exist
timeout 300 bash -c "while ! (oc get LVMCluster -n openshift-storage >/dev/null 2>&1); do sleep 5; done"

# Wait for Subscription 'lvms'
timeout 300 bash -c "while ! (oc get subscription lvms -n openshift-storage >/dev/null 2>&1); do sleep 5; done"
```

Create the LVM cluster CR
```
oc apply -f lvm-cluster.yaml
```

Wait for cluster to crerate
```
# Wait for LVMCluster 'lvmcluster' to exist
timeout 300 bash -c "while ! (oc get lvmcluster lvmcluster -n openshift-storage >/dev/null 2>&1); do sleep 5; done"

# Wait for LVMCluster 'lvmcluster' to be Ready
timeout 300 bash -c "while [[ \"\$(oc get lvmcluster lvmcluster -n openshift-storage -o jsonpath={.status.ready} 2>/dev/null)\" != \"true\" ]]; do sleep 5; done"

# Wait for LVMS operator pods to be Ready
timeout 300 bash -c "while [[ -z \"\$(oc get pods -n openshift-storage -l app.kubernetes.io/name=lvms-operator -o jsonpath={.items[*].status.containerStatuses[0].ready} 2>/dev/null)\" ]]; do sleep 5; done"
```