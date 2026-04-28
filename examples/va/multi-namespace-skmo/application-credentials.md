---
# Near Zero Downtime Password Rotation via Application Credentials

## Overview

[Keystone Application Credentials (ACs)][upstream-docs] provide an alternative
authentication mechanism for OpenStack services. Instead of using the service
user's plain password from `osp-secret`, each service authenticates to Keystone
with a time-scoped, project-scoped credential that has its own ID and secret.

This enables **near zero downtime password rotation**: once AC is active, the
service no longer uses `osp-secret` at runtime, so the password can be rotated
without restarting services. The AC controller re-reads the password on-demand
at reconcile time (for creating or rotating ACs), so a rotated password is
picked up automatically on the next reconcile cycle.

[upstream-docs]: https://github.com/openstack-k8s-operators/keystone-operator/blob/main/docs/applicationcredentials.md

## Architecture

Three operator layers are involved:

```
┌──────────────────────────────────────────────────────┐
│  openstack-operator                                  │
│  - Creates/patches KeystoneApplicationCredential CRs │
│  - Reads Status.SecretName from AC CR                │
│  - Sets ApplicationCredentialSecret on service CRs   │
└─────────────────────┬────────────────────────────────┘
                      │ creates AC CR
                      ▼
┌──────────────────────────────────────────────────────┐
│  keystone-operator                                   │
│  - Reconciles KeystoneApplicationCredential CRs      │
│  - Authenticates as service user → creates AC in     │
│    Keystone → stores AC_ID + AC_SECRET in K8s Secret │
│  - Manages rotation; emits ApplicationCredentialRotated event │
└─────────────────────┬────────────────────────────────┘
                      │ AC secret name flows to service CR
                      ▼
┌──────────────────────────────────────────────────────┐
│  service operators (nova, barbican, cinder, …)       │
│  - Watch the AC secret via field indexer             │
│  - Render service config with auth_type =            │
│    v3applicationcredential                           │
└──────────────────────────────────────────────────────┘
```

## SKMO-specific considerations

### External Keystone — connectivity

The leaf control plane (`openstack2`) uses `externalKeystoneAPI: true`. There
is no local Keystone pod; all authentication goes to the central Keystone in
the `openstack` namespace. The AC controller discovers the Keystone endpoint
from the `KeystoneAPI` CR in `openstack2`, which points to the central
Keystone via the Skupper listener (or directly via the public URL when Skupper
Keystone routing is disabled). No additional network configuration is required
beyond what `configure-leaf-keystone-internal.yaml` already sets up.

### Service user names

The leaf region's Keystone users are named with a `regionTwo_` prefix
(`regionTwo_nova`, `regionTwo_barbican`, etc.). The openstack-operator passes
the actual configured username to the AC CR's `userName` field, so the
keystone-operator authenticates as the correct user. The `passwordSelector`
keys in `osp-secret` (`NovaPassword`, `BarbicanPassword`, etc.) are the same
in both namespaces.

### Glance's Swift backend

`service-values.yaml` sets `swift_store_key = {{ .ServicePassword }}` in
glance's `customServiceConfig`. This is how Glance authenticates **to Swift**
(object store) — a separate credential path from Keystone auth. Enabling AC for
Glance replaces how Glance authenticates **to Keystone** (identity); it has no
effect on the Swift backend password.

### EDPM gap — Nova and Ceilometer

**This is the most critical operational consideration.**

EDPM nodes (`compute2`) receive AC credentials as **static Ansible-rendered
config files**. There is no watch loop on the node side. After AC is initially
created, or after any rotation, a deliberate EDPM service redeployment is
required to propagate the new `ac-nova-secret` to `nova.conf` on the compute
nodes.

The grace period (`gracePeriodDays`) is set to 182 days (6 months) to provide
a wide window to schedule EDPM redeployments before the old AC expires. If the
old AC expires before the EDPM nodes are redeployed, `nova-compute` will begin
returning authentication errors.

The `configure-leaf-appcred.yaml` ci-framework playbook handles the initial
EDPM redeployment. For subsequent automatic rotations (triggered by the
keystone-operator when the grace window is reached), an operator must watch for
`ApplicationCredentialRotated` events and trigger EDPM redeployment manually:

```bash
# Monitor rotation events
oc get events -n openstack2 --sort-by=.lastTimestamp | grep ApplicationCredentialRotated
```

