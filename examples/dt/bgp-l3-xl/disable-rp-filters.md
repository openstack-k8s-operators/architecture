# Disable RP filters on OCP workers

Reverse path filters need to be disabled on OCP workers running Openstack services.
This is needed to make OCP workers forward traffic properly based on the BGP
advertisements received.

The following CR needs to be applied:
```
apiVersion: tuned.openshift.io/v1
kind: Tuned
metadata:
  name: openshift-no-reapply-sysctl
  namespace: openshift-cluster-node-tuning-operator
spec:
  profile:
  - data: |
      [main]
      summary=Optimize systems running OpenShift (provider specific parent profile)
      include=-provider-${f:exec:cat:/var/lib/ocp-tuned/provider},openshift

      [sysctl]
      net.ipv4.conf.enp7s0.rp_filter=0
      net.ipv4.conf.enp8s0.rp_filter=0
    name: openshift-no-reapply-sysctl
  recommend:
  - match:
    - label: kubernetes.io/hostname
      value: worker-0
    - label: kubernetes.io/hostname
      value: worker-1
    - label: kubernetes.io/hostname
      value: worker-2
    - label: node-role.kubernetes.io/master
    operand:
      tunedConfig:
        reapply_sysctl: false
    priority: 15
    profile: openshift-no-reapply-sysctl
```
