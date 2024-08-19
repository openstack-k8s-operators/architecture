# MetalLB

Observe CRs which will be generated.
```
kustomize build examples/dt/bgp_dt01/metallb/
```

Apply the metallb kustomization from this directory.
```
oc apply -k examples/dt/bgp_dt01/metallb/
```

Then, check that a speaker is running on the OCP tester node.
```
oc -n metallb-system wait pod -l component=speaker --field-selector=spec.host=worker-3 --for condition=Ready --timeout=300s
```
