# Skupper installation and site-link guide

## Overview

[Red Hat Service Interconnect](https://www.redhat.com/en/technologies/cloud-computing/service-interconnect)
(upstream: [Skupper](https://skupper.io/)) provides a layer-7 application
network that connects services running in different Kubernetes namespaces or
clusters over a mutual-TLS tunnel.  In the SKMO scenario it is used to:

* Expose the **central RabbitMQ** service to the leaf (`openstack2`) namespace
  so that `barbican-keystone-listener` can reach it without traversing the
  public network.
* Expose the **central Keystone internal endpoint** to the leaf namespace so
  that service-to-service authentication traffic stays on the cluster network.

This guide covers the two steps that must be completed before any
Skupper Connector or Listener can be created:

1. Install the Skupper operator (cluster-scoped, runs in the `skupper` namespace).
2. Create Skupper Sites in the central (`openstack`) and leaf (`openstack2`)
   namespaces and establish the site link between them.

---

## Automated deployment

In the CI pipeline these steps are handled by two hook playbooks that run as
`pre_stage_run` hooks in Stage 5 of
`automation/vars/multi-namespace-skmo.yaml`:

| Step | Playbook |
|------|----------|
| Install Skupper operator | `skmo/skupper-install.yaml` |
| Create and link Sites | `skmo/skupper-sites.yaml` |

The playbooks are idempotent: they check whether the Skupper CRD / Sites /
Links already exist and skip creation if they do.

Relevant variables (all have defaults; set in your automation vars or as
`extra_vars` to override):

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_skupper_install_source` | `upstream` | `upstream` fetches from skupper.io; `downstream` applies a locally-downloaded Red Hat Service Interconnect YAML |
| `cifmw_skupper_upstream_install_url` | `https://skupper.io/v2/install.yaml` | URL for the upstream install YAML |
| `cifmw_skupper_downstream_install_file` | _(empty)_ | Path to a locally-downloaded downstream install YAML; required when `source=downstream` |
| `cifmw_skupper_central_namespace` | `openstack` | Central region namespace |
| `cifmw_skupper_leaf_namespace` | `openstack2` | Leaf region namespace |
| `cifmw_skupper_central_site_name` | `openstack` | Skupper Site name in the central namespace |
| `cifmw_skupper_leaf_site_name` | `openstack2` | Skupper Site name in the leaf namespace |
| `cifmw_skupper_link_access_type` | `route` | How the central Site exposes its link endpoint: `route` (OpenShift Route), `loadbalancer`, or `nodeport` |

---

## Manual procedure

The steps below reproduce what the automation playbooks do.  Follow them if
you need to set up Skupper outside of the CI pipeline.

### Prerequisites

* An OpenShift cluster with the `openstack` and `openstack2` namespaces already
  created.
* `oc` and `kubectl` configured to reach the cluster.
* Cluster-admin privileges (the Skupper operator is cluster-scoped).

### Step 1 — Install the Skupper operator

**Upstream (community) install:**

```bash
kubectl apply -f https://skupper.io/v2/install.yaml
```

**Downstream (Red Hat Service Interconnect) install:**

Download the install YAML from the Red Hat registry or customer portal, then:

```bash
kubectl apply -f /path/to/rhsi-install.yaml
```

Wait for the controller to be ready:

```bash
kubectl -n skupper rollout status deployment --timeout=5m
```

Verify:

```bash
kubectl -n skupper get deploy
# NAME                         READY   UP-TO-DATE   AVAILABLE
# skupper-controller           1/1     1            1         (upstream)
# skupper-controller-manager   1/1     1            1         (downstream)
```

### Step 2 — Create Sites

Create a Site in the central namespace with link access enabled so it can
issue tokens, and a Site in the leaf namespace that will connect to it:

```bash
# Central site (link access enabled via OpenShift Route)
kubectl apply -f - <<EOF
apiVersion: skupper.io/v2alpha1
kind: Site
metadata:
  name: openstack
  namespace: openstack
spec:
  linkAccess: route
EOF

# Leaf site
kubectl apply -f - <<EOF
apiVersion: skupper.io/v2alpha1
kind: Site
metadata:
  name: openstack2
  namespace: openstack2
spec:
  linkAccess: none
EOF
```

Wait for both Sites to be Ready:

```bash
kubectl -n openstack  wait site/openstack  --for='condition=Ready' --timeout=5m
kubectl -n openstack2 wait site/openstack2 --for='condition=Ready' --timeout=5m
```

### Step 3 — Link the Sites

Create an `AccessGrant` in the central namespace (the grant holds a one-time
token that the leaf will redeem):

```bash
kubectl apply -f - <<EOF
apiVersion: skupper.io/v2alpha1
kind: AccessGrant
metadata:
  name: link-to-openstack2
  namespace: openstack
spec:
  redemptionsAllowed: 1
  expirationWindow: 15m
EOF
```

Wait for the grant to be ready and extract the credentials:

```bash
kubectl -n openstack wait accessgrant/link-to-openstack2 \
  --for='condition=Ready' --timeout=5m

URL=$(kubectl -n openstack get accessgrant/link-to-openstack2 \
  -o jsonpath='{.status.url}')
CA=$(kubectl -n openstack get accessgrant/link-to-openstack2 \
  -o jsonpath='{.status.ca}')
CODE=$(kubectl -n openstack get accessgrant/link-to-openstack2 \
  -o jsonpath='{.status.code}')
```

Redeem the grant from the leaf namespace by creating an `AccessToken`:

```bash
kubectl apply -f - <<EOF
apiVersion: skupper.io/v2alpha1
kind: AccessToken
metadata:
  name: link-to-openstack
  namespace: openstack2
spec:
  url: "$URL"
  ca: "$CA"
  code: "$CODE"
EOF
```

Wait for the Link to be established:

```bash
kubectl -n openstack2 wait link --all --for='condition=Ready' --timeout=5m
```

### Verification

```bash
# Both Sites should show Ready=True
kubectl get site -n openstack
kubectl get site -n openstack2

# A Link should appear in the leaf namespace with Ready=True
kubectl get link -n openstack2
```

Once the Link is Ready you can proceed to create Skupper Connectors and
Listeners for individual services.  See:

* [Routing SKMO Keystone traffic through Skupper](multi-namespace-skmo/skupper-keystone-internal.md)
