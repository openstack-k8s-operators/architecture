    | vm    | 3      |
| Galera DB node, replicating                   | vm    | 3      |
| Hardware security module                      | bm    | 1      |

## Services, enabled features and configurations
| Service                                     | configuration                   | Lock-in coverage?  |
| ------------------------------------------- | ------------------------------- | ------------------ |
| RabbitMQ                                    | default                         | Must have          |
| OVN                                         | default                         | Must have          |
| RabbitMQ                                    | default                         | Must have          |
| Cinder                                      | Ceph/RGW backend                | optional           |
| Manila                                      | Ceph/Ganesha+MDS Backend        | Must have          |
| Glance                                      | NetApp, Fibre channel           | Must have          |
| Keystone                                    | Special appliance [redacted]    | Interchangable     |
| FIPS Mode                                   | default                         | Must have/standard |


## Testing tree

| Test framework   | Stage to run | Special configuration | Test case to report |
| ---------------- | ------------ | --------------------- | :-----------------: |
| Tempest/compute  | stage7       | Use rhel image        | 11223344            |
| Tempest/scenairo | stage7       | Use cirros image      | 22334455            |
| Jordan           | stage7       | None                  | 44556677            |
| Rally/Browbeat   | stage8       | Use CS9 image         | 55667788            |
| Tobiko/Faults    | stage9       | Use cirros image      | 33445566            |

## Stages

All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. Deploy a Director Operator env
7. Execute OSP pre adaption sanity testing
8. Execute OSP pre deployment per DFG specific testing
2. Collect services' DB from OSPdO env
3. Prepare second env for Podified Deploymnt
4. Install dependencies for the OpenStack K8S operators
5. Migrate DB to Podified env's Operators
6. Install the OpenStack K8S operators
7. Configuring networking on the OCP nodes
8. Configure and deploy the control plane
7. Execute OSP post adaption sanity testing
8. Execute OSP post deployment Integrate with DFG specific testing as needed
