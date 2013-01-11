# -*- coding: utf-8 -*-
import os
import unittest

import mock


class TestPyramidMongokit(unittest.TestCase):

    def test_includeme(self):
        from pyramid.config import Configurator
        from pyramid_mongokit import includeme

        config = Configurator(settings={})

        includeme(config)

    def test_register_document(self):
        from pyramid_mongokit import register_document

        registry = mock.Mock()
        document_cls = mock.Mock()

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
            getattr(request.mongo_connection, os.environ['MONGO_DB_NAME']),
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
    def test_no_db_name(self, env):
        from pyramid_mongokit import includeme
        env.__getitem__.side_effect = KeyError()

        with self.assertRaises(KeyError):
            includeme(mock.Mock())
