# Stage 5

Deploy the initial data plane to prepare for CephHCI installation

## Notes

Step 1 can be skipped if you already have 3 metal3.io/v1alpha1 BareMetalHosts in the "available"
state in the "openshift-machine-api" namespace and have labelled them as "app: openstack".
Further details on these resources can be found [here](https://access.redhat.com/documentation/en-us/openshift_container_platform/4.13/html/post-installation_configuration/post-install-bare-metal-configuration).

## Steps

1. (Optional -- see above) Create BareMetalHosts and wait for them to become available (and label them)
```bash
oc apply -f baremetalhosts.yaml
oc label bmh -n openshift-machine-api openshift-worker-0 openshift-worker-1 openshift-worker-2 app=openstack
timeout 720 bash -c 'until [ $(oc get bmh -n openshift-machine-api -l app=openstack | grep -c available) == "3" ]; do sleep 5; done'
```
2. Install OpenStackDataPlaneService
```bash
oc apply -f openstackdataplaneservice_reposetup.yaml
```
3. Create Secrets
```bash
oc apply -f baremetalsetpasswordsecret.yaml -f dataplanesshsecret.yaml
```
4. Create OpenStackDataPlaneNodeSet and wait for BaremetalHosts to be provisioned
```bash
oc apply -f openstackdataplanenodeset.yaml
while ! (oc get osbms openstack-edpm-ipam); do sleep 2; done
oc wait osbms openstack-edpm-ipam --for condition=Ready --timeout=720s
```
5. Create OpenStackDataPlaneDeployment and wait for it to finish
```bash
oc apply -f openstackdataplanedeployment.yaml
oc wait osdpd openstack-edpm-ipam --for condition=Ready --timeout=720s
```