"""
Provides the various v2 endpoints and entities
"""
__copyright__ = "Copyright 2015, Datera, Inc."


from .base import Endpoint as _Endpoint
from .base import ContainerEndpoint as _ContainerEndpoint
from .base import SingletonEndpoint as _SingletonEndpoint
from .base import SimpleReferenceEndpoint as _SimpleReferenceEndpoint
from .base import ListEndpoint as _ListEndpoint
from .base import StringEndpoint as _StringEndpoint
from .base import MetricCollectionEndpoint as _MetricCollectionEndpoint
from .base import MetricEndpoint as _MetricEndpoint
from .base import Entity as _Entity


##################################################################
#
#  Entity classes


class AccessNetworkIpPool(_Entity):

    def __init__(self, *args):
        super(AccessNetworkIpPool, self).__init__(*args)


class AccessNetworkIpPools(_Entity):

    def __init__(self, *args):
        super(AccessNetworkIpPools, self).__init__(*args)
        self._set_subendpoint(NetworkPathsEp)


class NetworkPath(_Entity):

    def __init__(self, *args):
        super(NetworkPath, self).__init__(*args)


class AppInstance(_Entity):
    """
        /app_instances/:name
        could contain storage_instances ( AppInstanceStorageInstanceRefEp  )
        get/set/delete
    """

    def __init__(self, *args):
        super(AppInstance, self).__init__(*args)
        self._set_subendpoint(StorageInstancesEp)
        self._set_subendpoint(SnapshotPoliciesEp)
        self._set_subendpoint(SnapshotsEp)

class AppTemplate(_Entity):
    """
        /app_templates/:name
        contains storage_templates ( StorageTemplatesEp  )
        get/set/delete
    """

    def __init__(self, *args):
        super(AppTemplate, self).__init__(*args)
        self._set_subendpoint(StorageTemplatesEp)
        self._set_subendpoint(SnapshotPoliciesEp)

class DnsServer(_Entity):
    """ Dns entity """

    def __init__(self, *args):
        super(DnsServer, self).__init__(*args)


class DnsSearchDomain(_Entity):
    """ Dns search_domains entity """

    def __init__(self, *args):
        super(DnsSearchDomain, self).__init__(*args)


class NtpServer(_Entity):
    """ Ntp entity """

    def __init__(self, *args):
        super(NtpServer, self).__init__(*args)


class Initiator(_Entity):

    def __init__(self, *args):
        super(Initiator, self).__init__(*args)


class InitiatorGroup(_Entity):

    def __init__(self, *args):
        super(InitiatorGroup, self).__init__(*args)
        self._set_subendpoint(InitiatorGroupMembersRefEp)


class Users(_Entity):
    """ get,create,list,modify methods for user    """

    def __init__(self, *args):
        super(Users, self).__init__(*args)
        self._set_subendpoint(UsersRolesRefEp)


class Roles(_Entity):
    """ get,list,modify methods for roles   """

    def __init__(self, *args):
        super(Roles, self).__init__(*args)


class StorageNode(_Entity):
    """ storage_node entity """

    def __init__(self, *args):
        super(StorageNode, self).__init__(*args)
        self._set_subendpoint(NvmFlashDevicesEp)
        self._set_subendpoint(HddsEp)
        self._set_subendpoint(NicsEp)
        self._set_subendpoint(SubsystemEp)
        self._set_subendpoint(BootDrivesEp)
        self._set_subendpoint(StorageNodeMetricsEp)


class EventLog(_Entity):
    """ event_logs entity """

    def __init__(self, *args):
        super(EventLog, self).__init__(*args)


class AuditLog(_Entity):
    """ audit_logs entity """

    def __init__(self, *args):
        super(AuditLog, self).__init__(*args)


class FaultLog(_Entity):
    """ fault_logs entity """

    def __init__(self, *args):
        super(FaultLog, self).__init__(*args)


class HttpProxy(_Entity):
    """ /system/http_proxy """

    def __init__(self, *args):
        super(HttpProxy, self).__init__(*args)


