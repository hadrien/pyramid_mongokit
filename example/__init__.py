import logging

from datetime import datetime

from bson.objectid import ObjectId

import mongokit

from pyramid_mongokit import register

log = logging.getLogger(__name__)


@register()
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

    config.register_document([UserGame])

    config.generate_index(UserGame, collection='bingo')
    config.generate_index(UserGame, collection='scrabble')
    config.scan(__name__)


def includeme_mongo_connection(config):
    config.include('pyramid_mongokit')

    config.register_document([User, UserGame])

    config.generate_index(User, db_name='games')
    config.generate_index(UserGame, db_name='games', collection='bingo')
    config.generate_index(UserGame, db_name='games', collection='scrabble')

    config.generate_index(User, db_name='another')

    # We can access mongo_connection via config.get_mongo_connection:
    config.get_mongo_connection()
