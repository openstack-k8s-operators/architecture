# Stage 4

Deploy the control plane

## Steps

1. Switch to "openstack" namespace
```bash
oc project openstack
```
2. Create NetConfig
```bash
oc apply -f netconfig.yaml
```
3. Create Secret
```bash
oc apply -f osp-secrets.yaml
```
4. Create OpenStackControlPlane and wait for it to finish deploying
```bash
oc apply -f openstackcontrolplane.yaml
oc wait osctlplane openstack-galera-network-isolation-3replicas --for condition=Ready --timeout=600s
```
