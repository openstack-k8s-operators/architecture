# Routing SKMO Keystone traffic through Skupper

## Overview

In a standard Single Keystone Multiple OpenStacks (SKMO) deployment the
workload regions authenticate service-to-service traffic using the **public**
endpoint of the central region's Keystone service.  The current Red Hat
documentation states explicitly:

> *"Even though the internal service-to-service communication traffic of the
> workload regions is encrypted it is more vulnerable to DDOS attacks because
> it is not isolated on a separate internal network making it easier for
> external attackers to intercept these messages."*

By using Red Hat Service Interconnect (Skupper), the *internal* Keystone
endpoint of the central region can be exposed as a private virtual service
inside each workload namespace.  All service-to-service authentication traffic
then travels over the Skupper mTLS application-network tunnel and never leaves
the cluster network.

### What changes

| Concern | Current approach | With Skupper |
|---|---|---|
| Internal service → Keystone path | Public load-balancer route | Skupper mTLS tunnel (in-cluster) |
| Keystone endpoint used by leaf services | `https://<external-route>/v3` | `https://keystone-regionone.<leaf-ns>.svc.cluster.local:5000` |
| Traffic exposure | Public network | Internal cluster network only |
| End-user / catalog endpoint | Public route | Public route (unchanged) |
| EDPM compute node auth_url | Public route | MetalLB LoadBalancer IP on internalapi network |

---

## Prerequisites

* Skupper is installed and Sites are linked between the central and workload
  namespaces.  If you are also routing RabbitMQ traffic through Skupper (for
  `barbican-keystone-listener`), the Site link is already in place.  See the
  [Skupper installation and site-link guide](./skupper-install.md) if you are
  starting from scratch.
* The central region `OpenStackControlPlane` (`controlplane` in namespace
  `openstack`) is deployed and `Ready`.
