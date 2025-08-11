# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane/README.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nvidia-vfio-passthrough directory
```
cd architecture/examples/va/nvidia-vfio-passthrough
```

### Create the BareMetalHost CRs

Edit the `edpm/nodeset/values.yaml` file to suit your environment. Pay special attention to the `baremetalhosts` section, where you will need to provide details for each of your baremetal compute nodes, including:
- `bmc.address`: The IP address of the Baseboard Management Controller (BMC).
- `bootMACAddress`: The MAC address of the network interface that the node will use to PXE boot.
- Other parameters as described in the main [README.md](README.md).

Additionally, you need to provide SSH keys for Nova live migration. The following keys in `edpm/nodeset/values.yaml` must be populated with base64 encoded values:
- `nova.migration.ssh_keys.private`
- `nova.migration.ssh_keys.public`

You can encode your keys using the `base64` command, for example: `cat ~/.ssh/id_rsa | base64 -w0`.

Also, ensure the `bmhLabelSelector` in `baremetalSetTemplate` matches the labels you have defined for your `baremetalhosts`. For example, if you use `app: openstack`, your `baremetalhosts` should have a corresponding label.

Before applying the nodeset configuration, you must also create the `bmc-secret` secret that contains the BMC credentials. You can create it with the following command:
```
oc create secret generic bmc-secret --from-literal=username=CHANGEME --from-literal=password=CHANGEME
```

Generate the dataplane nodeset CR, which includes the BareMetalHost definitions.
```
kustomize build edpm/nodeset > dataplane-nodeset.yaml
```
Apply the CRs to create the BareMetalHosts and the nodeset.
```
oc apply -f dataplane-nodeset.yaml
```

Wait for the BareMetalHosts to become available. You can monitor the status with:
```
oc get bmh -w
```
The state should change to `available`.

### Configure and deploy the dataplane

Edit `edpm/deployment/values.yaml` if needed.
```
vi edpm/deployment/values.yaml
```
Generate the dataplane deployment CR.
```
kustomize build edpm/deployment > dataplane-deployment.yaml
```

Wait for dataplane nodeset setup to finish.
```
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=600s
```

Start the deployment.
```
oc apply -f dataplane-deployment.yaml
```

Wait for dataplane deployment to finish.
```
oc wait osdpns openstack-edpm --for condition=Ready --timeout=60m
```

After the Nvidia drivers have been blacklisted on the EDPM nodes, and kernel args updated, edpm hosts will be
automatically rebooted.
