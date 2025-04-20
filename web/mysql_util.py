"""
This file has been written by Qihan Zhuang (z5271722)
It contains MySQL database operation utilities
"""

import pymysql

def get_pw():
    """
    Get the password of MySQL database setted in MySQL configuration during installing/operating MySQL.

    Parameters:
    No arguments

    Returns:
    String : Password
    """
    return 'remnant81234!'

class MysqlUtil:
    """
    An utility class that provides database connection between MySQL and Flask 
    with addition to basic operations to let the backend create/read/update/delete data in the database
    """
    def __init__(self):
        """
        Init function of the class
        The function connect the database and flask project using pymysql module
        """
        self.db = pymysql.connect(
            host='localhost',
            user='root',
            password=get_pw(),
            database='holywood'
        )
        self.searchCursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        self.cursor = self.db.cursor()
    
    def close_db(self):
        """
        Close database

        Parameters:
        No Arguments

        Returns:
        None
        """
        self.db.close()
    
    def insert(self, sql):
        """
        Insert data with specified sql command to the database
        Single time operation with committed transaction
        If the operation fails then the transaction will be rolled back and error trace message will be printed on the console

        Parameters:
        sql (string) : sql command

        Returns:
        None
        """
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()
        finally:
            self.db.close()

    def delete(self, sql):
        """
        Delete data with specified sql command to the database
        Single time operation with committed transaction
        If the operation fails then the transaction will be rolled back and error trace message will be printed on the console

        Parameters:
        sql (string) : sql command

        Returns:
        None
        """
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()
        finally:
            self.db.close()

    def update(self, sql):
        """
        Update data with specified sql command to the database
        Single time operation with committed transaction
        If the operation fails then the transaction will be rolled back and error trace message will be printed on the console

        Parameters:
        sql (string) : sql command

        Returns:
        None
        """
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()
        finally:
            self.db.close()
    
    def fetchone(self, sql):
        """
        Read one data record with specified sql command to the database
        Single time operation with committed transaction
        If the operation fails then the transaction will be rolled back and error trace message will be printed on the console

        Parameters:
        sql (string) : sql command

        Returns:
        One data record matches the sql command, if no match data, return None
        """
        try:
            self.searchCursor.execute(sql)
            result = self.searchCursor.fetchone()
        except Exception as e:
            print(e)
            self.db.rollback()
        finally:
            self.db.close()
        return result
    
    def fetchall(self, sql):
        """
        Read all data records with specified sql command to the database
        Single time operation with committed transaction
        If the operation fails then the transaction will be rolled back and error trace message will be printed on the console

        Parameters:
        sql (string) : sql command

        Returns:
        All data records match the sql command, if no match data, return None
        """
        try:
            self.searchCursor.execute(sql)
            results = self.searchCursor.fetchall()
        except Exception as e:
            print(e)
            self.db.rollback()
        finally:
            self.db.close()
        return results
    
    def fetchmany(self, sql, num_row):
        """
        Read some data records with specified sql command to the database
        Single time operation with committed transaction
        If the operation fails then the transaction will be rolled back and error trace message will be printed on the console

        Parameters:
        sql (string) : sql command
        num_row (int) : top num_row data records

        Returns:
        Specified number of data records match the sql command, if no match data, return None
        """
        try:
            self.searchCursor.execute(sql)
            results = self.searchCursor.fetchmany(num_row)
        except Exception as e:
            print(e)
            self.db.rollback()
        finally:
            self.db.close()
        return results
    
    def insertWithoutClose(self, sql):
        """
        Insert data with specified sql command to the database
        Operation with committed transaction
        If the operation fails then the transaction will be rolled back and error trace message will be printed on the console

        Parameters:
        sql (string) : sql command

        Returns:
        None
        """
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()


    def deleteWithoutClose(self, sql):
        """
        Delete data with specified sql command to the database
        Operation with committed transaction
        If the operation fails then the transaction will be rolled back and error trace message will be printed on the console

        Parameters:
        sql (string) : sql command

        Returns:
        None
        """
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()


    def updateWithoutClose(self, sql):
        """
        Update data with specified sql command to the database
        Operation with committed transaction
        If the operation fails then the transaction will be rolled back and error trace message will be printed on the console

        Parameters:
        sql (string) : sql command

        Returns:
        None
        """
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()

    
    def fetchoneWithoutClose(self, sql):
        """
        Read one data record with specified sql command to the database
        Operation with committed transaction
        If the operation fails then the transaction will be rolled back and error trace message will be printed on the console

        Parameters:
        sql (string) : sql command

        Returns:
        One data record matches the sql command, if no match data, return None
        """
        try:
            self.searchCursor.execute(sql)
            result = self.searchCursor.fetchone()
        except Exception as e:
            print(e)
            self.db.rollback()
        return result
    
    def fetchallWithoutClose(self, sql):
        """
        Read all data records with specified sql command to the database
        Operation with committed transaction
        If the operation fails then the transaction will be rolled back and error trace message will be printed on the console

        Parameters:
        sql (string) : sql command

        Returns:
        All data records match the sql command, if no match data, return None
        """
        try:
            self.searchCursor.execute(sql)
            results = self.searchCursor.fetchall()
        except Exception as e:
            print(e)
            self.db.rollback()
        return results
    

    def fetchmanyWithoutClose(self, sql, num_row):
        """
        Read some data records with specified sql command to the database
        Operation with committed transaction
        If the operation fails then the transaction will be rolled back and error trace message will be printed on the console

        Parameters:
        sql (string) : sql command
        num_row (int) : top num_row data records

        Returns:
        Specified number of data records match the sql command, if no match data, return None
        """
        try:
            self.searchCursor.execute(sql)
            results = self.searchCursor.fetchmany(num_row)
        except Exception as e:
            print(e)
            self.db.rollback()
        return results