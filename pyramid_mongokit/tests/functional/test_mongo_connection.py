import os
import unittest

from pyramid.config import Configurator
from pyramid import testing

"""
Functional test of example.
"""


class TestMongoConnection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from pyramid_mongokit import get_mongo_connection
        os.environ['MONGO_URI'] = 'mongodb://localhost'
        os.environ['MONGO_DB_PREFIX'] = 'pm_test_'
        cls.config = cls.get_example_config()
        cls.mongo = get_mongo_connection(cls.config.registry)

    @classmethod
    def tearDownClass(cls):
        del os.environ['MONGO_URI']
        del os.environ['MONGO_DB_PREFIX']
        for name in cls.mongo.database_names():
            if name.startswith('pm_test'):
                cls.mongo.drop_database(name)

    @classmethod
    def get_example_config(cls):
        from example import includeme_mongo_connection
        config = Configurator(settings={})
        config.include(includeme_mongo_connection)
        return config

    def test_configuration(self):
        # assert db exists
        self.assertIn(u'pm_test_games', self.mongo.database_names())

        # assert collections exists
        collection_names = self.mongo.pm_test_games.collection_names()
        self.assertIn(u'user', collection_names)
        self.assertIn(u'bingo', collection_names)
        self.assertIn(u'scrabble', collection_names)

        # assert indexes
        user_indexes = self.mongo.pm_test_games.user.index_information()
        self.assertIn(u'mail_1', user_indexes)
        self.assertIn(u'username_1', user_indexes)

        game_indexes = self.mongo.pm_test_games.bingo.index_information()
        self.assertIn(u'user_id_1', game_indexes)

        game_indexes = self.mongo.pm_test_games.scrabble.index_information()
        self.assertIn(u'user_id_1', game_indexes)

    def test_mongo_db(self):
        from pyramid_mongokit import mongo_db

        request = testing.DummyRequest()
        request.mongo_connection = self.mongo

        # MongoConnection permits multiple db with prefix:
        self.assertEqual(self.mongo['pm_test_bingo'],
                         mongo_db(request, db_name='bingo'))

        self.assertEqual(self.mongo['pm_test_slot'],
                         mongo_db(request, db_name='slot'))

    def test_prefixed_database_name(self):
        self.assertEqual([u'pm_test_another', u'pm_test_games'],
                         list(self.mongo.prefixed_database_names()))


class TestSingleDbConnection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from pyramid_mongokit import get_mongo_connection
        os.environ['MONGO_URI'] = 'mongodb://localhost'
        os.environ['MONGO_DB_NAME'] = 'pm_test_games'
        cls.config = cls.get_example_config()
        cls.mongo = get_mongo_connection(cls.config.registry)

    @classmethod
    def tearDownClass(cls):
        del os.environ['MONGO_URI']
        del os.environ['MONGO_DB_NAME']
        cls.mongo.drop_database('pm_test_games')

    @classmethod
    def get_example_config(cls):
        from example import includeme_single_db_connection
        config = Configurator(settings={})
        config.include(includeme_single_db_connection)
        return config

    def test_configuration(self):
        # assert db exists
        self.assertIn(u'pm_test_games', self.mongo.database_names())

        # assert collections exists
        collection_names = self.mongo.pm_test_games.collection_names()
        self.assertIn(u'user', collection_names)
        self.assertIn(u'bingo', collection_names)
        self.assertIn(u'scrabble', collection_names)

        # assert indexes
        user_indexes = self.mongo.pm_test_games.user.index_information()
        self.assertIn(u'mail_1', user_indexes)
        self.assertIn(u'username_1', user_indexes)

        game_indexes = self.mongo.pm_test_games.bingo.index_information()
        self.assertIn(u'user_id_1', game_indexes)

        game_indexes = self.mongo.pm_test_games.scrabble.index_information()
        self.assertIn(u'user_id_1', game_indexes)

    def test_db_property(self):
        self.assertEqual(self.mongo['pm_test_games'], self.mongo.db)

    def test_mongo_db(self):
        from pyramid_mongokit import mongo_db

        request = testing.DummyRequest()
        request.mongo_connection = self.mongo

        # SingleDbConnection re-write db name:
        self.assertEqual(self.mongo['pm_test_games'],
                         mongo_db(request, db_name='whatever'))
