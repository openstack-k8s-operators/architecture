# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane/README.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nova/nova04delta directory
```
cd architecture/examples/dt/nova/nova04delta/edpm
```
Edit the [nodeset/values.yaml](nodeset/values.yaml)
and [deployment/values.yaml](deployment/values.yaml) files to suit
your environment.
In `nodeset/values.yaml`, pay special attention to the `baremetalhosts` section. You will need to provide details for each of your baremetal compute nodes, including:
- `bmc.address`: The IP address of the Baseboard Management Controller (BMC).
- `bootMACAddress`: The MAC address of the network interface that the node will use to PXE boot.
- Other parameters as described in the main [README.md](README.md).

Additionally, you need to provide SSH keys for Nova live migration. The following keys in `nodeset/values.yaml` must be populated with base64 encoded values:
- `nova.migration.ssh_keys.private`
- `nova.migration.ssh_keys.public`

You can encode your keys using the `base64` command, for example: `cat ~/.ssh/id_rsa | base64 -w0`.
```
vi nodeset/values.yaml
vi deployment/values.yaml
```

### Create the BareMetalHost CRs

Also, ensure the `bmhLabelSelector` in `baremetalSetTemplate` matches the labels you have defined for your `baremetalhosts`. For example, if you use `app: openstack`, your `baremetalhosts` should have a corresponding label.

Before applying the nodeset configuration, you must also create the `bmc-secret` secret that contains the BMC credentials. You can create it with the following command:
```
oc create secret generic bmc-secret --from-literal=username=CHANGEME --from-literal=password=CHANGEME
```

Generate the dataplane nodeset CR, which includes the BareMetalHost definitions.
```
kustomize build nodeset > dataplane-nodeset.yaml
```

Apply the CR to create the BareMetalHost and the nodeset.
```
oc apply -f dataplane-nodeset.yaml
```

Wait for the BareMetalHosts to become available. You can monitor the status with:
```
oc get bmh -w
```
The state should change to `available`.

### Configure and deploy the dataplane

Edit `deployment/values.yaml` if needed.
```
vi deployment/values.yaml
```
Generate the dataplane deployment CR.
```
kustomize build deployment > dataplane-deployment.yaml
```

Wait for dataplane nodeset setup to finish.
```
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=600s
```

Start the deployment
```
oc apply -f dataplane-deployment.yaml
```

Wait for dataplane deployment to finish
```
oc wait osdpd edpm-deployment --for condition=Ready --timeout=40m
```

// FIXME(bogdando): use edpm_reboot_strategy=force to avoid this extra step?

## Generate yamls necessary to finialize Nvidia GPU installation
After the Nvidia drivers have been blacklisted on the EDPM nodes, the computes need
to be rebooted. Below explains the necessary steps to apply a reboot on the necessary nodesets.

Change to the nova/nova04delta/edpm-post-driver directory
```
cd architecture/examples/dt/nova/nova04delta/edpm-post-driver/
```
Edit the [deployment/values.yaml](edpm-post-driver/deployment/values.yaml) files to suit
your environment.
```
vi deployment/values.yaml
```
Generate the dataplane deployment CR.
```
kustomize build deployment > dataplane-post-driver-deployment.yaml
```

## Create CRs to finalize GPU installation
Start the deployment
```
oc apply -f dataplane-post-driver-deployment.yaml
```

Wait for dataplane deployment to finish
```
oc wait osdpd edpm-deployment-post-driver --for condition=Ready --timeout=20m
```
