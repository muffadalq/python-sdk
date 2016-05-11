"""
Base classes for endpoint and entitys
"""
__copyright__ = "Copyright 2015, Datera, Inc."

import json
import collections
from .exceptions import _ApiResponseError

###############################################################################


def _is_stringtype(value):
    try:
        return isinstance(value, basestring)
    except NameError:
        return isinstance(value, str)


###############################################################################


class Entity(collections.OrderedDict):
    """
    Entity object
    This is a mapping, so its attributes can be accessed just like a dict
    """

    def __init__(self, context, data):
        """
        Parameters:
          context (dateraapi.context.ApiConnection)
          data (dict)
        """
        super(Entity, self).__init__(data)
        self._context = context
        self._connection = context.connection
        self._data = data

        # Set self._path:
        if 'path' in data:
            self._path = data['path']
        else:
            self._path = None

    def _set_subendpoint(self, klass):
        """ Create a sub-endpoint of the given endpoint type """
        assert(issubclass(klass, Endpoint))
        subendpoint = klass(self._context, self._path)
        subendpoint = self._context.prepare_endpoint(subendpoint)
        subendpoint_name = klass._name
        setattr(self, subendpoint_name, subendpoint)

    def reload(self):
        """ Load a new instance of this entity from the API """
        data = self._connection.read_entity(self._path)
        entity = self.__class__(self._context, data)
        entity = self._context.prepare_entity(entity)
        return entity

    def __str__(self):
        """ A human-readable representation of this entity """
        return json.dumps(self._data, encoding='utf-8', indent=4)

    def __repr__(self, **kwargs):
        return "<" + self.__module__ + "." + self.__class__.__name__ + \
               " " + repr(self._path) + " " + str(self) + ">"

    def set(self, **params):
        """ Modify this entity """
        data = self._connection.update_entity(self._path, params)
        entity = self.__class__(self._context, data)
        entity = self._context.prepare_entity(entity)
        return entity

    def delete(self, **params):
        """ Delete this entity """
        data = self._connection.delete_entity(self._path, data=params)
        entity = self.__class__(self._context, data)
        entity = self._context.prepare_entity(entity)

        # Call any on_delete hooks:
        entity = self._context.on_entity_delete(entity)
        return entity


###############################################################################


class Endpoint(object):
    """ REST API endpoint
        There should be a corresponding Entity Object created
        Eg, /network
    """

    _name = None  # Subclass must initialize it
    _entity_cls = Entity  # Subclass must over-ride this

    def __init__(self, context, parent_path):
        """
        Parameters:
          context (dateraapi.context.ApiContext)
        """
        self._context = context
        if not parent_path and not self._name:
            self._path = ""  # root endpoint
        else:
            self._path = parent_path + '/' + self._name
        self._connection = context.connection

    def __str__(self):
        if self._path:
            return "<" + self.__class__.__name__ + \
                   " " + repr(self._path) + ">"
        else:
            return repr(self)

    def _set_subendpoint(self, klass):
        """ Create a sub-endpoint of the given endpoint type """
        assert(issubclass(klass, Endpoint))
        subendpoint = klass(self._context, self._path)
        subendpoint = self._context.prepare_endpoint(subendpoint)
        subendpoint_name = klass._name
        setattr(self, subendpoint_name, subendpoint)

    def _set_subendpoint_as_endpoint(self, klass):
        """ Create a endpoint of given sub-endpoint type

        If subendpoint level supports some operation (GET, POST etc) but there
        is no operation allowed on endpoint level then set the subendpoint as
        endpoint.

        e.g. Endpoint /init does not support any read or write operation but
             SubEndpoint /init/config supports read (GET) operation. Hence
             setting init_config (replacing "/" by "_") as a endpoint object.
        """
        assert(issubclass(klass, Endpoint))
        subendpoint = klass(self._context, self._path)
        subendpoint = self._context.prepare_endpoint(subendpoint)
        subendpoint_name = klass._name.strip('/').replace('/', '_')
        setattr(self, subendpoint_name, subendpoint)

    def _get_list(self, _path, data):
        """ Returns a list of objects or strings, depending on the endpoint """
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [self._prepare_data(value)
                    for value in data.values()]
        else:
            raise ValueError("Unexpected response: " + repr(data))

    def _prepare_data(self, value):
        """
        If the data looks like a entity, create a Entity object from it,
        else just return it unchanged
        """
        if isinstance(value, dict):
            return self._new_contained_entity(value)
        else:
            return value

    def _new_contained_entity(self, data):
        """ Creates a Entity object
        """
        entity = self._entity_cls(self._context, data)
        entity = self._context.prepare_entity(entity)
        return entity

    def get(self, *args, **params):
        """
        Get a entity by its ID
        If no ID, return the whole collection
        """
        if len(args) == 0:
            # GET the whole collection
            path = self._path  # Eg. /storage_templates
            data = self._connection.read_endpoint(path, params)
            if isinstance(data, dict):
                for key in data:
                    data[key] = self._new_contained_entity(data[key])
                return data
            elif isinstance(data, list):
                return self._get_list(path, data)
            else:
                return data
        elif len(args) == 1:
            # GET a entity in the collection
            entity_id = args[0]
            # /storage_template/MyTemplate
            path = self._path + "/" + entity_id
            data = self._connection.read_entity(path)
            # This should return a single object in a dictionary form
            return self._new_contained_entity(data)
        else:
            raise TypeError("Too many arguments for get()")


