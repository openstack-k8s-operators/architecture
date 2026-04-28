# Configuring networking and deploy the OpenStack control plane

See [control-plane.md](../control-plane.md) for deployment instructions.

The `service-values.yaml` in this directory is a minimal stub providing
only the fields required by `lib/control-plane` (preserveJobs,
notificationsBus, tls). The full service configuration (Glance, Nova PCI,
telemetry, Ceph extraMounts) is in the top-level
[service-values.yaml](../service-values.yaml) and is applied during the
post-ceph stage rebuild.
