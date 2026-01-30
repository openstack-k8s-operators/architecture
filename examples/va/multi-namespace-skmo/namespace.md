# Create the second namespace (openstack2)

## Apply namespace

Change to the multi-namespace-skmo directory
```
cd architecture/examples/va/multi-namespace-skmo
```

Generate the namespace YAML
```
kustomize build namespace > namespace.yaml
```
Apply the YAML
```
oc apply -f namespace.yaml
```
