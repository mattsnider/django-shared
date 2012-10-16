from redis import Redis


class ConnectionDoesNotExist(Exception):
    pass


class ConnectionHandler(object):
    def __init__(self, redises):
        self.redises = redises
        self._connections = {}

    def ensure_defaults(self, alias):
        """
        Puts the defaults into the settings dictionary for a given connection
        where no settings is provided.
        """
        try:
            conn = self.redises[alias]
        except KeyError:
            raise ConnectionDoesNotExist("The connection %s doesn't exist" % alias)

        conn.setdefault('DB', 1)
        for setting in ('HOST', 'PORT', 'PASSWORD'):
            conn.setdefault(setting, '')

    def __getitem__(self, alias):
        if alias in self._connections:
            return self._connections[alias]

        self.ensure_defaults(alias)
        redis = self.redises[alias]
        conn = Redis(
            host=redis['HOST'],
            port=redis['PORT'],
            db=redis['DB'],
            password=redis['PASSWORD']
        )
        self._connections[alias] = conn
        return conn

    def __iter__(self):
        return iter(self.redises)

    def all(self):
        return [self[alias] for alias in self]

    def close(self, alias):
        conn = self._connections.pop(alias, None)
        if conn is not None and conn.connection_pool is not None:
            conn.connection_pool.disconnect()

    def close_all(self):
        for alias in self:
            self.close(alias)


class InMemoryRedis(object):
    def __init__(self):
        self.store = {}

    def sadd(self, key, *values):
        if not values:
            raise ValueError("wrong number of arguments for 'sadd' command")
        if key not in self.store:
            self.store[key] = set([])
        prev_len = len(self.store[key])
        self.store[key] |= set(values)
        return len(self.store[key]) != prev_len

    def srem(self, key, *values):
        if not values:
            raise ValueError("wrong number of arguments for 'srem' command")
        if key not in self.store:
            self.store[key] = set([])
        prev_len = len(self.store[key])
        self.store[key] -= set(values)
        return len(self.store[key]) != prev_len

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value):
        self.store[key] = value
        return True

    def _incr_decr(self, key, incr=True):
        if key not in self.store:
            self.store[key] = 0
        if incr:
            self.store[key] += 1
        else:
            self.store[key] -= 1
        return self.store[key]

    def incr(self, key):
        return self._incr_decr(key, incr=True)

    def decr(self, key):
        return self._incr_decr(key, incr=False)

    # FIXME: implement remaining redis functions
