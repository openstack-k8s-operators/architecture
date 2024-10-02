# Configuring and deploying the dataplane

## Assumptions

- The [control plane](control-plane.md) has been created and successfully deployed

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the nvidia-mdev/edpm directory
```
cd architecture/examples/va/nvidia-mdev/edpm
```
Edit the [nodeset/values.yaml](nodeset/values.yaml) and [deployment/values.yaml](deployment/values.yaml) files to suit 
your environment.
```
vi nodeset/values.yaml
vi deployment/values.yaml
```
Generate the dataplane nodeset CR.
```
kustomize build nodeset > dataplane-nodeset.yaml
```
Generate the dataplane deployment CR.
```
kustomize build deployment > dataplane-deployment.yaml
```

## Create CRs
Create the nodeset CR
```
oc apply -f dataplane-nodeset.yaml
```
Wait for dataplane nodeset setup to finish
```
oc wait osdpns openstack-edpm --for condition=SetupReady --timeout=600s
```

Start the deployment
```
oc apply -f dataplane-deployment.yaml
```

Wait for dataplane deployment to finish
```
oc wait osdpns openstack-edpm --for condition=Ready --timeout=60m
```

## Apply necessary Nvidia Configurations
Update or create a blacklist file in /etc/modeprobe
```
cat /etc/modprobe.d/blacklist-nouveau.conf
blacklist nouveau
options nouveau modeset=0
```
Download the relevant Nvidia driver for your hardware and install per Nvidia's
instructions.
Regenerate initramfs
```
dracut --force
grub2-mkconfig -o /boot/grub2/grub.cfg --update-bls-cmdline
```
Create a configmap for the provider.yaml to map CUSTOM_TRAITS to the relevant
resource providers, then create the corresponding service that will apply the
configMap (optional).
```
vi edpm-post-driver/nodeset/values.yaml
kustomize build nodeset > compute-provider-service.yaml
oc apply -f compute-provider-service.yaml
```
Create a deployment to run the service.
```
vi examples/va/nvidia-mdev/edpm-post-driver/deployment/values.yaml
kustomize build deployment > post-driver-deployment.yaml
oc apply -f post-driver-deployment.yaml
```

