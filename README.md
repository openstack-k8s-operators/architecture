# OpenStack K8S Operators Architectures

This repository contains templates used a a part of the validated architecture
(VA) and deployment topology (DT) effort.

Validated architectures and deployment topologies are represented as kustomize
compatible templates and custom resources.

Deployment topologies are only to be used for testing environments. Validated
architectures are intended to represent production-style deployment
environments

The [automation](automation) directory contains YAML files which
define the stages for each VA/DT including the path to the CR
kustomization and its values as well as a shell command which may
be used to validate that the stage is complete.

## Requirements

The templating provided here requires [kustomize](https://kustomize.io/)
version 5.0.1 or higher ([OpenShift CLI (oc)](https://docs.openshift.com/container-platform/4.14/cli_reference/openshift_cli/getting-started-cli.html#installing-openshift-cli) 4.14 or higher).

## Understanding the repository layout

The architecture layout is made up of three main layers:

1. Base templates in `lib/` directory that are common to all VAs and DTs.
2. VA and DT specific templates in `va/*` and `dt/*` directories that are
   specific to a given VA or DT.
3. User-environment templates and values in `examples/va/*` and `examples/dt/*`
   directories that are specific to a given VA or DT. These user-environment
   templates are expected to be modified to match the users unique environment.

## Validated Architectures

The following VAs are available.

- [Hyperconverged OpenStack and Ceph](examples/va/hci/)
- [Network Functions Virtualization with SRIOV](examples/va/nfv/sriov/)
- [Network Functions Virtualization with OvS DPDK](examples/va/nfv/ovs-dpdk/)
- [Network Functions Virtualization with OvS DPDK & SRIOV](examples/va/nfv/ovs-dpdk-sriov/) [untested]
