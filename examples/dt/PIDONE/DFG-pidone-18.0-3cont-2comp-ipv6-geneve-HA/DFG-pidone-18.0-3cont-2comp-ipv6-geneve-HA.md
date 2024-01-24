RHOS Deployed Topology DFG-pidone-18.0-3cont-2comp-ipv6-geneve-HA
Based on OpenStack K8S operators from the "main" branch of the OpenStack Operator repo on Oct 17th, 2023

General information:
Revision	Change		Publication Date
v0.1	 	Initial		Dec 20 2023

Node topology:
Node role	                                bm/vm	amount
Openshift master/worker combo-node cluster	vm	    3
Compute node					vm	    2

Services, enabled features and configurations:
Service	        configuration	    Lock-in coverage?
Galera      default             Must have
RabbitMQ	default	            Must have
Redis           ?                   Must have
Memcached       default             Must have
TLS             default             Must have
FIPS Mode	default	            Must have/standard

Considerations:
Highly Available deployment
Network protocol - ipv6

Testing tree:
Test framework			Stage to run	Special configuration	Test case to report
Tobiko/Sanity (health checks)	stage7	        Use cirros image        33445566
Tobiko/Resources' creation	stage7	        Use cirros image	33445566
Tobiko/Faults	            	stage9	        Use cirros image	33445566

Stages:
All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

Install dependencies for the OpenStack K8S operators
Install the OpenStack K8S operators
Configuring networking on the OCP nodes
Configure and deploy the control plane
Configure and deploy the initial data plane to prepare for CephHCI installation
Update the control plane and finish deploying the data plane after CephHCI has been installed
Execute non destructive testing
Execute load testing
Destructive testing
