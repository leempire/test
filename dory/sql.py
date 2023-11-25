import pymysql
import sqlite3


class SQL:
    def __init__(self, host='localhost', port=3306, user='root', password='sqlmima123', database=None):
        self.connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
        self.cursor = self.connection.cursor()

    def __call__(self, order):
        """执行order"""
        self.cursor.execute(order)
        self.connection.commit()
        return self.cursor.fetchall()

    def execute(self, order):
        return self(order)

    def quit(self):
        self.cursor.close()
        self.connection.close()


class LocalSql:
    def __init__(self, database_filename):
        self.connection = sqlite3.connect(database_filename, check_same_thread=False)

    def __del__(self):
        self.connection.close()

    def _execute(self, statement, values=None):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(statement, values or [])
            return cursor.fetchall()

    def __call__(self, order):
        return self._execute(order)

    def create_table(self, table_name, columns):
        columns_with_types = [
            f'{column_name} {data_type}'
            for column_name, data_type in columns.items()
        ]
        self._execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name}
            ({', '.join(columns_with_types)});
            """
        )

    def add(self, table_name, data):
        placeholders = ', '.join('?' * len(data))
        column_names = ', '.join(data.keys())
        column_values = tuple(data.values())

        self._execute(
            f"""
            INSERT INTO {table_name}
            ({column_names})
            VALUES ({placeholders});
            """,
            column_values,
        )

    def delete(self, table_name, criteria):
        placeholders = [f'{column} = ?' for column in criteria.keys()]
        delete_criteria = ' AND '.join(placeholders)
        self._execute(
            f"""
            DELETE FROM {table_name}
            WHERE {delete_criteria};
            """,
            tuple(criteria.values()),
        )

    def select(self, table_name, criteria=None, order_by=None):
        criteria = criteria or {}
        query = f'SELECT * FROM {table_name}'
        if criteria:
            placeholders = [f'{column} = ?' for column in criteria.keys()]
            select_criteria = ' AND '.join(placeholders)
            query += f' WHERE {select_criteria}'

        if order_by:
            query += f' ORDER BY {order_by}'

        return self._execute(
            query,
            tuple(criteria.values()),
        )