* Choose a deployment path (see [Deployment paths](#deployment-paths) below).
  **Greenfield workload regions must use Option B** (public bootstrap, then
  Skupper, then patch).  Option A is only viable when `rootca-internal`
  already exists in the workload namespace.
* `cert-manager` is running in the cluster.  The `rootca-internal` `Issuer` in
  the workload namespace is created by the openstack-operator when the
  workload OSCP is deployed; cert-manager can issue the Listener certificate
  only after that Issuer exists.
* If the workload region includes EDPM compute nodes, MetalLB must be
  configured with an address pool for the workload region's internalapi network
  (e.g. `internalapi2`), and a `DNSMasq` LoadBalancer Service must be serving
  DNS to those nodes.  Step 5 relies on both.

---

## Deployment paths

Two paths reach the same **steady-state** configuration (Skupper internal URL
on the leaf OSCP).  They differ in **order of operations** and whether a second
OSCP reconcile is required.

| | Option A | Option B (recommended) |
|---|---|---|
| **When to use** | Workload OSCP (or `rootca-internal`) **already** exists; you add Skupper before changing URLs | **Greenfield** deploy, CI automation, or any case where cert timing is uncertain |
| **Leaf OSCP first apply** | `keystoneInternalURL` = Skupper virtual service | `keystoneInternalURL` = central **public** URL (`skmo-values.yaml` default) |
| **Steps 1–3 timing** | Before first OSCP apply | After leaf OSCP is `Ready` |
| **Extra OSCP reconcile** | No (if cert + Listener are ready first) | Yes — patch internal URL after Skupper (Step 4 / hook 07) |
| **CI hooks** | Not used | `automation/vars/multi-namespace-skmo.yaml` hooks 05–07 |

### Option A and the `rootca-internal` dependency

The Listener TLS `Certificate` (Step 2) is issued by the workload namespace's
`rootca-internal` `Issuer`.  That Issuer is created when the workload
`OpenStackControlPlane` is deployed — it does **not** exist on a greenfield
workload namespace.

Option A therefore has a dependency cycle on first deploy:

1. Option A asks you to complete Steps 1–3 (including a **Ready** Listener
   certificate) **before** applying the workload OSCP.
2. Step 2 cannot reach `Ready` until `rootca-internal` exists.
3. `rootca-internal` is created only when the workload OSCP is applied.

**Option A is not supported for a greenfield workload region** unless you
bootstrap `rootca-internal` independently (not the normal operator flow).
Use **Option B** for first-time SKMO deploys and for CI.

Option A remains valid when the workload OSCP has **already** been deployed
once (for example migrating from the public-internal URL to Skupper): the
Issuer exists, Steps 1–3 can complete, then you set `keystoneInternalURL` to
the Skupper URL before the next OSCP reconcile — or patch as in Step 4.

To disable Skupper Keystone routing entirely, set
`cifmw_skupper_keystone_enabled: false` in the job/scenario.  Hooks 05, 06,
and 07 all honor that flag (the Keystone Listener hook skips when the flag is
false).

---

## Procedure

The step order below matches a **manual Option B** run.  For Option A on an
existing workload namespace, perform Steps 1–3 first, then apply or update
the OSCP as described in Step 4.

### Step 1 — Create a Skupper Connector for Keystone in the central namespace

The Connector tells Skupper to expose the Keystone internal service from the
central namespace onto the application network.

First obtain the TLS Secret name that Keystone uses for its internal endpoint:

```bash
KEYSTONE_TLS_SECRET=$(oc -n openstack get keystoneapi keystone \
  -o jsonpath='{.spec.tls.api.internal.secretName}')
echo "Keystone internal TLS secret: ${KEYSTONE_TLS_SECRET}"
```

Apply the Connector CR:

```yaml
apiVersion: skupper.io/v2alpha1
kind: Connector
metadata:
  name: keystone-internal
  namespace: openstack        # central namespace
spec:
  routingKey: keystone-internal
  host: keystone-internal.openstack.svc.cluster.local
  port: 5000
  type: tcp
  tlsCredentials: <keystone-tls-secret>   # value from the command above
  # verifyHostname is false because the Skupper router connects using the
  # cluster-internal service name which may differ from the cert SANs.
  verifyHostname: false
```

Wait for the Connector to report `Configured: True`:

```bash
oc -n openstack wait connector keystone-internal \
  --for=jsonpath='{.status.conditions[?(@.type=="Configured")].status}'=True \
  --timeout=5m
```

> **Note:** The Connector will not reach `Ready: True` until the matching
> Listener is also created (step 3 below).  `Configured: True` is sufficient
> to proceed.

---

### Step 2 — Create a TLS certificate for the Listener in the workload namespace

The Skupper Listener presents its own TLS certificate to workload-region
services.  Create a `cert-manager` Certificate issued by the workload
namespace's `rootca-internal` Issuer so that workload services trust it.

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: skupper-keystone-regionone
  namespace: openstack2       # workload namespace
spec:
  secretName: cert-skupper-keystone-regionone
  issuerRef:
    name: rootca-internal
    kind: Issuer
  dnsNames:
    - keystone-regionone
    - keystone-regionone.openstack2.svc
    - keystone-regionone.openstack2.svc.cluster.local
  usages:
    - digital signature
    - key encipherment
    - server auth
```

Wait for cert-manager to issue the certificate:

```bash
oc -n openstack2 wait certificate skupper-keystone-regionone \
  --for=condition=Ready --timeout=2m
```

> **Note:** If the workload OSCP has not yet been deployed, `rootca-internal`
> does not exist and cert-manager **cannot** issue this certificate.  On a
> greenfield workload region you must use **Option B**: deploy the workload
> OSCP first (Step 4), wait for `Ready`, then return here for Steps 2–3.
> Option A before first OSCP apply is only possible if `rootca-internal` was
> created by other means.

---

### Step 3 — Create a Skupper Listener in the workload namespace

The Listener creates a virtual `Service` named `keystone-regionone` in the
workload namespace backed by the Skupper tunnel to the central Keystone
Connector.

```yaml
apiVersion: skupper.io/v2alpha1
kind: Listener
metadata:
  name: keystone-internal
  namespace: openstack2       # workload namespace
spec:
  routingKey: keystone-internal
  host: keystone-regionone
  port: 5000
  type: tcp
  tlsCredentials: cert-skupper-keystone-regionone
```

The Skupper controller creates the virtual `Service` once the Listener reaches
`Configured: True`.  That requires the matching Connector to be active and the
TLS credentials secret to exist when the Listener is reconciled.

Wait before proceeding to Step 4:

```bash
oc -n openstack2 wait listener keystone-internal \
  --for=jsonpath='{.status.conditions[?(@.type=="Configured")].status}'=True \
  --timeout=5m
```

---

### Step 4 — Deploy or patch the workload OSCP Keystone internal endpoint

**Option B (deploy OSCP first — required for greenfield, used by CI):** apply
the workload `OpenStackControlPlane` with both `keystoneInternalURL` and
`keystonePublicURL` set to the central public Keystone route (the default in
`control-plane2/skmo-values.yaml`).  Wait for `Ready`, complete Steps 1–3
above, then patch the internal override:

```bash
INTERNAL_URL="https://keystone-regionone.openstack2.svc.cluster.local:5000"

oc -n openstack2 patch osctlplane controlplane --type=merge -p "{
  \"spec\": {
    \"keystone\": {
      \"template\": {
        \"override\": {
          \"service\": {
            \"internal\": {
              \"endpointURL\": \"${INTERNAL_URL}\"
            }
          }
        }
      }
    }
  }
}"
```

The OSCP performs a rolling restart of affected services; allow up to 30 minutes
for it to return to `Ready`.  The CI hook `configure-leaf-keystone-internal.yaml`
performs this patch and wait automatically.

**Option A (Skupper before OSCP URL change — existing workload only):** only
when `rootca-internal` already exists in the workload namespace, complete
Steps 1–3 (including a `Ready` Listener certificate), then set
`keystoneInternalURL` to the Skupper virtual Service endpoint in kustomize
values **before** applying or reconciling the workload `OpenStackControlPlane`.
This avoids the post-Skupper rolling restart that Option B performs via the
patch below.  **Do not use this path on a greenfield workload region** — see
[Option A and the `rootca-internal` dependency](#option-a-and-the-rootca-internal-dependency).

---

### Step 5 — Expose the Skupper Keystone endpoint to EDPM compute nodes

> **Skip this step if the workload region has no EDPM compute nodes.**

The Skupper Listener creates `keystone-regionone` as a **ClusterIP** Service.
ClusterIP addresses are only routable from within the OCP cluster; EDPM
compute nodes running outside the cluster cannot reach them.  Yet `nova-compute`
on those nodes is configured with an `auth_url` of
`https://keystone-regionone.<leaf-ns>.svc.cluster.local:5000`, which it must be
able to resolve and connect to on startup.

