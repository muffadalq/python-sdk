

Introduction
------------

This is Python SDK version 0.1 for the Datera Fabric Services API.
Download and use of this package implicitly accepts the terms in COPYING

Users of this package are assumed to have familiarity with the Datera API.
Details around the API itself are not necessarily covered through this SDK.


Installation
------------
To install:
   git clone https://github.com/Datera/python-sdk.git 
   cd python-sdk
   python setup.py install


Managed Objects
---------------
Datera provides an application-driven storage management model, whose goal is to closely align storage 
with a corresponding application's requirements.

The main storage objects are defined and differentiated as follows:

	Application Instance (AppInstance)
	-	Corresponds to an application, service, etc.
	-	Contains Zero or more Storage Instances

	Storage Instance
	-	Corresponds to one set of storage requirements for a given AppInstance
	-	ACL Policies, including IQN Initiators
	-	Target IQN
	-	Contains Zero or more Volumes

	Volumes 
	-	Corresponds to a single allocated storage object
	-	Size (default unit is GB)
	-	Replication Factor
	-	Performance Policies (QoS for Bandwidth and IOPS)
	-	Protection Policies (Snapshot scheduling)

Another way of viewing the managed object hierarchy is as follows:

	app_instances:
		- storage_instances:                     (1 or more per app_instance)
			+ acl_policy                     (1 or more host initiators )
			+ iqn                            (target IQN) 
			+ ips                            (target IPs)
			+ volumes:                       (1 or more per storage_instance)
				* name
				* size
				* replication
				* performance_policy     (i.e. QoS)
				* protection_policy      (i.e. Snapshot schedules)
	

Endpoints
---------
HTTP operations on URL endpoints is the only way to interact with the set of managed objects.
URL's have the format:
      http://192.168.42.13:7717/v2/<object_class>/[<instance>]/...
where 7717 is the port used to access the API, and "v2" corresponds to an API version control.

Briefly, the REST API supports 4 operations/methods create (POST), modify (PUT), list (GET), delete (DELETE).
Any input payload is in JSON format;  any return payload is in JSON format.

Login session keys are required within the "header" of any HTTP request.
Sessions keys have a 15 minute lifetime.

For a full reference documentation of the REST API, please review the Datera REST API Guide.

This Python SDK serves as a wrapper around the raw HTTP layer.


Using this SDK
-------------

The Datera module is named "dfs_sdk", and the main entry point is called "DateraApi".
Obtaining an object handle can be done as follows:

		from dfs_sdk import DateraApi
		[...]
                api = DateraApi(username=user, password=password, hostname=ipaddr)



Common Objects, Examples and  Use Cases
---------------------------------------

Please see the "utils" directory for programming examples that cover the following:

Common methods for all objects include "create(), set(), delete(), list()"

Looping through objects can be done via 'list()':

        for ai in api.app_instances.list():
		print "AppInstance: ", ai

Attribute assignment for 'create', and 'set' methods can be provided as follows:

	To create an app_instance with name "FOO":
		api.app_instances.create(name="FOO")

	To set a given app_instance into an offline state:
		ai.set(admin_state="offline")


'dhutil' : Datera Host Utility
------------------------------

The 'dhutil' host-utility is provided along with this SDK.
'dhutil' can be used as both a reference example for using the SDK,
as well as providing some common host-side utility.
For example, a given storage/application lifecycle might looks like this:

1) To create 5 app_instances named 'mongodev', each with a single 10G volume,
and to perform the host-side iscsi scan and login:
  dhutil --basename mongodev --count 5 --size 10

2) To view the multipath mapping to the host:
  dhutil --mpmap

3) To create ext4 filesystems for the 'mongodb' volumes, 
mount them at '/mnt' and change the permissions to 'mongodb:mongodb':
  dhutil --basename mongodev --mkfs --dirprefix /mnt --chown mongodb:mongodb

4) To do a complete teardown (unmount, remove directory, iscsi logout, delete app_instances):
  dhutil --basename mongodev --cleanall

Note that steps 1 and 3 could be combined as follows:
   dhutil --basename mongodev --count 5 --size 10 --mkfs --dirprefix /mnt --chown mongodb:mongodb
Or a corresponding "app_template" could be used, if available:
   dhutil --basename mongodev --count 5 --template mongodb ...

Caveats:  'dhutil' presumes a 'singleton' model, whereby an app_instance
is created with a single storage_instance with a single volume.
Extending the functionality is left as an exercise for the reader 
and is strongly encouraged!


Reporting Problems
------------------
For problems and feedback, please email "support@datera.io"

