# Configuring and deploying Ceph nodes


## Assumptions

- The [control plane](control-plane.md) has been created
  and successfully deployed.


## Initialize pre-Ceph

Switch to the "openstack" namespace.
```bash
oc project openstack
```

Change to the uni05epsilon directory.
```bash
cd architecture/examples/dt/uni05epsilon
```

Edit the [edpm-pre-ceph/nodeset/values.yaml](edpm-pre-ceph/nodeset/values.yaml)
file to suit your environment.
```bash
vi edpm-pre-ceph/nodeset/values.yaml
```

Generate the pre-Ceph dataplane nodeset CR.
```bash
kustomize build edpm-pre-ceph/nodeset > nodeset-pre-ceph.yaml
```

Generate the pre-Ceph dataplane deployment CR.
```bash
kustomize build edpm-pre-ceph/deployment > deployment-pre-ceph.yaml
```


## Create pre-Ceph CRs

Create the nodeset CR.
```bash
oc apply -f nodeset-pre-ceph.yaml
```

Wait for pre-Ceph dataplane nodeset setup to finish.
```bash
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=10m
```

Start the deployment.
```bash
oc apply -f deployment-pre-ceph.yaml
```

Wait for pre-Ceph dataplane deployment to finish.
```bash
oc wait osdpd edpm-deployment-pre-ceph --for condition=Ready --timeout=30m
```
