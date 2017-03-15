import os
import sys
from dfs_sdk import DateraApi
from dfs_sdk import DateraApi21
import linecache

API_VER = "2.0"
NUMREPLICAS = 3

class Server(object):
    def __init__(self, args):
        self.basename = args.basename
        self.template = args.template
        self.tenant = args.tenant
        self.numreplicas = args.numreplicas
        self.size = args.size
        self.count = args.count
        self.snappol = args.snappol
        self.volperf = args.volperf
        self.api = self.get_api()

    def _run_cmd(self, cmd):
        print cmd
        os.system(cmd)
    
    def _nocreds(self):
	print
	print "Credentials needed of form 'user:password:IPAddr'"
	print "supplied in DTSCREDS environment variable"
	print
	sys.exit(-1)    

    def _get_creds(self):
	creds = os.getenv("DTSCREDS")
	if not creds or creds == "":
	    self._nocreds()
	return creds

    # Why is this so ugly. There has to be a simpler way
    def _PrintException(self):
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(
	    filename, lineno, line.strip(), exc_obj)

    def _copy_snapshot_policy(self, new_app_instance, volume_map, si, vol):
	for snapid in volume_map[si][vol]['snapshot_policy']:
	    name = volume_map[si][vol]['snapshot_policy'][snapid]['name']
	    ret_count = volume_map[si][vol]['snapshot_policy'][snapid]['retention_count']
	    start_time = volume_map[si][vol]['snapshot_policy'][snapid]['start_time']
	    interval =  volume_map[si][vol]['snapshot_policy'][snapid]['interval']
	    new_app_instance.storage_instances.get(si).volumes.get(vol).snapshot_policies.create(name=name, retention_count=ret_count, start_time=start_time, interval=interval)

    def _get_volume_id_and_path(self, app_instance):
	volume_map = {}
	ai = self.api.app_instances.get(app_instance['name'])
	for si in ai['storage_instances'].keys():
	   volume_map[si] = {}
	   for vol in ai['storage_instances'][si]['volumes'].keys():
	      volume_map[si][vol] = {}
	      volume_map[si][vol]['path'] = ai['storage_instances'][si]['volumes'][vol]['path']
	      if 'acl_policy' in ai['storage_instances'][si]:
		 volume_map[si][vol]['acl_policy'] = ai['storage_instances'][si]['acl_policy']['initiators']
	      if 'performance_policy' in ai['storage_instances'][si]['volumes'][vol]:
		 volume_map[si][vol]['performance_policy'] = ai['storage_instances'][si]['volumes'][vol]['performance_policy']
	      if 'snapshot_policies' in ai['storage_instances'][si]['volumes'][vol]:
		 volume_map[si][vol]['snapshot_policy'] = ai['storage_instances'][si]['volumes'][vol]['snapshot_policies']
	return volume_map

    def show_all(self):
	for at in self.api.app_templates.list():
	    print "App_Template: " + at['name']
	#if not api.system.get()['sw_version'].startswith(API_VER):
	for tenant in self.api.tenants.list():
	   print "Tenant: " + tenant['name']
	   if tenant["name"] != "root" :
		tenant = "/root/" + tenant["name"]
	   else:
		tenant = "/" + tenant["name"]
	   for ai in self.api.app_instances.list(tenant=tenant):
	       print "  App_instance: " + ai['name']
	       print "    admin_state: ", ai['admin_state']
	       for si in ai.storage_instances.list(tenant=tenant):
		   print "    -Storage_instance: " + si['name']
		   for i in si.acl_policy.initiators.list(tenant=tenant):
		       print "        +Initiators: %s  (%s)" % (i['id'], i['name'])
		   if 'iqn' in si['access']:
		       print "        +IQN: " + si['access']['iqn']
		   for ip in si['access']['ips']:
		       print "        +ACCESS IP: " + ip
		   for sn in si['active_storage_nodes']:
		       print "        +ACTIVE_STORAGE_NODES: " + self._sn_to_hostname(sn)
		   for v in si.volumes.list(tenant=tenant):
		       print "        =Volume: {},   Size : {},   UUID : {} ".format(v['name'], v['size'], v['uuid'])

    def get_api(self):
	creds = self._get_creds()
	user, password, ipaddr = creds.split(":")
	try:
	    print "Connecting to : ", ipaddr
	    api = DateraApi(username=user, password=password, hostname=ipaddr)
	    # check sw verstion, and if it is 2.1, import the 2.1 API
	    if not api.system.get()['sw_version'].startswith(API_VER):
	       if self.tenant:
		  api = DateraApi21(username=user, password=password, hostname=ipaddr, tenant="/root/" + self.tenant)
	       else:
		  api = DateraApi21(username=user, password=password, hostname=ipaddr, tenant=None)
	except Exception as e:
	    self._PrintException()
	    sys.exit(1)

	return api

    def si_to_snname(self, si):
	sn_name = 'undef'
	for sn in si['active_storage_nodes']:
	   if not self.api.system.get()['sw_version'].startswith(API_VER):
	      uuid = sn['path'].split("/")[2]
	   else:
	      uuid = sn.split("/")[2]
	   sn = self.api.storage_nodes.get(uuid)
	   sn_name = 'undef'
	   sn_name = sn['name']
	#todo, this only returns the last active server in the list
	return sn_name

    def _sn_to_hostname(self, sn):
	#uuid = sn.split("/")[2]
	if not self.api.system.get()['sw_version'].startswith(API_VER):
	   uuid = sn['path'].split("/")[2]
	else:
	   uuid = sn.split("/")[2]
	sn = self.api.storage_nodes.get(uuid)
	return sn['name']
    
    def chk_template(self):
        # hardcoding to /root for now, since there is an API bug where the list returns 400 bad request if the tenant is anything other than /root
	for at in self.api.app_templates.list(tenant='/root'):
	    if at['name'] == self.template:
		return True
	return False 

    def op_state_poller(self, instance):
	count = 0
	while count < 10:
	   if instance['op_state'] != 'available':
	      time.sleep(1)
	      count = count + 1
	   if count > 9:
	      print instance['name'] + " did not become available in 10s"
	      sys.exit(-1)
	   break   

    def create_initiator(self, id):
        host = os.uname()[1].split('.')[0]
	iis = self.api.initiators.list()
	for i in iis:
	    if i['id'] == id:
		print "Initiator: (%s) %s,  already exists" % (i['name'], id)
		return i
	print "Creating Initiator: (%s) %s" % (host, id)
	return self.api.initiators.create(name=host, id=id)
  
    def delete_initiator(self):
        for initiator in self.api.initiators.list():
            if not initiator["name"].startswith(self.basename):
               continue
            print "Delete initiator " + initiator['name']
            initiator.delete()

    def create_tenant(self):
       if self.tenant:
           # Use tenant if it exists
           subtenant_list = self.api.tenants.list()[0]['subtenants']
           if "/tenants/root/subtenants/" + self.tenant in subtenant_list:
	       print "Using prexisting subtenant " + self.tenant
   	       tenant = "/root/" + self.tenant
           else:
               self.api.tenants.create(name=self.tenant)
               print "Created subtenant: ", self.tenant
               tenant = "/root/" + self.tenant
       else:
           tenant = "/root"
       return tenant

    def delete_tenants(self):
       for tenant in self.api.tenants.list():
           if self.tenant == "root":
               print "Cannot delete root tenant"
           elif tenant['name'] != self.tenant:
               print "Ignoring " + tenant['name'] + " tenant"
           elif self.api.app_instances.list(tenant = "/root/" + self.tenant):
               print tenant['name'] + " tenant is not empty. Ignoring..."
           else:
               tenant.delete(tenant="/root/" + self.tenant)
               print "Deleted " + tenant['name'] + " tenant"

    def list_tenants(self):
        tenant_list = self.api.tenants.list()
        return tenant_list

    def create_ai_from_template(self, ii, tenant):
        ailist = []
        tname = {}
	for n in range(1, self.count + 1):
	   appname = "%s-%d" % (self.basename, n)
           # Add if else clause to pass tname as a string for API_VER < 2.1
	   tname['path'] = "/app_templates/" + self.template
	   ai = self.api.app_instances.create(name=appname, app_template=tname, tenant=tenant)
	   print "Created app_instance: ", ai['name']
	   for si in ai.storage_instances.list(tenant=tenant):
	      si.acl_policy.initiators.add(ii,tenant=tenant)
           ailist.append(ai)
        return ailist

    def create_ai(self, tenant):
        ailist = []
        for i in range(1, self.count + 1):
            ainame = "{}_{}".format(self.basename, i)
            ai = self.api.app_instances.create(name=ainame, tenant=tenant)
            ailist.append(ai)

        return ailist
    
    def delete_ai(self):
        for ai in self.api.app_instances.list():
          if not ai["name"].startswith(self.basename):
              continue
          print "Delete app instance " + ai['name']
          ai.set(admin_state="offline", force=True)
          ai.delete()
   
    def list_ai(self):
        ailist =  self.api.app_instances.list()
        return ailist

    def list_at(self):
        atlist =  self.api.app_templates.list()
        return atlist
   
    def create_si(self, ii, tenant, ailist):
        count = 1
        silist = []
        for ai in ailist:
            siname = "{}_{}".format(self.basename, count)
            si = ai.storage_instances.create(name=siname, tenant=tenant)
            si.acl_policy.initiators.add(ii, tenant=tenant)
            silist.append(si)
            count = count + 1
        return silist
 
    def list_si(self, ailist):
        silist = []
        for ai in ailist:
            for si in ai.storage_instances.list():
               silist.append(si)

        return silist

    def create_vol(self, tenant, silist):
        count = 1
        vlist = []
	if self.numreplicas:
	    numreplicas = self.numreplicas
	else:
	    numreplicas = NUMREPLICAS
        for si in silist:
	#if not self.api.system.get()['sw_version'].startswith(API_VER):
            vname = "{}_vol".format(self.basename)
	    vol = si.volumes.create(name=vname, size=int(self.size),replica_count=int(numreplicas), tenant=tenant)
	    if self.snappol:
	        vol.snapshot_policies.create(name=vname, retention_count=int(self.snappol[0]),interval=self.snappol[1], tenant=tenant)
	    if self.volperf:
	        vol.performance_policy.create(total_iops_max = int(self.volperf[0]),total_bandwidth_max = int(self.volperf[1]), tenant=tenant)
            print "Created Volume: %s (%s)" % (vname, vol['uuid']) 
            vlist.append(vol)
            count = count + 1
	return vlist

    def list_vol(self, ailist, silist):
        vlist = []
        for ai in ailist:
            for si in silist:
                for v in si['volumes']:
                    vlist.append(v)

        return vlist
	 
    # Ignore this method for now. This method needs to be re-written for the new API. That's a project for later
    def clone_an_app_instance(self):
	clone_ai_list = []
	if not self.api.system.get()['sw_version'].startswith(API_VER):
	   print "cloning via dhutil is not yet supported in " + self.api.system.get()['sw_version']
	   sys.exit(-1)
	else:
	    for app_instance in self.api.app_instances.list():
		if app_instance["name"].startswith(self.basename):
		   try:
			# get volume id
			volume_map = self._get_volume_id_and_path(app_instance)
			for si in volume_map.keys():
			   for vol in volume_map[si].keys():
			      # clone app Intance with volume id as the new name
			      new_app_instance = self.api.app_instances.create(name=app_instance['name'] + "_clone", clone_src=volume_map[si][vol]['path'])
			      # copy acl policies
			      if 'acl_policy' in volume_map[si][vol]:
				 acl_policy = self.api.app_instances.get(app_instance['name']).storage_instances.get(si).acl_policy.get()
				 new_app_instance.storage_instances.get(si).acl_policy.set(initiators=[str(volume_map[si][vol]['acl_policy'][0])])
				 time.sleep(2)
				 if new_app_instance.reload()['storage_instances'][si]['op_state'] != "available":
				     print "error copying acl_policies"
				     sys.exit(1)
				 #add initiator groups
			      # copy performance policies
			      if 'performance_policy' in volume_map[si][vol]:
				 performance_policy = self.api.app_instances.get(app_instance['name']).storage_instances.get(si).volumes.get(vol).performance_policy.list()[0]
				 new_app_instance.storage_instances.get(si).volumes.get(vol).performance_policy.create(total_iops_max=performance_policy['total_iops_max'],
				 total_bandwidth_max=performance_policy['total_bandwidth_max'],
				 read_iops_max=performance_policy['read_iops_max'],
				 read_bandwidth_max=performance_policy['read_bandwidth_max'],
				 write_iops_max=performance_policy['write_iops_max'],
				 write_bandwidth_max=performance_policy['write_bandwidth_max'])
				 time.sleep(2)
				 if new_app_instance.reload()['storage_instances'][si]['op_state'] != "available":
				     print "error copying performance_policies"
				     sys.exit(1)
			      # copy snapshot policies
			      if 'snapshot_policy' in volume_map[si][vol]:
				 self._copy_snapshot_policy(new_app_instance, volume_map, si, vol)
				 time.sleep(2)
				 if new_app_instance.reload()['storage_instances'][si]['op_state'] != "available":
				     print "error copying snapshot_policies"
				     sys.exit(1)
			      print "cloned " + app_instance['name'] + " to " + new_app_instance['name']
			      state = self.api.app_instances.get(new_app_instance["name"]).set(admin_state="online")
			      print "setting admin state of " + new_app_instance['name'] + " to " + state["admin_state"]
			      clone_ai_list.append(new_app_instance)
		   except KeyError:
			msg = "appInstance: [{}] doesn't exist".format(app_instance['name'])
			print msg
			continue
	return clone_ai_list

