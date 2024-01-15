# NOVA.CONF

###############
# On Computes #
###############

[libvirt]
hw_machine_type=x86_64=q35

#
# Virtual RAM to physical RAM allocation ratio. For more information, refer to
# the documentation. (floating point value)
# Minimum value: 0
ram_allocation_ratio=1.0

#
# Amount of memory in MB to reserve for the host so that it is always available
# to host processes.
reserved_host_memory_mb=4096