class Snapshot(_Entity):
    """
        /app_instances/:name/storage_instances/:name/volumes/:name/snapshots
    """

    def __init__(self, *args):
        super(Snapshot, self).__init__(*args)


class SnapshotPolicy(_Entity):
    """
        /storage_templates/:name/volume_templates/:name/snapshot_policies/:name
    """

    def __init__(self, *args):
        super(SnapshotPolicy, self).__init__(*args)

class StorageInstance(_Entity):
    """
        /app_instances/:name/storage_instances/:name
    """

    def __init__(self, *args):
        super(StorageInstance, self).__init__(*args)
        self._set_subendpoint(VolumesEp)
        self._set_subendpoint(AclPolicyEp)
        self._set_subendpoint(AuthEp)
        self._set_subendpoint(AccessEP)
        # To be removed once we have acl_policy back
        self._set_subendpoint(AccessControlEp)
        self._set_subendpoint(StorageInstanceMetricsEp)


class StorageTemplate(_Entity):
    """
        /app_template/:name/storage_templates/:name - get / set / unlink()
        /storage_templates/:name - get / set / delete
    """

    def __init__(self, *args):
        super(StorageTemplate, self).__init__(*args)
        self._set_subendpoint(VolumeTemplatesEp)
        self._set_subendpoint(AuthEp)


class Volume(_Entity):
    """
        /app_instances/:name/storage_instances/:name/volumes/:name
    """

    def __init__(self, *args):
        super(Volume, self).__init__(*args)
        self._set_subendpoint(SnapshotPoliciesEp)
        self._set_subendpoint(PerformancePolicyEp)
        self._set_subendpoint(SnapshotsEp)
        self._set_subendpoint(VolumeMetricsEp)


class VolumeTemplate(_Entity):
    """
        /app_template/:name/storage_templates/:name/volume_templates/:name
          - get / set /delete
        /storage_templates/:name/volume_templates/:name - get / set /delete
    """

    def __init__(self, *args):
        super(VolumeTemplate, self).__init__(*args)
        self._set_subendpoint(SnapshotPoliciesEp)
        self._set_subendpoint(PerformancePolicyEp)


class Hdd(_Entity):
    pass


class Api(_Entity):
    pass


class AccessVipInterface(_Entity):
    pass


class MgmtVipInterface(_Entity):
    pass


class InternalNetworkInterface(_Entity):
    pass


class AccessNetworks(_Entity):

    def __init__(self, *args):
        super(AccessNetworks, self).__init__(*args)


class AccessVip(_Entity):

    def __init__(self, *args):
        super(AccessVip, self).__init__(*args)
        self._set_subendpoint(AccessVipInterfacesEp)


class MgmtVip(_Entity):

    def __init__(self, *args):
        super(MgmtVip, self).__init__(*args)
        self._set_subendpoint(MgmtVipInterfacesEp)


class InternalNetwork(_Entity):

    def __init__(self, *args):
        super(InternalNetwork, self).__init__(*args)
        self._set_subendpoint(InternalNetworkInterfacesEp)


class Network(_Entity):

    def __init__(self, *args):
        super(Network, self).__init__(*args)
        self._set_subendpoint(AccessNetworksEp)
        self._set_subendpoint(AccessVipEp)
        self._set_subendpoint(MgmtVipEp)
        self._set_subendpoint(InternalNetworkEp)


class System(_Entity):

    def __init__(self, *args):
        super(System, self).__init__(*args)
        self._set_subendpoint(DnsEp)
        self._set_subendpoint(NetworkEp)
        self._set_subendpoint(NtpServersEp)
        self._set_subendpoint(HttpProxyEp)
        self._set_subendpoint(SystemMetricsEp)


class AclPolicy(_Entity):

    def __init__(self, *args):
        super(AclPolicy, self).__init__(*args)
        self._set_subendpoint(AclPolicyInitiatorsRefEp)
        self._set_subendpoint(AclPolicyEpInitiatorGroupsRefEp)


class AccessControl(_Entity):

    def __init__(self, *args):
        super(AccessControl, self).__init__(*args)
        self._set_subendpoint(AclPolicyInitiatorsRefEp)
        self._set_subendpoint(AclPolicyEpInitiatorGroupsRefEp)


