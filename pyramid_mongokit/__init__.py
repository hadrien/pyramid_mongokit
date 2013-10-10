# -*- coding: utf-8 -*-
import os
import logging
import urlparse

import mongokit

from pymongo import ReadPreference
from pymongo.uri_parser import parse_uri

from pyramid.decorator import reify

from zope.interface import Interface, implementer

log = logging.getLogger(__name__)

__all__ = ['register_document', 'generate_index', 'get_mongo_connection']


def includeme(config):
    log.info('Configure mongokit connection...')
    db_prefix = os.environ.get('MONGO_DB_PREFIX', '')

    mongo_uri = os.environ['MONGO_URI']
    res = parse_uri(mongo_uri)

    params = {
        'auto_start_request': False,
        'tz_aware': True,
        'read_preference': ReadPreference.SECONDARY_PREFERRED,
        }

    # Udpate params with options contained in uri in order to ensure their
    # use for mongo_client initialization
    params.update(res['options'])

    if 'MONGO_DB_NAME' in os.environ:
        connection = SingleDbConnection(
            os.environ['MONGO_DB_NAME'],
            db_prefix,
            mongo_uri,
            **params
            )
        config.add_request_method(mongo_db, 'mongo_db', reify=True)
    else:
        connection = MongoConnection(
            db_prefix,
            mongo_uri,
            **params
            )
        config.add_request_method(mongo_db, 'get_mongo_db')

    config.registry.registerUtility(connection)

    config.add_request_method(mongo_connection, 'mongo_connection',
                              reify=True)

    log.info('Mongo connection configured...')


class IMongoConnection(Interface):
    pass


@implementer(IMongoConnection)
class MongoConnection(mongokit.Connection):

    def __init__(self, db_prefix, *args, **kwargs):
        super(MongoConnection, self).__init__(*args, **kwargs)
        self.db_prefix = db_prefix
        log.info('Creating connection: args=%s kwargs=%s', args, kwargs)

    def get_db(self, db_name):
        return getattr(self, '%s%s' % (self.db_prefix, db_name))

    def generate_index(self, document_cls, db_name=None, collection=None):
        collection = collection if collection else document_cls.__collection__
        document_cls.generate_index(self.get_db(db_name)[collection])

    def prefixed_database_names(self):
        return (name for name in self.database_names()
                if name.startswith(self.db_prefix))


@implementer(IMongoConnection)
class SingleDbConnection(MongoConnection):

    def __init__(self, db_name, db_prefix, uri, *args, **kwargs):
        uri = list(urlparse.urlsplit(uri))
        uri[2] = db_prefix + db_name
        uri = urlparse.urlunsplit(uri)
        super(SingleDbConnection, self).__init__(db_prefix, uri, *args,
                                                 **kwargs)
        self.db_name = db_name

    @reify
    def db(self):
        return self.get_db(self.db_name)

    def get_db(self, db_name=None):
        return super(SingleDbConnection, self).get_db(self.db_name)

    def generate_index(self, document_cls, db_name=None, collection=None):
        super(SingleDbConnection, self).generate_index(document_cls,
                                                       self.db_name,
                                                       collection)


def generate_index(registry, document_cls, db_name='', collection=None):
    mongo_connection = get_mongo_connection(registry)
    mongo_connection.generate_index(document_cls, db_name=db_name,
                                    collection=collection)


def register_document(registry, document_cls):
    mongo_connection = get_mongo_connection(registry)
    mongo_connection.register(document_cls)


def get_mongo_connection(registry):
    return registry.getUtility(IMongoConnection)


def mongo_connection(request):
    """This method is dedicated to be reified.
    It ensure that current thread or greenlet always use the same socket until
    request processing is over.
    """
    mongo_client = get_mongo_connection(request.registry)
    mongo_client.start_request()
    request.add_finished_callback(mongo_client.end_request)
    return mongo_client


def mongo_db(request, db_name=False):
    conn = request.mongo_connection
    if db_name:
        return conn.get_db(db_name)
    return conn.db
