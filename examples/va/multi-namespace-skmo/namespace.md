# Create the second namespace (openstack2)

## Initialize

Change to the multi-namespace-skmo directory
```
cd architecture/examples/va/multi-namespace-skmo
```

## Apply namespace

Generate the namespace YAML
```
kustomize build ../multi-namespace/namespace > namespace.yaml
```
Apply the YAML
```
oc apply -f namespace.yaml
```
Wait for the namespace to be active
```
oc wait ns openstack2 --for jsonpath='{.status.phase}'=Active --timeout=5m
```
