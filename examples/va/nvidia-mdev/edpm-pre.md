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
Edit the [nodeset/values.yaml](edpm/nodeset/values.yaml) and [deployment/values.yaml](edpm/deployment/values.yaml) files to suit your environment.
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

## NVIDIA host driver installation

The `install-nvidia` service is an example customization, not an official NVIDIA
installation procedure. Use an approved **vGPU host** driver and confirm the
supported kernel and licensing requirements with NVIDIA.

The default `data.nova.mdev.nvidia_mdev_driver_install_method` is `rpm`, preserving
installation of prebuilt RPMs. A package labeled for the correct RHEL release
can still have an incompatible kernel interface: RPM installation success alone
does not prove that the module can be loaded by the booted kernel.

When carrying forward an older complete `nodeset/values.yaml`, include the new
`nvidia_mdev_driver_*` and `nvidia_mdev_expected_types` defaults from the example,
even if retaining RPM installation, so the added Kustomize replacements resolve.

To compile the interface locally instead, configure the following fields in
`nodeset/values.yaml` (replace the illustrative URL and checksum):

```yaml
data:
  nova:
    mdev:
      nvidia_mdev_driver_install_method: run
      nvidia_mdev_driver_url: https://example.nvidia.com/path/to/vgpu-host-driver.run
      nvidia_mdev_driver_checksum: sha256:<approved-installer-digest>
      nvidia_mdev_driver_accept_license: "true"
      nvidia_mdev_expected_types: '["nvidia-228", "nvidia-229"]'
```

The license acknowledgement, checksum and expected profile values are strings,
because they are copied into a ConfigMap. Leave `nvidia_mdev_expected_types` as
`"[]"` to require at least one NVIDIA mdev profile without naming specific types.
The checksum is optional, but pinning a vendor-approved installer and its digest
is recommended instead of using a mutable `latest` URL.

The `run` method requires explicit acknowledgement of NVIDIA's license. It
downloads the installer over HTTPS, installs `kernel-devel` for `uname -r` plus
the compiler/build prerequisites, and disables precompiled interfaces and DKMS.
The kernel development package must be available from the compute's repositories.
Complete kernel updates and boot the intended kernel **before** this service runs;
the build targets the running kernel, not an arbitrary installed kernel package.

Installation state is recorded in `/var/lib/nvidia-mdev/run-install.json`. A
different installer SHA256, a different running kernel, or missing/different
module versions triggers a rebuild. After later kernel updates, rerun installation
for the newly booted kernel; this example does not arrange automatic DKMS rebuilds.
Failed builds report the tail of `/var/log/nvidia-installer.log`.

Use fresh computes for a new installation method. Switching an existing host
between RPM and `.run` requires explicitly uninstalling the previous driver with
the appropriate package/vendor tools. After uninstalling a `.run` driver, remove
its state marker. The service refuses to mix an installed `NVIDIA-vGPU-rhel` RPM
with `.run`, or an existing `.run` marker with RPM installation. It does not
uninstall drivers from active computes, force incompatible modules, disable
Secure Boot, or bypass module-signature checks. Arrange supported module signing
separately if required by the host's security policy.

Nouveau must be unloaded before `.run` installation. If it is already loaded,
the service rebuilds initramfs with the blacklist and fails with a reboot request.
Reboot, then retry on a host with no active workloads. Do not unload GPU drivers
from an active compute to bypass the check.

## Create CRs and do initial deployment
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
