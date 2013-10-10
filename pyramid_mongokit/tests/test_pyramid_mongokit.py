# -*- coding: utf-8 -*-
import os
import unittest

import mock
import pymongo
from pyramid.config import Configurator


class Test(unittest.TestCase):

    @mock.patch.dict(os.environ, {
        'MONGO_DB_NAME': 'pyramid_mongokit',
        'MONGO_URI': 'mongodb://localhost/',
        })
    def test_includeme(self):
        from pyramid_mongokit import includeme

        config = Configurator(settings={})

        includeme(config)

    def test_register_document(self):
        from pyramid_mongokit import register_document

        registry = mock.MagicMock()
        document_cls = mock.Mock()
        document_cls.__collection__ = 'test_document'

        register_document(registry, document_cls)

    @mock.patch('pyramid_mongokit.end_request')
    @mock.patch('pyramid_mongokit.get_mongo_connection')
    def test_mongo_connection(self, m_get_mongo_connection, m_end_request):
        from pyramid_mongokit import mongo_connection

        request = mock.Mock()

        self.assertEqual(
            mongo_connection(request),
            m_get_mongo_connection.return_value,
            )

        # 1. Mongo client was retrived from request's registry
        m_get_mongo_connection.assert_called_once_with(request.registry)

        # 2. Method start_request of mongo client was called
        m_get_mongo_connection.return_value.start_request.assert_called_once_with()

        # 3. Method end_request of mongo client was registered as a callback for
        # end of request processing
        request.add_finished_callback.assert_called_once_with(
            m_end_request,
            )

    def test_mongo_db(self):
        from pyramid_mongokit import mongo_db

        request = mock.Mock()

        self.assertEqual(
            request.mongo_connection.db,
            mongo_db(request)
            )

    def test_end_request(self):
        from pyramid_mongokit import end_request

        request = mock.Mock()

        end_request(request)

        request.mongo_connection.end_request.assert_called_once_with()


    @mock.patch('os.environ')
    def test_no_db_name(self, os_environ):
        from pyramid_mongokit import includeme
        os_environ.__getitem__.side_effect = KeyError()

        with self.assertRaises(KeyError):
            includeme(mock.Mock())


    @mock.patch.dict(os.environ, {
        'MONGO_DB_NAME': 'pyramid_mongokit',
        'MONGO_URI': 'mongodb://localhost/',
        })
    @mock.patch('pyramid_mongokit.mongokit.Connection.__init__')
    def test_single_db_connection(self, m_client_init):
        config = Configurator(settings={})

        config.include('pyramid_mongokit')

        self.assertEqual(m_client_init.call_count, 1)

        from pyramid_mongokit import get_mongo_connection, SingleDbConnection

        connection = get_mongo_connection(config.registry)
        self.assertIsInstance(connection, SingleDbConnection)

    @mock.patch.dict(os.environ, {
        'MONGO_URI': 'mongodb://localhost/',
        })
    @mock.patch('pyramid_mongokit.mongokit.Connection.__init__')
    def test_multi_db_connection(self, m_client_init):
        config = Configurator(settings={})

        config.include('pyramid_mongokit')

        self.assertEqual(m_client_init.call_count, 1)

        from pyramid_mongokit import get_mongo_connection, MongoConnection

        connection = get_mongo_connection(config.registry)
        self.assertIsInstance(connection, MongoConnection)

    @mock.patch.dict(os.environ, {
        'MONGO_DB_NAME': 'pyramid_mongokit',
        'MONGO_URI': 'mongodb://localhost/?replicaSet=tests',
        })
    @mock.patch('pyramid_mongokit.mongokit.ReplicaSetConnection.__init__')
    def test_replicaset_single_db_connection(self, m_client_init):
        config = Configurator(settings={})

        config.include('pyramid_mongokit')

        self.assertEqual(m_client_init.call_count, 1)

        from pyramid_mongokit import get_mongo_connection, ReplicasetSingleDbConnection

        connection = get_mongo_connection(config.registry)
        self.assertIsInstance(connection, ReplicasetSingleDbConnection)


    @mock.patch.dict(os.environ, {
        'MONGO_URI': 'mongodb://localhost/?replicaSet=tests',
        })
    @mock.patch('pyramid_mongokit.mongokit.ReplicaSetConnection.__init__')
    def test_replicaset_multi_db_connection(self, m_client_init):
        config = Configurator(settings={})

        config.include('pyramid_mongokit')

        self.assertEqual(m_client_init.call_count, 1)

        from pyramid_mongokit import get_mongo_connection, ReplicasetMongoConnection

        connection = get_mongo_connection(config.registry)
        self.assertIsInstance(connection, ReplicasetMongoConnection)
