import subprocess
import os
import platform
import multiprocessing as mp

# THINGS TO DO:
# 1) Implement logging

DISK_BY_PATH = "/dev/disk/by-path"
#DISK_BY_UUID = "/dev/disk/by-uuid"
SYS_BLOCK = "/sys/block"

class Client(object):
    def __init__(self, args):
        self.basename = args.basename
        self.mkfs = args.mkfs
        self.dirprefix = args.dirprefix
    
    # Eventually replace with subprocess 
    def _run_cmd(self, cmd):
        print cmd
        os.system(cmd)
    
    def uuid_to_dm(self, uuid):
	for f in os.listdir(DISK_BY_UUID):
	    if uuid in f:
	       return os.path.basename(os.readlink(DISK_BY_UUID + "/" + uuid))

    def iqn_to_sd(self, iqn):
	for f in os.listdir(DISK_BY_PATH):
	    if iqn in f:
	       return os.path.basename(os.readlink(DISK_BY_PATH + "/" + f))

    def sd_to_dm(self, sd):
	for f in os.listdir(SYS_BLOCK):
	    t = SYS_BLOCK + "/" + f + "/" + "slaves" + "/" + sd
	    if os.path.islink(t):
	       return f

    def dm_to_mapper(self, dm):
	fname = "{}/{}/dm/name".format(SYS_BLOCK, dm)
	with open(fname, 'r') as f:
	   mapper = f.read().strip()
	f.closed
	return mapper

    def mapper_to_dmpath(self, mapper):
	return "/dev/mapper/" + mapper
    
    def _create_fio_template(self):
	with open('fiotemplate.fio','w') as f:
	   lines = ["[global]","randrepeat=0","ioengine=libaio","iodepth=16","direct=1","numjobs=4","runtime=3600","group_reporting","time_based"]
	   for line in lines:
	      f.write(line + '\n')

    def target_login(self, si, sleep=0):
        if sleep != 0:
            print "Wait %s for storage to come online " % sleep
            time.sleep(sleep)
        #print si['access']
        iqn = si['access']['iqn']
        print "IQN: " + iqn
        for ip in si['access']['ips']:
            print "IP ADDRS = ", ip
            cmd = "iscsiadm -m node -T {} --portal {} --op=new".format(iqn, ip)
            cmd = cmd + " > /dev/null 2>&1"
            print cmd
            subprocess.check_output(cmd, shell=True)
            cmd = "iscsiadm -m node -T {} --portal {} -l".format(iqn, ip)
            print cmd
            subprocess.check_output(cmd, shell=True)
   
    def target_logout_and_node_cleanup(self, s):
        ailist = s.list_ai()
        silist = s.list_si(ailist)
        for si in silist:
            if si['name'].startswith(self.basename):
                if 'iqn' in si['access']:
                    self._run_cmd("iscsiadm -m node -u -T %s" % si['access']['iqn'])
                    self._run_cmd("iscsiadm -m node -T %s --op=delete" % si['access']['iqn'])
                for ip in si['access']['ips']:
                    self._run_cmd("iscsiadm -m discoverydb -t st -p %s:3260 --op=delete" % ip)
           
        self._run_cmd("iscsiadm -m session --rescan")
        self.restart_services()
  
    def unmount(self):
        cmd = "mount |grep %s | awk '{print $3}'" % self.basename
        for l in os.popen(cmd).readlines():
            line = l.rstrip()
            if line == "/":
               print "skipping unmount of /"
               return None
            p = os.path.basename(line)
            print p
            print line
            self._run_cmd("umount %s" % line)
            self._run_cmd("rm -rf %s" % line)
        # cleanup fio files
        self._run_cmd("rm -rf " + self.basename + "*.fio")

    # need to figure out how to handle client_cluster_map
    def mp_mkfs(self, mntmap):
        pool = mp.Pool(processes=10)
        pool.map(mkfs, mntmap)
 
    # need to figure out how to handle client_cluster_map
    def create_fio_files(self, mntmap):
        
	fio = {self.basename + '_randread.fio':{'rw':'randread', 'blocksize':'4k'},
	       self.basename + '_seqread.fio':{'rw':'read', 'blocksize':'1m'},
	       self.basename + '_randwrite.fio':{'rw':'randwrite', 'blocksize':'4k'},
	       self.basename + '_seqwrite.fio':{'rw':'write', 'blocksize':'1m'},
	       self.basename + '_randreadwrite.fio':{'rw':'randrw', 'rwmixread': '70', 'blocksize':'4k'}
	      }

	self._create_fio_template()

	for key,item in fio.items():
	   with open('fiotemplate.fio', 'r') as f:
	      with open(key, 'w') as key:
		 for line in f:
		    key.write(line)
		 for param in item:
		    key.write(param + "=" + item[param] + '\n')
		 if self.mkfs:
		    for index in range(len(mntmap)):
		       #key.write("[" + str(key).split()[2].strip(',') + "]" + '\n')
		       key.write("[fiofile]" + '\n')
		       key.write("directory=/" + mntmap[index][1] + '\n')
		       key.write("size=500M" + '\n')
		 else:
		     for id in mntmap:
			#key.write("[" + str(key).split()[2].strip(',') + "]" + '\n')
			key.write("[fiofile]" + '\n')
			sd = iqn_to_sd(mntmap[id]['iqn'])
			if sd:
			   #dm = uuid_to_dm(args, mntmap[id]['id'])
			   dm = sd_to_dm(sd)
			   key.write("filename=/dev/" + dm + '\n')
			   key.write("size=500M" + '\n')

    def get_initiator_name(self):
        cmd = "grep '^InitiatorName' /etc/iscsi/initiatorname.iscsi"
        cmd = cmd + " | sed -e 's/InitiatorName=//'"
        initiator_name = subprocess.check_output(cmd, shell=True).strip()
        return initiator_name

    def restart_services(self):
        pass

class UbuntuClient(Client):
    def __init__(self, args):
        super(UbuntuClient, self).__init__(args)
        self.os_type = platform.dist()[0]
    def restart_services(self):
        self._run_cmd("service multipath-tools reload")
    
class CentosClient(Client):
    def __init__(self, args):
        super(UbuntuClient, self).__init__(args)
        self.os_type = platform.dist()[0]
    def restart_services(self):
        self._run_cmd("service multipathd reload")

# helper method for client factory
def get_client(args):
    if platform.dist()[0] == "Ubuntu":
        client = UbuntuClient(args)
    elif platform.dist()[0] == "centos":
        client = CentosClient(args)
    else:
        raise ValueError("Client not supported")
   
    return client

#Creating as a helper method because otherwise mp library does not like it if called as in instance method
def mkfs(item):
    if item[2].fstype == "ext4":
	cmd = "mkfs.ext4 -E lazy_itable_init=1 {} ; mkdir -p /{}; mount {} /{}".format(item[0], item[1], item[0], item[1])
    else:
	cmd = "mkfs.xfs {} ; mkdir -p /{}; mount {} /{}".format(item[0], item[1], item[0], item[1])
    print cmd
    os.system(cmd)
    if item[2].chown:
	os.system("chown -R {} /{}".format(item[2].chown, item[1]))
    