class ListEndpoint(Endpoint):
    """ List collection endpoint"""

    def get(self):
        path = self._path
        data = self._connection.read_endpoint(path)
        return data

    def list(self):
        """ Returns a list of strings """
        return self.get()

    def set(self, *args):
        """Sets the endpoint with list passed"""
        data = self._connection.update_endpoint(self._path, args)
        return data


class StringEndpoint(Endpoint):
    """
    Endpoint which returns a simple string
    """
    def get(self):
        """ Returns a string """
        path = self._path
        data = self._connection.read_endpoint(path)
        return data


class ContainerEndpoint(Endpoint):
    """ Entity collection endpoint """

    def create(self, **params):
        """ Create an entity """
        data = self._connection.create_entity(self._path, params)
        entity = self._new_contained_entity(data)

        # Call any on_create hooks:
        entity = self._context.on_entity_create(entity)
        return entity

    def list(self, **params):
        """ Return all entities in this collection as a list """
        path = self._path
        data = self._connection.read_endpoint(path, params)
        return self._get_list(path, data)


class SimpleReferenceEndpoint(Endpoint):
    """
    A LikEndpoint
    supports get() / list() / add() / remove()
    e.g.
        api.app_templates.get('app1').storage_templates.link('/storage_templates/st9')
        /app_templates/:app1/storage_templates

     """
    _name = None  # sub-classes must implement
    _entity_cls = Entity  # sub-classes must implement
    _parent_entity_cls = Entity  # sub-classes must implement

    def _create_parent_entity(self, data):
        return self._parent_entity_cls(self._context, data)

    def _link_unlink(self, op, entity):
        if _is_stringtype(entity):
            path = entity
        else:
            path = entity._path
        params = dict(op=op, path=path)
        data = self._connection.update_endpoint(self._path, params)
        return self._create_parent_entity(data)

    def list(self, **params):
        """ Return all entities in this collection as a list """
        path = self._path
        data = self._connection.read_endpoint(path, params)
        return self._get_list(path, data)

    def add(self, entity):
        return self._link_unlink('add', entity)

    def remove(self, entity):
        return self._link_unlink('remove', entity)


class SingletonEndpoint(Endpoint):
    """ Singleton endpoint """

    def get(self, **params):
        """
        Returns a single entity
        """
        data = self._connection.read_entity(self._path, params)
        return self._new_contained_entity(data)

    def set(self, **params):
        """
        Modifies the entity
        """
        data = self._connection.update_endpoint(self._path, params)
        return self._new_contained_entity(data)

    def create(self, **params):
        """ Create an entity """
        data = self._connection.create_entity(self._path, params)
        entity = self._new_contained_entity(data)

        # Call any on_create hooks:
        entity = self._context.on_entity_create(entity)

        return entity

    def list(self, **params):
        """ Return a 0- or 1-element list """
        try:
            return [self.get(**params)]
        except _ApiResponseError as ex:
            if ex.message.startswith("No data at "):
                return []
            raise


class MetricCollectionEndpoint(ListEndpoint):
    """ Returns a list of dictionaries of available metrics
        e.g. /system/metrics
    """

    def get(self):
        path = self._path
        data = self._connection.read_endpoint(path)
        return data


class MetricEndpoint(Endpoint):
    """ A specific metric endpoint
        e.g. /system/metrics/total_reads
    """
    pass


class MonitoringStatusEndpoint(Endpoint):
    """ Returns a list of dictionaries to check the status of monitor's health
        and the system.
        e.g. /system/health
            /system/storage_status
            /system/volume_status
    """

    def get(self, **params):
        path = self._path
        data = self._connection.read_endpoint(path, params)
        return data

###############################################################################
