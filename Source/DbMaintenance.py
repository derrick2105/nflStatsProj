#!/usr/bin/python
import MySQLdb as SQLModule
import Common
####
# TODO:
# 1. Create a config file with database connection data
####

######
# This is a wrapper class that is designed to abstract away Database specifics.
######


class DbMaintenance:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def __del__(self):
        self.close_connection()

    # Add a config file for this.
    def open_connection(self):
        if self.conn is not None:
            self.close_connection()

        ip = '192.168.1.4'
        username = 'pythonUser'
        password = 'pythonPassword'
        database = 'NFLStats1'
        try:
            self.conn = SQLModule.connect(ip, username, password, database)

        except SQLModule.Error, e:
            Common.log(e, './dbMaintenanceLog.txt')
            self.conn = None

    def close_connection(self):
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.cursor:
            self.cursor = None

    def get_cursor(self):
        # Open a connection if the dataBase is closed.
        if self.conn is None:
            self.open_connection()

        if self.conn is not None:
            try:
                self.cursor = self.conn.cursor()

            except SQLModule.Error, e:
                Common.log(e, './dbMaintenanceLog.txt')
                self.close_connection()

    def execute_statement(self, statement):
        if self.cursor is None:
            self.get_cursor()

        if self.cursor is not None:
            try:
                self.cursor.execute(statement)
                self.conn.commit()

            except SQLModule.Error, e:
                Common.log(e, './dbMaintenanceLog.txt')
                self.close_connection()

    def get_results(self):
        ret = []
        if self.cursor is None:
            return None

        for row in self.cursor.fetchall():
            ret.append(row)
        return ret
