# Configure networking and deploy the OpenStack control planes

## Assumptions

- A storage class called `local-storage` should already exist.
- The `openstack2` namespace has been created (see [namespace.md](namespace.md)).

## Initialize

Change to the multi-namespace-skmo directory
```
cd architecture/examples/va/multi-namespace-skmo
```

Edit the values files to suit your environment. The networking values are
shared with the multi-namespace scenario:
```
vi ../multi-namespace/control-plane/networking/nncp/values.yaml
vi ../multi-namespace/control-plane2/networking/nncp/values.yaml
vi control-plane/service-values.yaml
vi control-plane2/service-values.yaml
vi control-plane2/skmo-values.yaml
```

## Central region (openstack namespace)

### Apply node network configuration

Generate the node network configuration
```
kustomize build ../multi-namespace/control-plane/networking/nncp > nncp.yaml
```
Apply the NNCP CRs
```
oc apply -f nncp.yaml
```

### Apply networking configuration

Generate the networking configuration
```
kustomize build ../multi-namespace/control-plane/networking > networking.yaml
```
Apply the networking CRs
```
oc apply -f networking.yaml
```

### Apply control-plane configuration

Wait for NNCPs to be ready before deploying the control plane
```
oc -n openstack wait nncp -l osp/nncm-config-type=standard \
  --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured \
  --timeout=5m
```
Generate the central control-plane CR
```
kustomize build control-plane > control-plane.yaml
```
Apply the CR
```
oc apply -f control-plane.yaml
```

## Leaf region (openstack2 namespace)

The leaf region can be deployed in parallel with the central region to save time.
The automation hooks handle inter-region configuration after both control planes
are deployed.

### Apply node network configuration

Generate the node network configuration
```
kustomize build ../multi-namespace/control-plane2/networking/nncp > nncp2.yaml
```
Apply the NNCP CRs
```
oc apply -f nncp2.yaml
```
Wait for NNCPs to be ready
```
oc -n openstack2 wait nncp -l osp/nncm-config-type=standard \
  --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured \
  --timeout=5m
```

### Apply networking configuration

Generate the networking configuration
```
kustomize build ../multi-namespace/control-plane2/networking > networking2.yaml
```
Apply the networking CRs
```
oc apply -f networking2.yaml
```

### Prepare leaf region prerequisites

Before deploying the leaf control plane, several resources must be created in
the central region. These steps are handled automatically by the CI automation
hooks; for a manual deployment run the following commands.

Wait for the central Keystone API and openstackclient pod to be ready
```
oc -n openstack wait keystoneapi keystone --for condition=Ready --timeout=60m
oc -n openstack wait pod openstackclient --for condition=Ready --timeout=10m
```

Create the leaf credentials secret in the leaf namespace
```
oc -n openstack2 create secret generic osp-secret \
  --from-env-file=architecture/lib/control-plane/base/osp-secrets.env \
  --dry-run=client -o yaml | oc apply -f -
```

Register the leaf region and its Keystone endpoints in the central Keystone.
Replace `<keystonePublicURL>` and `<keystoneInternalURL>` with the values from
`control-plane2/skmo-values.yaml`:
```
oc -n openstack rsh openstackclient openstack region create regionTwo

oc -n openstack rsh openstackclient \
  openstack endpoint create --region regionTwo identity public <keystonePublicURL>

oc -n openstack rsh openstackclient \
  openstack endpoint create --region regionTwo identity internal <keystoneInternalURL>
```

Create the leaf admin project and user in the central Keystone. Replace
`<leafAdminPassword>` with the value of the `leafAdminPasswordKey` entry from
`osp-secret` in the `openstack2` namespace:
```
oc -n openstack rsh openstackclient openstack project create leafadmin

oc -n openstack rsh openstackclient \
  openstack user create --domain Default --password <leafAdminPassword> leafadmin

oc -n openstack rsh openstackclient \
  openstack role add --project leafadmin --user leafadmin admin
```

Add the central region's root CA certificates to the leaf CA bundle secret so
that the leaf control plane trusts the central region's TLS endpoints:
```
CENTRAL_CA=$(oc -n openstack get secret rootca-public \
  -o jsonpath='{.data.tls\.crt}')
CENTRAL_CA_INT=$(oc -n openstack get secret rootca-internal \
  -o jsonpath='{.data.tls\.crt}')

oc -n openstack2 create secret generic custom-ca-certs \
  --from-literal=skmo-central-rootca.crt="$(echo "$CENTRAL_CA" | base64 -d)" \
  --from-literal=skmo-central-rootca-internal.crt="$(echo "$CENTRAL_CA_INT" | base64 -d)" \
  --dry-run=client -o yaml | oc apply -f -
```

Create a RabbitMQ `TransportURL` in the central namespace for the leaf Barbican
keystone listener and copy the resulting secret to the leaf namespace:
```
oc apply -f - <<EOF
apiVersion: rabbitmq.openstack.org/v1beta1
kind: TransportURL
metadata:
  name: barbican-keystone-listener-regiontwo
  namespace: openstack
spec:
  rabbitmqClusterName: rabbitmq
EOF

oc -n openstack wait transporturl barbican-keystone-listener-regiontwo \
  --for condition=Ready --timeout=120s

oc -n openstack get secret \
  rabbitmq-transport-url-barbican-keystone-listener-regiontwo \
  -o yaml \
  | sed 's/namespace: openstack/namespace: openstack2/' \
  | sed 's/name: rabbitmq-transport-url-.*/name: barbican-keystone-listener-regiontwo-transport/' \
  | oc apply -f -
```

### Apply leaf control-plane configuration

Generate the leaf control-plane CR
```
kustomize build control-plane2 > control-plane2.yaml
```
Apply the CR
```
oc apply -f control-plane2.yaml
```

Wait for both control planes to be available
```
oc -n openstack wait osctlplane controlplane --for condition=Ready --timeout=60m
oc -n openstack2 wait osctlplane controlplane --for condition=Ready --timeout=60m
```

### Post-deploy: update CA bundles and Barbican transport URL

Once both control planes are Ready, add the leaf region's CA certificates to
the central CA bundle so that the central region trusts the leaf:
```
LEAF_CA=$(oc -n openstack2 get secret rootca-public \
  -o jsonpath='{.data.tls\.crt}')
LEAF_CA_INT=$(oc -n openstack2 get secret rootca-internal \
  -o jsonpath='{.data.tls\.crt}')

oc -n openstack get secret custom-ca-certs -o json \
  | jq --arg ca "$LEAF_CA" --arg ca_int "$LEAF_CA_INT" \
    '.data["skmo-leaf-rootca.crt"]=$ca | .data["skmo-leaf-rootca-internal.crt"]=$ca_int' \
  | oc apply -f -
```

Patch the leaf control plane with the cross-region RabbitMQ transport URL for
the Barbican keystone listener:
```
TRANSPORT_URL=$(oc -n openstack get secret \
  rabbitmq-transport-url-barbican-keystone-listener-regiontwo \
  -o jsonpath='{.data.transport_url}' | base64 -d)

oc -n openstack2 patch osctlplane controlplane --type=merge -p "{
  \"spec\": {
    \"barbican\": {
      \"template\": {
        \"barbicanKeystoneListener\": {
          \"customServiceConfig\": \"[DEFAULT]\ntransport_url = ${TRANSPORT_URL}\n[keystone_notifications]\npool_name = barbican-listener-regionTwo\"
        }
      }
    }
  }
}"
```
