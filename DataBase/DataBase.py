from PyQt5 import QtSql, QtGui
from colorama import Fore

class DataBase:

    def __init__(self, id):


        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE',id)
        self.db.setDatabaseName('robotDb.sqlite')

        if not self.db.open():
            print(f"{Fore.RED}ERROR (hardwareHandler) -> Error while lauching database")
            exit(0)
        else:
            print("Database open")
        
        self.query = QtSql.QSqlQuery(self.db)
        
        #self.db.close()

    def initSensorTable(self,listSensor):
        #self.db.open()
        query = "DROP TABLE SensorValue"
        self.query.exec_(query)
        #exit(0)
        
        
        query = "CREATE TABLE SensorValue (sensor varchar(20), value varchar(20))"
        self.query.exec_(query)
        self.insertSensorValue(listSensor)
        #self.db.close()


    def insertSensorValue(self, listSensor):
       # self.db.open()
        for sensor in listSensor:
            request = "INSERT OR REPLACE INTO SensorValue (sensor, value) " "VALUES ('"+str(sensor)+"', 0-0-0-0)"
            self.query.exec_(request)
        #self.db.close()
    
    def updateSensorValue(self, sensor, value): 
        #self.db.open()
        request = "UPDATE SensorValue SET value ='"+str(value)+"'WHERE sensor ='"+str(sensor)+"'"
        self.query.exec_(request)
        #self.db.close()

    def getSensorValue(self, sensor):
        #self.db.open()
        self.query.exec("SELECT sensor, value FROM SensorValue")
        while(self.query.next()):
            if self.query.value(0) == sensor:
                return self.query.value(1)
        #self.db.close()

