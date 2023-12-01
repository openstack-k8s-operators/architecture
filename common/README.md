# Common files for VAs and DTs

The common directory prevents duplicate CR files.

For example, [stage 1 of the HCI VA](../va/hci/stage1) has
CRs for Namespaces, OperatorGroups, Subscriptions and Deploys.
We expect all VAs and [DTs](../dt/README.md) to need these so they are
stored in the [common stage1](stage1) directory and each file is
symbolically linked from each VA and DT stage1 directory.

The downside of this type of deduplication is that there are a lot of
symbolic links. The upside is that it's easy to delink and replace
any linked file in any DT or VA directory with a new copy of that file
when necessary and that symbolic links are easy to understand.
