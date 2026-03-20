# Single Keystone Multi-region OpenStack (SKMO)

This is a collection of CR templates that represent a validated Red Hat
OpenStack Services on OpenShift deployment with the following
characteristics:

- 3 master/worker combo-node OpenShift cluster
- Two OpenStack control planes deployed in separate namespaces:
  - **Central region** (`openstack` namespace, `regionOne`): hosts the
    Keystone identity service and the Horizon dashboard.  The horizon
    dashboard provides a "single plane of glass" for the central and
    leaf regions.
  - **Leaf region** (`openstack2` namespace, `regionTwo`): all services
    authenticate against the central Keystone identity service 
    (`externalKeystoneAPI: true`).  Neither keystone nor horizon pods
    are present in the leaf region.
- Barbican is enabled in both regions.
  - **Central region** The barbican-keystone-listener listens to the
    central region's rabbitmq service using a unique pool_name:
    (`pool_name = barbican-listener-regionOne`)
  - **Leaf Region** The barbican-keystone-listener is configured to
    listen to the central region's rabbitmq service, rather than the
    leaf region rabbitmq service.  It uses a unique pool_name:
    (`pool_name = barbican-listener-regionTwo`)  
- Mutual CA trust: each region's root CA certificates are added to the
  other region's custom CA bundle
- Network isolation over a single NIC using OVN
- 3-replica Galera database and RabbitMQ per region
- RabbitMQ memory reduced to 2Gi per instance for compact clusters

## Considerations

1. These CRs are validated for the overall functionality of the OSP cloud
   deployed, but they nonetheless require customization for the particular
   environment in which they are utilized. In this sense they are
   _templates_ meant to be consumed and tweaked to fit the specific
   constraints of the hardware available.

2. The CRs are applied against an OpenShift cluster in _stages_. That is,
   there is an ordering in which each grouping of CRs is fed to the
   cluster. It is _not_ a case of simply taking all CRs from all stages
   and applying them all at once.

3. [kustomize](https://kustomize.io/) is used to generate control plane
   CRs dynamically. The `values.yaml` and `service-values.yaml` files in
   each stage directory must be updated to fit your environment. kustomize
   version 5 or newer is required.

4. The `control-plane2/skmo-values.yaml` file contains SKMO-specific
   configuration such as the leaf region name, Keystone endpoint URLs,
   and CA bundle secret names. These **must** be customized before
   deployment.

5. The two control planes are deployed in parallel (stages 5 and 6) to
   reduce overall deployment time. The automation hooks handle the
   inter-region setup (transport URLs, CA trust) automatically.

## Customization

Before deploying, update the following files:

### Central region (`control-plane/`)

- `service-values.yaml`: Set the Barbican keystone listener pool name
  for the central region (`barbican-listener-regionOne` by default).

### Leaf region (`control-plane2/`)

- `service-values.yaml`: Set the Barbican keystone listener pool name
  for the leaf region, Keystone `externalKeystoneAPI` URL, and any
  other leaf-specific service configuration.
- `skmo-values.yaml`: Set the following values for your environment:
  - `leafRegion`: The region name for the leaf control plane (e.g. `regionTwo`)
  - `keystoneInternalURL` / `keystonePublicURL`: The central Keystone
    endpoint URLs reachable from the leaf region
  - `leafAdminUser` / `leafAdminProject`: Admin credentials for the leaf
    region in the central Keystone

## Stages

All stages must be executed in the order listed below. See
`automation/vars/multi-namespace-skmo.yaml` for the automation
configuration used in CI.

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. Configure node network (`nncp`) for the central namespace
3. Configure node network (`nncp`) for the leaf namespace
4. Deploy networking (NAD, MetalLB, etc.) for the central namespace
5. Deploy networking (NAD, MetalLB, etc.) for the leaf namespace
6. **Deploy the central control plane** (`control-plane/`). The central
   Keystone and Barbican services are configured here. The automation
   waits only for the CR to exist, allowing the leaf control plane to
   deploy in parallel.
7. **Deploy the leaf control plane** (`control-plane2/`). Before
   deployment, automation hooks:
   - Register the leaf region and admin user in the central Keystone
   - Create a cross-region RabbitMQ `TransportURL` for the leaf Barbican
     keystone listener
   - Copy the transport URL secret to the leaf namespace
   - Add the central region's root CA to the leaf CA bundle

   After deployment, automation hooks:
   - Add the leaf region's root CA to the central CA bundle
   - Configure the central control plane to use the custom CA bundle
   - Patch the leaf control plane with the cross-region transport URL
     for `barbican-keystone-listener`
