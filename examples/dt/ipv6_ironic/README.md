# OpenStack IPv6 Controlplane with Ironic

This is a collection of CR templates that represent a validated Red Hat OpenStack Services on OpenShift deployment that has the following characteristics:

- 1 master/worker combo-node OpenShift cluster
- 1-replica Galera database
- RabbitMQ
- OVN networking
- Network isolation over two NICs

## Stages

All stages must be executed in the order listed below. Everything is required unless

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