class Access(_Entity):

    def __init__(self, *args):
        super(Access, self).__init__(*args)


class Dns(_Entity):
    pass


class Nic(_Entity):
    pass


class NvmFlashDevice(_Entity):
    pass


class BootDrive(_Entity):
    pass


class Subsystem(_Entity):
    pass


class PerformancePolicy(_Entity):
    pass


class Auth(_Entity):
    pass


class Upgrade(_Entity):
    pass


class UpgradeAvailable(_Entity):
    pass


###############################################################################
#
#  SingletonEndpoint classes


class SystemEp(_SingletonEndpoint):
    _name = "system"
    _entity_cls = System

    def __init__(self, *args):
        super(SystemEp, self).__init__(*args)
        self._set_subendpoint(DnsEp)
        self._set_subendpoint(NetworkEp)
        self._set_subendpoint(NtpServersEp)
        self._set_subendpoint(HttpProxyEp)


class ApiEp(_SingletonEndpoint):
    _name = "api"
    _entity_cls = Api


class AclPolicyEp(_SingletonEndpoint):
    _name = "acl_policy"
    _entity_cls = AclPolicy

    def __init__(self, *args):
        super(AclPolicyEp, self).__init__(*args)
        self._set_subendpoint(AclPolicyInitiatorsRefEp)
        self._set_subendpoint(AclPolicyEpInitiatorGroupsRefEp)


class AccessControlEp(_SingletonEndpoint):
    _name = "access_control"
    _entity_cls = AccessControl

    def __init__(self, *args):
        super(AccessControlEp, self).__init__(*args)
        self._set_subendpoint(AclPolicyInitiatorsRefEp)
        self._set_subendpoint(AclPolicyEpInitiatorGroupsRefEp)


class AccessEP(_SingletonEndpoint):
    _name = "access"
    _entity_cls = Access

    def __init__(self, *args):
        super(AccessEP, self).__init__(*args)


class AuthEp(_SingletonEndpoint):
    _name = "auth"
    _entity_cls = Auth

    def __init__(self, *args):
        super(AuthEp, self).__init__(*args)


class DnsEp(_SingletonEndpoint):
    _name = "dns"
    _entity_cls = Dns

    def __init__(self, *args):
        super(DnsEp, self).__init__(*args)
        self._set_subendpoint(DnsServersEp)
        self._set_subendpoint(DnsSearchDomainsEp)

class AccessNetworksEp(_SingletonEndpoint):
    _name = "access_networks"
    _entity_cls = AccessNetworks

    def __init__(self, *args):
        super(AccessNetworksEp, self).__init__(*args)


class AccessVipEp(_SingletonEndpoint):
    _name = "access_vip"
    _entity_cls = AccessVip

    def __init__(self, *args):
        super(AccessVipEp, self).__init__(*args)
        self._set_subendpoint(AccessVipInterfacesEp)


class NetworkPathsEp(_ContainerEndpoint):
    _name = "network_paths"
    _entity_cls = NetworkPath

    def __init__(self, *args):
        super(NetworkPathsEp, self).__init__(*args)


class MgmtVipEp(_SingletonEndpoint):
    _name = "mgmt_vip"
    _entity_cls = MgmtVip

    def __init__(self, *args):
        super(MgmtVipEp, self).__init__(*args)
        self._set_subendpoint(MgmtVipInterfacesEp)


class InternalNetworkEp(_SingletonEndpoint):
    _name = "internal_network"
    _entity_cls = InternalNetwork

    def __init__(self, *args):
        super(InternalNetworkEp, self).__init__(*args)
        self._set_subendpoint(InternalNetworkInterfacesEp)


class NetworkEp(_SingletonEndpoint):
    _name = "network"
    _entity_cls = Network

    def __init__(self, *args):
        super(NetworkEp, self).__init__(*args)
        self._set_subendpoint(AccessNetworksEp)
        self._set_subendpoint(AccessVipEp)
        self._set_subendpoint(MgmtVipEp)
        self._set_subendpoint(InternalNetworkEp)


