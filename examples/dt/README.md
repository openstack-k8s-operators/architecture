# Deployed Topologies

All validated architectures (VAs) are deployed topologies
(DTs), but not all DTs are VAs.

Most DTs represent CI optimizations. We typically design them to test
lots of things together so we can have as few of them as possible. Before
proposing a new DT to test something, consider if an update to an existing DT will
achieve the same result. Other DTs define specific toplogies where a subset of
compoents are deployed explictly without others. Where a DT is not intended
To be extendable such as the compute-starter-kit it should be documeted as such.
