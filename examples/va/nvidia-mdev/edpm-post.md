# Download Nvidia drivers to EDPM Nodes and apply follow up deployment

## Assumptions

- Initial [dataplane](edpm-pre.md) deployment has finalized and is successful

## Apply necessary Nvidia configurations to EDPM Nodes
### The following commands should be executed on every EDPM Node expected to provide vGPU MDevs
Log into EDPM Node and update or create a blacklist file in /etc/modeprobe
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

## Create a post deployment to finalize Nvidia configuration
Log out of EDPMs and return to architecture repo on the controller.

```
cd architecture/examples/va/nvidia-mdev/edpm-post-driver
```

### Optional: Create a provider.yaml
Create a configmap for the provider.yaml to map CUSTOM_TRAITS to the relevant
resource providers and their MDevs, then create the corresponding service that
will apply the configMap.

Update the post [nodeset](edpm-post-driver/nodeset/values.yaml) values to how
you wish to map resource provider to traits.

```
vi nodeset/values.yaml
kustomize build nodeset > compute-provider-service.yaml
oc apply -f compute-provider-service.yaml
```

## Reboot EDPM Nodes and optionaly apply provider.yaml
In order finish Nvidia Driver installation the EDPM Nodes will need a final
reboot. This will require a new deployment that will run ```reboot-os``` on the
relevant EDPM Nodes.

Update [deployment](edpm-post-driver/deployment/values.yaml) values to suit
your environment and to include provider.yaml if using.
```
vi deployment/values.yaml
```

Create and apply deployment.
```
kustomize build deployment > post-driver-deployment.yaml
oc apply -f post-driver-deployment.yaml
```
