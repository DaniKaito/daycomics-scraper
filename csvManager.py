import pandas as pd
import os

class CsvManager():
    def __init__(self, csvFilePath, columns):
        self.csvFilePath = csvFilePath
        self.columns = columns
        if not os.path.exists(self.csvFilePath):
            df = pd.DataFrame(columns=self.columns)
            df.to_csv(self.csvFilePath, index=False)
            print(f"Created the following csv file: {self.csvFilePath}")
    
    def loadDataset(self):
        df = pd.read_csv(self.csvFilePath)
        return df

    def saveDataset(self, df):
        df.to_csv(self.csvFilePath, index=False)
    
    def getColumn(self, columnName):
        df = self.loadDataset()
        return df[columnName].values.tolist()

    def getRow(self, columnName, key, df=None):
        df = self.loadDataset()
        return df.loc[df[columnName] == key]
    
    def getValue(self, columnName, valueColumn, key):
        df = self.loadDataset()
        rowIndex = df.loc[df[columnName] == key].index
        return df.loc[rowIndex, valueColumn].values[0]

    def modifyValue(self, columnName, key, newValueColumn, newValue):
        df = self.loadDataset()
        rowIndex = df.loc[df[columnName] == key].index
        df.loc[rowIndex, newValueColumn] = newValue
        self.saveDataset(df=df)

    def removeRow(self, key, columnName):
        df = self.loadDataset()
        df.drop(df[df[columnName] == key].index, inplace=True)
        self.saveDataset(df=df)
    
    def appendRow(self, values):
        if len(values) != len(self.columns):
            raise IndexError("list of values when appending a new row should be the same length of the columns in the dataframe")
        
        df = self.loadDataset()
        df.loc[len(df)] = values
        self.saveDataset(df=df)