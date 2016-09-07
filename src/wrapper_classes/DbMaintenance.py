#!/usr/bin/python
import mysql.connector as sql_module
import Utilities
import yaml

######
# This is a wrapper class that is designed to abstract away Database specifics.
# In order to avoid a major refactor, please use the existing method
# signatures.
######


class DbMaintenance:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.statement = None
        self.results_tup = None

        # CHANGE THESE FROM THERE DEFAULT VALUES!!!!!!
        ################################
        self.ip = 'localhost'
        self.username = 'username'
        self.password = 'password'
        self.database = 'database'
        ################################

    def __del__(self):
        self.close_connection()

    def import_db_config(self, config_file):
        try:
            with open(config_file, 'r') as f:
                config = yaml.load(f)
        except IOError, e:
            Utilities.log_exception(e, Utilities.db_log_file)
            config = None

        if config is not None:
            try:
                self.ip = config['db']['ip']
                self.username = config['db']['username']
                self.password = config['db']['password']
                self.database = config['db']['database']
                return True
            except KeyError:
                message = """Improperly formatted config file. Expected format:

                             db:
                                ip: localhost
                                username: username
                                password: password
                                database: database

                    """
                Utilities.log(message, Utilities.db_log_file)

        return False

    def set_db_config(self, username, password, ip, database):
        self.ip = ip
        self.username = username
        self.password = password
        self.database = database

    # Add a config file for this.
    def open_connection(self):
        if self.conn is not None:
            if not self.close_connection():
                Utilities.log("Cannot Connect to the database. Check the "
                                  "login credentials.",
                                  Utilities.db_log_file)
                return False

        try:
            self.conn = sql_module.connect(host=self.ip, user=self.username,
                                           password=self.password,
                                           database=self.database)

            return True

        except sql_module.Error, e:
            Utilities.log_exception(e, Utilities.db_log_file)
            self.conn = None
            return False

    def close_connection(self):
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.cursor:
            self.cursor = None

    def get_cursor(self, stored=False):
        # Open a connection if the dataBase is closed.
        if self.conn is None:
            if not self.open_connection():
                return False
        try:
            if not stored:
                self.cursor = self.conn.cursor(prepared=True, buffered=True)
            else:
                self.cursor = self.conn.cursor()
            return True

        except sql_module.Error, e:
            Utilities.log_exception(e, Utilities.db_log_file)
            self.close_connection()
            return False

    def prepare_statement(self, statement):
        if self.cursor is None:
            if not self.get_cursor():
                return False

        try:
            # Clear the cursor before running another statement
            self.get_results()

            self.cursor.execute(statement)
            self.statement = statement
            return True

        except sql_module.Error, e:
            Utilities.log_exception(e, Utilities.db_log_file)
            self.close_connection()
            return False

    # Only commit if it is an update
    def execute_statement(self, statement=None, values=None, commit=False):
        execute_many = False
        if type(values) is list:
            execute_many = True

        if self.cursor is None:
            if not self.get_cursor():
                return False

        if statement is not None:
            self.statement = statement

        try:
            # Clear the cursor before running another statement
            self.get_results()
            if values is None:
                self.cursor.execute(self.statement)
            elif execute_many:

                self.cursor.executemany(self.statement, values)
            else:
                self.cursor.execute(self.statement, values)

            if commit:
                self.conn.commit()
            return True

        except sql_module.Error, e:
            Utilities.log_exception(e, Utilities.db_log_file)
            self.close_connection()
            return False

    def commit(self):
        if self.conn is None:
            message = "There currently is not a connection to the database"
            Utilities.log(message, Utilities.db_log_file)
            return False

        try:
            self.conn.commit()
            return True
        except sql_module.Error, e:
            Utilities.log_exception(e, Utilities.db_log_file)
            return False

    def execute_stored_procedure(self, procedure, args):
        self.results_tup = None
        if self.cursor is None:
            if not self.get_cursor(stored=True):
                return False

        try:
            res = self.cursor.callproc(procedure, args)
            if list(res) != args:
                self.results_tup = res

        except sql_module.Error, e:
            Utilities.log_exception(e, Utilities.db_log_file)
            self.close_connection()
            return False

        return True

    def get_results(self, stored=False):
        ret = []
        if self.cursor is None:
            return None

        if not stored:
            row = self.cursor.fetchone()
            while row is not None:
                ret.append(row)
                row = self.cursor.fetchone()

        else:
            if self.results_tup:
                ret.append(self.results_tup)
            else:
                for result in self.cursor.stored_results():
                    ret.extend(result.fetchall())
        return ret
