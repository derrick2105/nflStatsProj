#!/usr/bin/python
import mysql.connector as sql_module
import Utilities
import yaml


class DbMaintenance:
    """
    Database Maintenance wrapper class that is designed to abstract away
    Database specifics in order to avoid major refactoring when the backing
    database changes.
    """

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
        """
        Sets the database endpoint information with the data in ``config_file``.
        Successfully importing the endpoint information does not guarantee \
        that a connection to the database can be made.

        :param config_file: A yaml file with the following format:

        ..testcode::

            db:
              ip: localhost
              username: username
              password: password
              database: database

        :return Bool: True if the data is successfully imported, else False.
        """

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
        """
        A method to update the database endpoint variables.

        :param username: Database username
        :param password: Database password
        :param ip: the ip address or host name of the database
        :param database: The name of a database schema to use.
        """

        self.ip = ip
        self.username = username
        self.password = password
        self.database = database

    def open_connection(self):
        """
        A method to open a connection to the backing database.

        :return Bool: True if a connection is established, else False.
        """

        if self.conn is not None:
            if not self.close_connection():
                Utilities.log("Cannot Connect to the database. Check the "
                              "login credentials.", Utilities.db_log_file)
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
        """
        A method to close a connection to the database if it exists.
        """

        if self.conn:
            self.conn.close()
            self.conn = None
        if self.cursor:
            self.cursor = None

    def get_cursor(self, stored=False):
        """

        :param stored: A bool that determines if the cursor supports prepared \
        statements or not. Only set to false if you are calling a stored \
        procedure. Prepared statements help protect against sql injections.
        :return Bool: True if a cursor is created, else False.
        """

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
        """
        A method to prepare a statement in the database. This method should be \
        called prior to to calling execute_statement if args are to be \
        passed to with the statement to the db.

        :param statement: A valid MySql prepared statement.
        :return Bool: If ``statement`` successfully prepares the statement, \
        else False.
        """
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
        """
        A method to execute ``statement`` with ``vales`` passed as args. The \
        transaction is committed only if ``commit`` is True. Otherwise the \
        commit method must be called.

        :param statement: A valid static or prepared MySql expression.
        :param values: A tuple, a list of tuples, or None. If not None, \
        then values is passed to the database with the statement.
        :param commit: A flag that controls whether or not the transaction is \
        committed.
        :return Bool: True if the statement is successfully executed in the \
        database. Otherwise, False.

        """

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
        """
        A method to commit the transaction to the database.

        :return Bool: True if the commit is successful, else False.
        """

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

    def execute_procedure(self, procedure, args, log_file):
        """
        A method to execute a stored procedure that manages the database \
        connection and returns a list of results.

        :param procedure: A string that names the stored procedure to be \
        executed.
        :param args: A list or other mutable sequence containing the \
        parameters required to execute ``procedure``. Arg types must \
        match the types of the input vars in ``procedure``. \
        :doc:`See stored procedure documentation </stored_procedures>`.
        :param log_file: The path to the log file to be written to.
        :return list: A list of tuples with the  results.
        :return []: If there are no results or the call failed for any reason.
        """
        Utilities.log('Entering execute_procedure.', log_file)
        self.results_tup = None
        if self.cursor is None:
            if not self.get_cursor(stored=True):
                return []
        data = []

        try:
            res = self.cursor.callproc(procedure, args)
            if list(res) != args:
                self.results_tup = res

            data = self.get_results(stored=True)

        except sql_module.Error, e:
            Utilities.log_exception(e, Utilities.db_log_file)
            Utilities.log('Could not execute the stored procedure.', log_file)

        finally:
            Utilities.log('Exiting execute_procedure.', log_file)
            self.close_connection()
            return data

    def get_results(self, stored=False):
        """
        A method to convert the tuples returned by the database into a list
        of tuples.

        :param stored: A bool with default value False.  Set to True only if \
        this call is being made directly after calling a stored procedure. \
        However, if you use the provided methods, you shouldn't need to ever \
        set this to True.
        :return list: A list of tuples returned by the database.
        :return []: If no tuples are returned or if an error occurred.
        """

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

    def populate_db(self, statement, log_file, values):
        """
        A wrapper function that prepares ``statement`` and then executes \
        ``statement`` with the provided values.
        :param statement: A string with a valid MySQL expression in prepared \
        statement form.
        :param log_file: The path to the log file to be written to.
        :param values: A tuple or a list of tuples with the values to be \
        inserted into the database.
        :return Bool: True if the values are successfully inserted into the \
        database, else False.
        """

        Utilities.log('Entering populate_db.', log_file)
        if not self.prepare_statement(statement):
            Utilities.log("Could not prepare statement.", log_file)
            return False

        if not self.execute_statement(values=values, commit=True):
            Utilities.log("Could not execute statement.", log_file)
            return False

        self.close_connection()

        Utilities.log('Exiting populate_db.', log_file)
        return True

    def pull_from_db(self, statement, log_file, values_list=None):
        """
        A wrapper function to pull data from the database. It accepts either a \
        static MySQL expression or a'prapared statement.

        .. testcode::

            Select * from Players; # static statement
            Select * from Players where playerId = %s; # prepared statement \
that requires a value_list

        :param statement: A valid MySQL statement that is either a static \
        expression or if ``values_list`` is not None a valid prepared statement.
        :param log_file: The path the the log file to be written to.
        :param values_list: A tuple to be used as the arguments for the \
        prepared statement generated from ``statement``.
        :return list: A list of tuples with the values returned from the \
        database
        :return []: If the database returns a empty result set or the \
        statement can not be executed.
        """

        Utilities.log('Entering pull_from_db.', log_file)
        results = None
        if values_list:
            self.prepare_statement(statement)
        if self.execute_statement(statement=statement, values=values_list):
            results = self.get_results()
        else:
            Utilities.log("Could not execute statement.", log_file)

        self.close_connection()

        Utilities.log('Exiting pull_from_db.', log_file)
        return results