Future operator improvements ([PR #1781][edpm-pr]) will add EDPM finalizer
coordination to automate this redeployment.

[edpm-pr]: https://github.com/openstack-k8s-operators/openstack-operator/pull/1781

## Enabling Application Credentials

AC is **enabled by default** — `control-plane2/application-credentials.yaml`
is included in `kustomization.yaml` so it is applied on the very first OSCP
deploy. Services start with `v3applicationcredential` auth from day one.

Because the OSCP is created with AC already active, the OSCP `Ready` condition
implicitly gates on all `KeystoneApplicationCredential` CRs being Ready (the
service operators finish reconciling only once they have an
`ApplicationCredentialSecret` set). EDPM compute nodes therefore receive AC
credentials on their initial deployment (stages 7–10) with no separate
redeployment required.

### Services enabled in the leaf region

| Service    | AC CR name       | Roles                    | Notes                             |
|------------|------------------|--------------------------|-----------------------------------|
| barbican   | `ac-barbican`    | admin, service           |                                   |
| cinder     | `ac-cinder`      | admin, service           |                                   |
| glance     | `ac-glance`      | admin, service           | Swift backend password unchanged  |
| neutron    | `ac-neutron`     | admin, service           |                                   |
| nova       | `ac-nova`        | admin, service, member   | EDPM redeployment required        |
| placement  | `ac-placement`   | admin, service           |                                   |

### Global defaults

| Parameter        | Value    | Notes                                         |
|------------------|----------|-----------------------------------------------|
| `expirationDays` | 730      | 2-year AC lifetime                            |
| `gracePeriodDays`| 182      | Rotation triggered 6 months before expiry     |
| `roles`          | [admin, service] | Per-service overrides where needed  |
| `unrestricted`   | false    |                                               |

## OSCP patch

The patch is defined in
`examples/va/multi-namespace-skmo/control-plane2/application-credentials.yaml`
and applied at CI time by `configure-leaf-appcred.yaml` when
`cifmw_skmo_appcred_enabled: true`.

## Rotation

### Automatic rotation

The keystone-operator triggers rotation when `now >= expiresAt - gracePeriodDays`.
On rotation:

1. A new AC is created in Keystone (with a fresh 5-character random suffix).
2. The existing K8s Secret (`ac-<service>-secret`) is updated in place with the
   new `AC_ID` and `AC_SECRET`.
3. The old AC in Keystone is **not** revoked — it expires naturally.
4. The Secret update triggers the service operator to reconcile and re-render
   config (one pod restart per control-plane service).
5. For EDPM nova/ceilometer: a `ApplicationCredentialRotated` event is emitted;
   operator must trigger `OpenStackDataPlaneDeployment` manually.

### Manual rotation

Patch `status.expiresAt` to a past timestamp to force immediate rotation:

```bash
oc patch -n openstack2 keystoneapplicationcredential ac-nova \
  --type=merge --subresource=status \
  -p '{"status":{"expiresAt":"2001-01-01T00:00:00Z"}}'
```

Alternatively, change a security-critical field (`roles`, `accessRules`,
`unrestricted`) to trigger rotation via security-hash mismatch.

## Observability

```bash
# List all AC CRs in the leaf namespace
oc get appcred -n openstack2

# Inspect a single AC CR
oc describe appcred -n openstack2 ac-nova

# Watch rotation events
oc get events -n openstack2 --sort-by=.lastTimestamp | grep ApplicationCredentialRotated

# Verify EDPM nova.conf uses AC auth (after EDPM redeployment)
ssh compute2-rqf2zhrn-0 grep -A3 'auth_type' /var/lib/openstack/config/nova/nova.conf
```

Example `oc get appcred -n openstack2` output when healthy:

```
NAME            ACID                               SECRETNAME          ROTATIONELIGIBLE       STATUS
ac-barbican     d38dc4310fbf4601bbe9f4234eb24114   ac-barbican-secret  2027-09-01T08:23:58Z   True
ac-cinder       b8c7fb9d3abc4ce18727a56f870c9a18   ac-cinder-secret    2027-09-01T13:04:41Z   True
ac-glance       da20e5b59d0f4227938046c60857cb62   ac-glance-secret    2027-09-01T08:31:42Z   True
ac-neutron      …                                  ac-neutron-secret   …                      True
ac-nova         …                                  ac-nova-secret      …                      True
ac-placement    …                                  ac-placement-secret …                      True
```

## Current limitations

1. **Mutable secrets** — Rotation overwrites the existing Secret in place. If
   propagation fails mid-rotation there is no rollback path.
2. **No Keystone-side revocation** — Old ACs persist until natural expiry.
3. **EDPM static config** — Nova (and Ceilometer if enabled) on EDPM nodes
   require a manual `OpenStackDataPlaneDeployment` after each AC rotation.
   Future work ([PR #1781][edpm-pr]) will automate this via EDPM finalizer
   coordination.