Two resources are required:

1. A **LoadBalancer Service** that selects the same Skupper router pod and
   obtains a MetalLB IP on the workload region's internalapi network, making
   port 5000 reachable from EDPM nodes.
2. A **DNSData CR** that registers both the short (`.svc`) and
   fully-qualified (`.svc.cluster.local`) names in the dnsmasq instance
   serving EDPM nodes, resolving to that MetalLB IP.

Create the LoadBalancer Service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: keystone-regionone-lb
  namespace: openstack2       # workload namespace
  annotations:
    # Let MetalLB auto-assign an IP from the workload internalapi pool.
    metallb.universe.tf/address-pool: internalapi2
spec:
  type: LoadBalancer
  selector:
    application: skupper-router
    skupper.io/component: router
  ports:
    - name: keystone-internal
      port: 5000
      protocol: TCP
      targetPort: 1024        # Skupper router application port
```

Wait for MetalLB to assign an external IP:

```bash
oc -n openstack2 get svc keystone-regionone-lb \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

Once the IP is shown (e.g. `172.17.10.87`), create the `DNSData` CR:

```yaml
apiVersion: network.openstack.org/v1beta1
kind: DNSData
metadata:
  name: keystone-skupper
  namespace: openstack2       # workload namespace
spec:
  dnsDataLabelSelectorValue: dnsdata
  hosts:
    - hostnames:
        - keystone-regionone.openstack2.svc
        - keystone-regionone.openstack2.svc.cluster.local
      ip: <metallb-ip>        # IP from the command above
```

The `dnsDataLabelSelectorValue: dnsdata` label causes the `DNSMasq` operator
to pick up this CR automatically and inject the host entries into the running
dnsmasq pods without a restart.