class PerformancePolicyEp(_SingletonEndpoint):
    _name = "performance_policy"
    _entity_cls = PerformancePolicy

    def __init__(self, *args):
        super(PerformancePolicyEp, self).__init__(*args)


class HttpProxyEp(_SingletonEndpoint):
    _name = "http_proxy"
    _entity_cls = HttpProxy

    def __init__(self, *args):
        super(HttpProxyEp, self).__init__(*args)


# To be depreceted , once access_network_ip_pools functionality is in place
class AccessNetworkIpPoolEp(_SingletonEndpoint):
    """
        /access_network_ip_pool/:id
        get() / list() / create() / delete()
    """
    _name = "access_network_ip_pool"
    _entity_cls = AccessNetworkIpPool

    def __init__(self, *args):
        super(AccessNetworkIpPoolEp, self).__init__(*args)
        self._set_subendpoint(NetworkPathsEp)


class AccessNetworkIpPoolsEp(_ContainerEndpoint):
    """
        /access_network_ip_pools/:id
        get() / list() / create() /modify() / delete()
    """
    _name = "access_network_ip_pools"
    _entity_cls = AccessNetworkIpPools

    def __init__(self, *args):
        super(AccessNetworkIpPoolsEp, self).__init__(*args)
        self._set_subendpoint(NetworkPathsEp)


###############################################################################
#
#  ContainerEndpoint classes


class UpgradeEp(_SingletonEndpoint):
    _name = "upgrade"
    _entity_cls = Upgrade

    def __init__(self, *args):
        super(UpgradeEp, self).__init__(*args)
        self._set_subendpoint(UpgradeAvailableEp)


class UpgradeAvailableEp(_ContainerEndpoint):
    _name = "available"
    _entity_cls = UpgradeAvailable


class AppInstancesEp(_ContainerEndpoint):
    """
        /app_instance
        get() / list() / create() / delete()
    """
    _name = "app_instances"
    _entity_cls = AppInstance

    def __init__(self, *args):
        super(AppInstancesEp, self).__init__(*args)


class AppTemplatesEp(_ContainerEndpoint):
    """
        /app_templates
        get() / list() / create() / delete()
    """
    _name = "app_templates"
    _entity_cls = AppTemplate

    def __init__(self, *args):
        super(AppTemplatesEp, self).__init__(*args)


class InitiatorsEp(_ContainerEndpoint):
    _name = "initiators"
    _entity_cls = Initiator

    def __init__(self, *args):
        super(InitiatorsEp, self).__init__(*args)


class InitiatorGroupsEp(_ContainerEndpoint):
    _name = "initiator_groups"
    _entity_cls = InitiatorGroup

    def __init__(self, *args):
        super(InitiatorGroupsEp, self).__init__(*args)


class StorageNodesEp(_ContainerEndpoint):
    _name = "storage_nodes"
    _entity_cls = StorageNode

    def __init__(self, *args):
        super(StorageNodesEp, self).__init__(*args)


class StorageTemplatesEp(_ContainerEndpoint):
    """
        /storage_templates/:name
        get() / list() / create() / delete()
    """
    _name = "storage_templates"
    _entity_cls = StorageTemplate

    def __init__(self, *args):
        super(StorageTemplatesEp, self).__init__(*args)


class EventLogsEp(_ContainerEndpoint):
    """
        /event_logs/:id
        get() / list()
    """
    _name = "event_logs"
    _entity_cls = EventLog

    def __init__(self, *args):
        super(EventLogsEp, self).__init__(*args)


class AuditLogsEp(_ContainerEndpoint):
    """
        /audit_logs/:id
        get() / list()
    """
    _name = "audit_logs"
    _entity_cls = AuditLog

    def __init__(self, *args):
        super(AuditLogsEp, self).__init__(*args)


class FaultLogsEp(_ContainerEndpoint):
    """
        /fault_logs/:id
        get() / list()
    """
    _name = "fault_logs"
    _entity_cls = FaultLog

    def __init__(self, *args):
        super(FaultLogsEp, self).__init__(*args)


