# -*- coding: utf-8 -*-
import os
import unittest

import mock
import pymongo
from pyramid.config import Configurator


class Test(unittest.TestCase):

    def setUp(self):
        os.environ['MONGO_URI'] = 'mongodb://localhost'
        os.environ['MONGO_DB_NAME'] = 'pyramid_mongokit'

    def tearDown(self):
        del os.environ['MONGO_URI']
        del os.environ['MONGO_DB_NAME']

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

    def test_mongo_connection(self):
        from pyramid_mongokit import mongo_connection

        request = mock.Mock()

        self.assertEqual(
            request.registry.getUtility.return_value,
            mongo_connection(request)
            )

    def test_mongo_db(self):
        from pyramid_mongokit import mongo_db

        request = mock.Mock()

        self.assertEqual(
            request.mongo_connection.db,
            mongo_db(request)
            )

    def test_begin_request(self):
        from pyramid_mongokit import begin_request

        event = mock.Mock()

        begin_request(event)

    def test_end_request(self):
        from pyramid_mongokit import end_request

        request = mock.Mock()

        end_request(request)

    @mock.patch('os.environ')
    def test_no_db_name(self, os_environ):
        from pyramid_mongokit import includeme
        os_environ.__getitem__.side_effect = KeyError()

        with self.assertRaises(KeyError):
            includeme(mock.Mock())

    @mock.patch('pyramid_mongokit.mongokit.Connection.__init__')
    def test_uri_with_params(self, m_client):
        os.environ['MONGO_URI'] = 'mongodb://localhost?replicaSet=tests'
        config = Configurator(settings={})

        config.include('pyramid_mongokit')

        m_client.assert_called_once_with(
            'mongodb://localhost/pyramid_mongokit?replicaSet=tests',
            # this will break if pymongo internals change, but it's the
            # simplest way to write a regression test that makes sense for #2
            auto_start_request=False, tz_aware=True,
            read_preference=pymongo.ReadPreference.SECONDARY_PREFERRED)
