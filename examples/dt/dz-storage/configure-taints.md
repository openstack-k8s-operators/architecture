# Apply taints on OCP tester node

This OCP worker node should not run any Openstack service apart from those
created by the test-operator.
It should also run a metallb's speaker pod, in order to obtain the proper
network configuration.
Due to this, taints should be configured on this worker.

Execute the following command:
```
oc patch node/worker-9 --type merge --patch '
  spec:
    taints:
      - effect: NoSchedule
        key: testOperator
        value: "true"
      - effect: NoExecute
        key: testOperator
        value: "true"
'
```