class UsersEp(_ContainerEndpoint):
    """      """
    _name = "users"
    _entity_cls = Users

    def __init__(self, *args):
        super(UsersEp, self).__init__(*args)


class RolesEp(_ContainerEndpoint):
    """      """
    _name = "roles"
    _entity_cls = Roles

    def __init__(self, *args):
        super(RolesEp, self).__init__(*args)


class UsersRolesRefEp(_SimpleReferenceEndpoint):
    """      """
    _name = "roles"
    _entity_cls = Roles
    _parent_entity_cls = Users

    def __init__(self, *args):
        super(UsersRolesRefEp, self).__init__(*args)


class AccessVipInterfacesEp(_ContainerEndpoint):
    _name = "network_paths"
    _entity_cls = AccessVipInterface


class MgmtVipInterfacesEp(_ContainerEndpoint):
    _name = "network_paths"
    _entity_cls = MgmtVipInterface


class InternalNetworkInterfacesEp(_ContainerEndpoint):
    _name = "network_paths"
    _entity_cls = InternalNetworkInterface


class NicsEp(_ContainerEndpoint):
    _name = "nics"
    _entity_cls = Nic

    def __init__(self, *args):
        super(NicsEp, self).__init__(*args)


class NvmFlashDevicesEp(_ContainerEndpoint):
    _name = "nvm_flash_devices"
    _entity_cls = NvmFlashDevice

    def __init__(self, *args):
        super(NvmFlashDevicesEp, self).__init__(*args)


class HddsEp(_ContainerEndpoint):
    _name = "hdds"
    _entity_cls = Hdd

    def __init__(self, *args):
        super(HddsEp, self).__init__(*args)


class BootDrivesEp(_ContainerEndpoint):
    _name = "boot_drives"
    _entity_cls = BootDrive

    def __init__(self, *args):
        super(BootDrivesEp, self).__init__(*args)


class SubsystemEp(_ContainerEndpoint):
    _name = "subsystem_health"
    _entity_cls = Subsystem

    def __init__(self, *args):
        super(SubsystemEp, self).__init__(*args)


class DnsServersEp(_ListEndpoint):
    # parent_path = "/dns", self._path = "/dns/servers"
    _name = "servers"
    _entity_cls = DnsServer

    def __init__(self, *args):
        super(DnsServersEp, self).__init__(*args)


class NtpServersEp(_ListEndpoint):
    # parent_path = "/system", self._path = "/system/ntp_servers"
    _name = "ntp_servers"
    _entity_cls = NtpServer

    def __init__(self, *args):
        super(NtpServersEp, self).__init__(*args)


class DnsSearchDomainsEp(_ListEndpoint):
    _name = "search_domains"
    _entity_cls = DnsSearchDomain

    def __init__(self, *args):
        super(DnsSearchDomainsEp, self).__init__(*args)


class SnapshotPoliciesEp(_ContainerEndpoint):
    """
        /storage_templates/:name/volume_templates/:name/snapshot_policies
        get() / list() / create() / delete()
    """
    _name = "snapshot_policies"
    _entity_cls = SnapshotPolicy

    def __init__(self, *args):
        super(SnapshotPoliciesEp, self).__init__(*args)


class SnapshotsEp(_ContainerEndpoint):
    _name = "snapshots"
    _entity_cls = Snapshot


class StorageInstancesEp(_ContainerEndpoint):
    """
        /app_instances/:name/storage_instances
        get() / list() / create() / delete()
    """
    _name = "storage_instances"
    _entity_cls = StorageInstance

    def __init__(self, *args):
        super(StorageInstancesEp, self).__init__(*args)


class VolumesEp(_ContainerEndpoint):
    """
        /app_instances/:name/storage_instances/:name/volumes
        get() / list() / create() / delete()
    """
    _name = "volumes"
    _entity_cls = Volume

    def __init__(self, *args):
        super(VolumesEp, self).__init__(*args)


class VolumeTemplatesEp(_ContainerEndpoint):
    """
        /storage_templates/:name/volume_templates
        get() / list() / create() / delete()
    """
    _name = "volume_templates"
    _entity_cls = VolumeTemplate

    def __init__(self, *args):
        super(VolumeTemplatesEp, self).__init__(*args)


