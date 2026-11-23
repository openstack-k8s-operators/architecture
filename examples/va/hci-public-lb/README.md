# HCI with MetalLB-backed public endpoints

The [hci](../hci/README.md) VA with the public endpoints of **all deployed API
services** (barbican, cinder, glance, horizon, keystone, neutron, nova, its cell1 noVNC proxy, and placement)
served by MetalLB `LoadBalancer` services instead of OpenShift Routes.

- All services share the VIP `172.21.0.85` of a dedicated `publicapi` MetalLB pool
  (VLAN 24, `172.21.0.0/24`, `allow-shared-ip`). The `nncp-configuration` and
  `network-configuration` stages add the VLAN interface to the OCP nodes and the pool
  with its L2 advertisement, from the `publicapi` entries of `network-values` like the
  other networks (parent interface, VLAN, MTU, node addresses and pool range). Only
  the OCP nodes are on it, and EDPM nodes use the internal endpoints.
  `networking/nncp/values.yaml` is a copy of the hci one with those entries, as
  kustomize can only read the values from inside its root: keep it in sync with hci. An off-subnet client such as controller-0 needs a router on
  the VLAN and, for the replies, the policy routing described in the
  [dev-docs](https://github.com/openstack-k8s-operators/dev-docs/blob/main/public_endpoint_loadbalancer.md#return-routing-for-clients-outside-the-public-network). CI Framework's
  `scenarios/reproducers/va-hci-public-lb.yml` adds the router VM, and the hook
  `public_endpoints_policy_routing.yml` applies the policy routing after the
  `control-plane` stage and again after `edpm-post-ceph-deployment`, when the
  Services of heat, manila, aodh and watcher exist. Every service has its own
  front port, so they do not collide on the shared VIP.
- Clients reach them by FQDN, `<service>.public.openstack.lab:<port>`, set through
  `override.service.*endpointURL`: keystone `:13000`, nova `:13774`, neutron `:13696`,
  glance `:13292`, cinder `:13776`, barbican `:13311`, placement `:13778`, nova
  noVNC proxy (cell1) `:13080`, horizon on 443.
  Those names must resolve to the VIP for every client, in-cluster pods and EDPM
  nodes included, and are **not** registered by the operators. CI Framework
  registers them in its dnsmasq from the overlay.
- Every public endpoint uses a bring-your-own certificate: one secret
  (`public-byo-cert`) with all the endpoint hostnames as SANs, CA in `byo-ca-bundle`.
  The secrets must exist before the control plane is applied; CI Framework's
  `hooks/playbooks/public_endpoints_byo_cert.yml` creates them.
- heat (`:13004`), heat-cfn (`:13005`), manila (`:13786`), aodh (`:13042`) and watcher
  (`:13322`) are converted too. `hci` enables them in the `edpm-post-ceph` stage, which is why
  the overlay is shared with that stage.
- Not converted: the other services `hci` leaves disabled (designate, ironic, octavia, swift),
  which have no public endpoint here.
- The `nncp-configuration`, `network-configuration`, `control-plane` and
  `edpm-post-ceph-nodeset` stages use roots of this VA, and `edpm-post-ceph-deployment`
  only adds the Loki and policy routing hooks; the other stages are the hci ones. The
  `control-plane` and `edpm-post-ceph-nodeset` stages both apply the control plane
  (the second one with the Ceph settings and the services hci enables then), so they
  share the overlay (`overlay/`): otherwise the second apply would remove the public
  endpoints. The automation file is
  [hci-public-lb.yaml](../../../automation/vars/hci-public-lb.yaml).

Only services whose operator sets the public vhost `ServerName` from
`endpointURL` can be converted; extend the patch in
`overlay/kustomization.yaml` as other operators gain that.

## Enabling and reverting

The feature is selected by the scenario: run CI Framework with
`cifmw_architecture_scenario: hci-public-lb` instead of `hci`. Switching back to
`hci` restores Routes; nothing else changes.

The `control-plane` stage runs two CI Framework hooks beforehand
(`hooks/playbooks/public_endpoints_byo_cert.yml` and `public_endpoints_dns.yml`),
so a CI Framework revision that contains them is required (`Depends-On` while
unmerged). The hooks read the endpoint hostnames from the overlay, located by
`cifmw_public_endpoints_overlay`, which CI Framework's `va-hci-public-lb.yml` scenario
sets to `overlay/kustomization.yaml`. The DNS hook writes to the `hypervisors` inventory group; its records
are removed by running it with `cifmw_public_endpoints_dns_state=absent`.