> **Background — why the Skupper Service alone is not enough:**
> Skupper manages `keystone-regionone` with the annotation
> `internal.skupper.io/controlled: "true"`, and its controller enforces the
> ClusterIP type.  Patching that Service directly to LoadBalancer would be
> reverted on the next Skupper reconcile.  The separate `keystone-regionone-lb`
> Service is intentionally unmanaged by Skupper and survives reconciliation.

---

## Verification

After the control plane has reconciled, confirm that the Keystone virtual
service is reachable from within the workload namespace:

```bash
# Start a debug pod in the workload namespace
oc -n openstack2 run skupper-keystone-test --rm -it \
  --image=registry.access.redhat.com/ubi9/ubi-minimal \
  --restart=Never -- \
  curl -ks https://keystone-regionone.openstack2.svc.cluster.local:5000/v3 \
  | python3 -m json.tool
```

You should see the Keystone v3 API response from the central region.

Confirm that the OSCP is using the virtual endpoint:

```bash
oc -n openstack2 get osctlplane controlplane \
  -o jsonpath='{.spec.keystone.template.override.service.internal.endpointURL}'
```

This URL is the same after **both** Option A and Option B; it does not show
which path was used.  To confirm **Option B**, check that hook 07 ran after
the initial deploy (for example
`post_stage_6_run_07_patch_leaf_oscp_internal_ke.log` shows `changed` on the
patch task) and that hooks 05–07 ran only after the leaf OSCP wait in
`ansible-deploy-architecture.log`.

Optionally, confirm that Skupper reports both sides `Ready`:

```bash
oc -n openstack  get connector keystone-internal -o wide
oc -n openstack2 get listener  keystone-internal -o wide
```

If Step 5 was performed, verify DNS resolution and connectivity from an EDPM
compute node:

```bash
# Confirm the LoadBalancer IP was assigned
oc -n openstack2 get svc keystone-regionone-lb

# Confirm the DNSData CR is reconciled
oc -n openstack2 get dnsdata keystone-skupper

# From an EDPM compute node, confirm name resolution
ssh <edpm-node> getent hosts keystone-regionone.openstack2.svc.cluster.local

# Confirm nova-compute is running and registered
oc -n openstack2 exec openstackclient -- openstack compute service list \
  --service nova-compute
```

---

## Comparison with the current documented approach

The existing RHOSO 18 documentation
([Chapter 10, section 10.5](https://docs.redhat.com/en/documentation/red_hat_openstack_services_on_openshift/18.0/html/configuring_security_services/assembly_single-keystone-multiple-openstacks-deployments#proc_create-public-private-endpoints-workload-region_assembly_single-keystone-multiple-openstacks-deployments))
instructs operators to set *both* the public and internal endpoint overrides to
the central region's **public** Keystone URL:

```yaml
# Current documented approach (both point to the public route)
override:
  service:
    internal:
      endpointURL: <central-public-url>   # ← public URL for internal traffic
    public:
      endpointURL: <central-public-url>
```

With the Skupper approach only the internal override changes; the public
override and all Keystone catalog entries are left untouched:

```yaml
# Skupper approach
override:
  service:
    internal:
      endpointURL: https://keystone-regionone.openstack2.svc.cluster.local:5000
    public:
      endpointURL: <central-public-url>   # unchanged
```

The `openstack endpoint create` catalog entries created during initial SKMO
setup do not need to change — they continue to point to the central public URL
for end-user consumption.

---

## Security considerations

* All traffic between the workload region services and the central Keystone
  service travels over Skupper's mTLS tunnel.  No authentication tokens or
  service passwords cross the public network during routine operation.
* The Skupper Listener certificate is issued by the workload namespace's own
  `rootca-internal` CA, which is already trusted by all services in that
  namespace.  No additional CA distribution is required.
* The public Keystone endpoint (used by end users and the Keystone service
  catalog) continues to be secured by the central region's external TLS
  certificate as before.

---

## Next steps — Application Credentials

Once Skupper Keystone routing is in place, the leaf region's service users can
be switched from plain-password authentication to Keystone Application
Credentials, enabling **near zero downtime password rotation**.

See [application-credentials.md](application-credentials.md) for the full
documentation.  AC is enabled by default via
`control-plane2/application-credentials.yaml` included in `kustomization.yaml`.