###############################################################################
#
#  SimpleReferenceEndpoint classes


class AclPolicyInitiatorsRefEp(_SimpleReferenceEndpoint):
    _name = "initiators"
    _entity_cls = Initiator
    _parent_entity_cls = AclPolicy

    def __init__(self, *args):
        super(AclPolicyInitiatorsRefEp, self).__init__(*args)


class InitiatorGroupMembersRefEp(_SimpleReferenceEndpoint):
    _name = "members"
    _entity_cls = Initiator
    _parent_entity_cls = InitiatorGroup

    def __init__(self, *args):
        super(InitiatorGroupMembersRefEp, self).__init__(*args)


class AclPolicyEpInitiatorGroupsRefEp(_SimpleReferenceEndpoint):
    _name = "initiator_groups"
    _parent_entity_cls = AclPolicy
    _entity_cls = InitiatorGroup

    def __init__(self, *args):
        super(AclPolicyEpInitiatorGroupsRefEp, self).__init__(*args)


###############################################################################
#
#  MetricCollectionEndpoint classes

class StorageInstanceMetricsEp(_MetricCollectionEndpoint):
    _name = "metrics"
    _entity_cls = _Entity

    def __init__(self, *args):
        super(StorageInstanceMetricsEp, self).__init__(*args)
        self._set_subendpoint(ReadsEp)
        self._set_subendpoint(WritesEp)
        self._set_subendpoint(BytesReadEp)
        self._set_subendpoint(BytessWrittenEp)
        self._set_subendpoint(IopsReadEp)
        self._set_subendpoint(IopsWriteEp)
        self._set_subendpoint(ThptReadEp)
        self._set_subendpoint(ThptWriteEp)
        self._set_subendpoint(LatAvgReadEp)
        self._set_subendpoint(LatAvgWriteEp)


class SystemMetricsEp(_MetricCollectionEndpoint):
    _name = "metrics"
    _entity_cls = _Entity

    def __init__(self, *args):
        super(SystemMetricsEp, self).__init__(*args)
        self._set_subendpoint(ReadsEp)
        self._set_subendpoint(WritesEp)
        self._set_subendpoint(BytesReadEp)
        self._set_subendpoint(BytessWrittenEp)
        self._set_subendpoint(IopsReadEp)
        self._set_subendpoint(IopsWriteEp)
        self._set_subendpoint(ThptReadEp)
        self._set_subendpoint(ThptWriteEp)
        self._set_subendpoint(LatAvgReadEp)
        self._set_subendpoint(LatAvgWriteEp)


class StorageNodeMetricsEp(_MetricCollectionEndpoint):
    _name = "metrics"
    _entity_cls = _Entity

    def __init__(self, *args):
        super(StorageNodeMetricsEp, self).__init__(*args)
        self._set_subendpoint(ReadsEp)
        self._set_subendpoint(WritesEp)
        self._set_subendpoint(BytesReadEp)
        self._set_subendpoint(BytessWrittenEp)
        self._set_subendpoint(IopsReadEp)
        self._set_subendpoint(IopsWriteEp)
        self._set_subendpoint(ThptReadEp)
        self._set_subendpoint(ThptWriteEp)
        self._set_subendpoint(LatAvgReadEp)
        self._set_subendpoint(LatAvgWriteEp)
        self._set_subendpoint(CpuUsageEp)


class VolumeMetricsEp(_MetricCollectionEndpoint):
    _name = "metrics"
    _entity_cls = _Entity

    def __init__(self, *args):
        super(VolumeMetricsEp, self).__init__(*args)
        self._set_subendpoint(ReadsEp)
        self._set_subendpoint(WritesEp)
        self._set_subendpoint(BytesReadEp)
        self._set_subendpoint(BytessWrittenEp)
        self._set_subendpoint(IopsReadEp)
        self._set_subendpoint(IopsWriteEp)
        self._set_subendpoint(ThptReadEp)
        self._set_subendpoint(ThptWriteEp)
        self._set_subendpoint(LatAvgReadEp)
        self._set_subendpoint(LatAvgWriteEp)
        self._set_subendpoint(Lat50ReadEp)
        self._set_subendpoint(Lat90ReadEp)
        self._set_subendpoint(Lat100ReadEp)
        self._set_subendpoint(Lat50WriteEp)
        self._set_subendpoint(Lat90WriteEp)
        self._set_subendpoint(Lat100WriteEp)


