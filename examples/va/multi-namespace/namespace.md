# Create the second namespace (openstack2)

## Apply namespace

Change to the multi-namespace directory
```
cd architecture/examples/va/multi-namespace
```

Generate the namespace YAML
```
kustomize build namespace > namespace.yaml
```
Apply the YAML
```
oc apply -f namespace.yaml
```
