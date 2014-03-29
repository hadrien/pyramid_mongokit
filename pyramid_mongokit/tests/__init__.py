import os


def setup_package():  # pragma no cover
    env = os.environ

    if 'MONGO_DB_NAME' in env:
        del env['MONGO_DB_NAME']

    if 'MONGO_URI' in env:
        del env['MONGO_URI']