###############################################################################
#
#  MetricEndpoint classes

class ReadsEp(_MetricEndpoint):
    _name = 'reads'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(ReadsEp, self).__init__(*args)


class WritesEp(_MetricEndpoint):
    _name = 'writes'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(WritesEp, self).__init__(*args)


class BytesReadEp(_MetricEndpoint):
    _name = 'bytes_read'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(BytesReadEp, self).__init__(*args)


class BytessWrittenEp(_MetricEndpoint):
    _name = 'bytes_written'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(BytessWrittenEp, self).__init__(*args)


class IopsReadEp(_MetricEndpoint):
    _name = 'iops_read'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(IopsReadEp, self).__init__(*args)


class IopsWriteEp(_MetricEndpoint):
    _name = 'iops_write'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(IopsWriteEp, self).__init__(*args)


class ThptReadEp(_MetricEndpoint):
    _name = 'thpt_read'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(ThptReadEp, self).__init__(*args)


class ThptWriteEp(_MetricEndpoint):
    _name = 'thpt_write'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(ThptWriteEp, self).__init__(*args)


class LatAvgReadEp(_MetricEndpoint):
    _name = 'lat_avg_read'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(LatAvgReadEp, self).__init__(*args)


class LatAvgWriteEp(_MetricEndpoint):
    _name = 'lat_avg_write'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(LatAvgWriteEp, self).__init__(*args)


class Lat50ReadEp(_MetricEndpoint):
    _name = 'lat_50_read'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(Lat50ReadEp, self).__init__(*args)


class Lat90ReadEp(_MetricEndpoint):
    _name = 'lat_90_read'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(Lat90ReadEp, self).__init__(*args)


class Lat100ReadEp(_MetricEndpoint):
    _name = 'lat_100_read'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(Lat100ReadEp, self).__init__(*args)


class Lat50WriteEp(_MetricEndpoint):
    _name = 'lat_50_write'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(Lat50WriteEp, self).__init__(*args)


class Lat90WriteEp(_MetricEndpoint):
    _name = 'lat_90_write'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(Lat90WriteEp, self).__init__(*args)


class Lat100WriteEp(_MetricEndpoint):
    _name = 'lat_100_write'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(Lat100WriteEp, self).__init__(*args)


class CpuUsageEp(_MetricEndpoint):
    _name = 'cpu_usage'
    _entity_cls = _Entity

    def __init__(self, *args):
        super(CpuUsageEp, self).__init__(*args)


###############################################################################


class TimeEp(_StringEndpoint):
    _name = "time"


###############################################################################


class RootEp(_Endpoint):
    """
    Top-level endoint, the starting point for all API requests
    """
    _name = ""

    def __init__(self, *args):
        super(RootEp, self).__init__(*args)
        self._set_subendpoint(AppInstancesEp)
        self._set_subendpoint(ApiEp)
        self._set_subendpoint(AppTemplatesEp)
        self._set_subendpoint(InitiatorsEp)
        self._set_subendpoint(InitiatorGroupsEp)
        self._set_subendpoint(AccessNetworkIpPoolEp) # To be remove, once access_network_ip_pools functionality is in place
        self._set_subendpoint(AccessNetworkIpPoolsEp)
        self._set_subendpoint(StorageNodesEp)
        self._set_subendpoint(SystemEp)
        self._set_subendpoint(EventLogsEp)
        self._set_subendpoint(AuditLogsEp)
        self._set_subendpoint(FaultLogsEp)
        self._set_subendpoint(RolesEp)
        self._set_subendpoint(UsersEp)
        self._set_subendpoint(UpgradeEp)
        self._set_subendpoint(TimeEp)


###############################################################################
