## General information

| Revision | Change                |    Date    |
|--------: | :-------------------- |:----------:|
| v0.1     | Initial publication   | 2024-01-11 |

## Purpose
Focusing on testing glance with multi backends over ceph, cinder, 
swift and additional testing for nova.

## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- |--------|
| Openshift master/worker combo-node cluster    | vm    | 3      |
| Compute nodes                                 | vm    | 2      |
| Ceph  nodes                                   | vm    | 3      |

## Services, enabled features and configurations
| Service  | configuration              | Lock-in coverage? |
|----------|----------------------------|-------------------|
| Glance   | multistore                 | Must have         |
| Ceph     | default                    | Must have         |
| Cinder   | RBD storage driver         | Must have         |
| Swift    | default                    | Must have         |
| Nova     | RBD storage driver         | Must have         |

### Support services

| Service  | Reason                     |
|----------|----------------------------|
| Neutron  | needed by scenario testing |
| Keystone | default                    |
| Barbican | default                    |
| Galera   | default                    |
| RabbitMQ | default                    |

### Additional configuration
Always-on, default services and features

| Service  |
| -------- |
| FIPS     |
| TLS-e    |


## Testing tree
Tempest, Rally

| Test framework          | Stage to run | Special configuration |
|------------------------ | ------------ |                       |
| Tempest/image           | tempest stage|                       |
| Tempest/image-import    | tempest stage|                       |
| Tempest/volume          | tempest stage|                       |
| Tempest/object-storage  | tempest stage|                       |
| Tempest/compute         | tempest stage|                       |
| Rally                   | rally stage  | Images 1G to 15G size |
