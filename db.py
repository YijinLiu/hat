from influxdb import InfluxDBClient

class DB:
    NAME = 'hat'

    def __init__(self, port: int=8086):
        self._client = InfluxDBClient(host='localhost', port=port)

        if not self._is_initialized():
            self._client.create_database(DB.NAME)
        self._client.switch_database(DB.NAME)

        has_default = False
        has_one_minute = False
        has_five_minute = False
        has_ten_minute = False
        has_half_hour = False
        has_one_hour = False
        for rp in self._client.get_list_retention_policies():
            name = rp['name']
            if name == 'default':
                has_default = True
            elif name == 'one_minute':
                has_one_minute = True
            elif name == 'five_minute':
                has_five_minute = True
            elif name == 'ten_minute':
                has_ten_minute = True
            elif name == 'half_hour':
                has_half_hour = True
            elif name == 'one_hour':
                has_one_hour = True
            else:
                self._client.drop_retention_policy(name)

        name = 'default'
        if has_default:
            self._client.alter_retention_policy(
                name, default=True, duration='1w', shard_duration='1d', replication=1)
        else:
            self._client.create_retention_policy(
                name, default=True, duration='1w', shard_duration='1d', replication=1)

        name = 'one_minute'
        if has_one_minute:
            self._client.alter_retention_policy(
                name, default=True, duration='52w', shard_duration='1w', replication=1)
        else:
            self._client.create_retention_policy(
                name, default=True, duration='52w', shard_duration='1w', replication=1)
            select = (
                f'SELECT mean("value") as mean, max("value") as max, min("value") as min '
                f'INTO "{name}"."humidity" FROM "humidity" GROUP BY time(1m)'
            )
            self._client.create_continuous_query(name + '_humidity', select=select)
            select = (
                f'SELECT mean("value") as mean, max("value") as max, min("value") as min '
                f'INTO "{name}"."temperature" FROM "temperature" GROUP BY time(1m)'
            )
            self._client.create_continuous_query(name + '_temperature', select=select)

        name = 'five_minute'
        if has_ten_minute:
            self._client.alter_retention_policy(
                name, default=True, duration='52w', shard_duration='1w', replication=1)
        else:
            self._client.create_retention_policy(
                name, default=True, duration='52w', shard_duration='1w', replication=1)
            select = (
                f'SELECT mean("value") as mean, max("value") as max, min("value") as min '
                f'INTO "{name}"."humidity" FROM "humidity" GROUP BY time(5m)'
            )
            self._client.create_continuous_query(name + '_humidity', select=select)
            select = (
                f'SELECT mean("value") as mean, max("value") as max, min("value") as min '
                f'INTO "{name}"."temperature" FROM "temperature" GROUP BY time(5m)'
            )
            self._client.create_continuous_query(name + '_temperature', select=select)

        name = 'ten_minute'
        if has_ten_minute:
            self._client.alter_retention_policy(
                name, default=True, duration='52w', shard_duration='1w', replication=1)
        else:
            self._client.create_retention_policy(
                name, default=True, duration='52w', shard_duration='1w', replication=1)
            select = (
                f'SELECT mean("value") as mean, max("value") as max, min("value") as min '
                f'INTO "{name}"."humidity" FROM "humidity" GROUP BY time(10m)'
            )
            self._client.create_continuous_query(name + '_humidity', select=select)
            select = (
                f'SELECT mean("value") as mean, max("value") as max, min("value") as min '
                f'INTO "{name}"."temperature" FROM "temperature" GROUP BY time(10m)'
            )
            self._client.create_continuous_query(name + '_temperature', select=select)

        name = 'half_hour'
        if has_ten_minute:
            self._client.alter_retention_policy(
                name, default=True, duration='260w', shard_duration='1w', replication=1)
        else:
            self._client.create_retention_policy(
                name, default=True, duration='260w', shard_duration='1w', replication=1)
            select = (
                f'SELECT mean("value") as mean, max("value") as max, min("value") as min '
                f'INTO "{name}"."humidity" FROM "humidity" GROUP BY time(30m)'
            )
            self._client.create_continuous_query(name + '_humidity', select=select)
            select = (
                f'SELECT mean("value") as mean, max("value") as max, min("value") as min '
                f'INTO "{name}"."temperature" FROM "temperature" GROUP BY time(30m)'
            )
            self._client.create_continuous_query(name + '_temperature', select=select)

        name = 'one_hour'
        if has_ten_minute:
            self._client.alter_retention_policy(
                name, default=True, duration='520w', shard_duration='1w', replication=1)
        else:
            self._client.create_retention_policy(
                name, default=True, duration='520w', shard_duration='1w', replication=1)
            select = (
                f'SELECT mean("value") as mean, max("value") as max, min("value") as min '
                f'INTO "{name}"."humidity" FROM "humidity" GROUP BY time(1h)'
            )
            self._client.create_continuous_query(name + '_humidity', select=select)
            select = (
                f'SELECT mean("value") as mean, max("value") as max, min("value") as min '
                f'INTO "{name}"."temperature" FROM "temperature" GROUP BY time(1h)'
            )
            self._client.create_continuous_query(name + '_temperature', select=select)

    def _is_initialized(self) -> bool:
        for db in self._client.get_list_database():
            if db['name'] == DB.NAME:
                return True
        return False

    def add_data(self, humidity: float, temperature: float) -> bool:
        return self._client.write_points(
            [
                {'measurement': 'humidity', 'fields': {'value': humidity}},
                {'measurement': 'temperature', 'fields': {'value': temperature}}
            ])

    def close(self):
        self._client.close()
