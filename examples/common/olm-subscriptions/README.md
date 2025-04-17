# OLM subscription that are used for deploying specific versions.

To deploy a specific version rather than the latest from OLM images
containing multiple version definitions, it is necessary to explicitly
set the `startingCSV` parameter.

This kustomization setup accomplishes this for:
- v1.0.3
- v1.0.6: this version no longer includes the AnsibleEE operator
- v1.0.7 and later: these versions only include the OpenStack operator

Refer to the `ci_gen_kustomize_values` role README for configuration
details.
