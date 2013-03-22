from datetime import datetime

from bson.objectid import ObjectId

import mongokit

from pyramid_mongokit import register_document, generate_index


class User(mongokit.Document):

    __collection__ = 'user'

    structure = {
        'username': unicode,
        'first_name': unicode,
        'last_name': unicode,
        'mail': unicode,
        'birthdate': datetime,
        }

    required = structure.keys()

    indexes = [
        {'fields': 'username', 'unique': True},
        {'fields': 'mail'},
    ]


class UserGame(mongokit.Document):

    structure = {
        'user_id': ObjectId,
        'title': unicode,
        'score': int,
        }

    required = structure.keys()

    indexes = [
        {'fields': 'user_id', 'unique': True},
    ]


def includeme_single_db_connection(config):
    """To use single db connection, provide ``MONGO_DB_NAME`` in environment
    variables. ``MONGO_DB_PREFIX`` is optionnal.
    """
    config.include('pyramid_mongokit')

    register_document(config.registry, [User, UserGame])

    generate_index(config.registry, User)
    generate_index(config.registry, UserGame, collection='bingo')
    generate_index(config.registry, UserGame, collection='scrabble')


def includeme_mongo_connection(config):
    config.include('pyramid_mongokit')

    register_document(config.registry, [User, UserGame])

    generate_index(config.registry, User, db_name='games')
    generate_index(config.registry, UserGame, db_name='games',
                   collection='bingo')
    generate_index(config.registry, UserGame, db_name='games',
                   collection='scrabble')
