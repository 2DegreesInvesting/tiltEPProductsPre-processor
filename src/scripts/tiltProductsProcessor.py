import pandas as pd
import numpy as np
import glob
import os
import csv
import uuid


class tiltProductsProcessor():
    """
    A class that is used to extract a list of products and services from a directory of csv files
    These CSV files are the output of the webscraped data from EuroPages

    @args:
        directory: the directory where the csv files are located. this contains one or more csv files. these files are assumed to use the ; delimiter

        
    @methods:
        load_files: reads all the files in the specified directory and creates one Pandas dataframe from all the files
        split_delimit: splits the products_and_services column into a list of strings such that every string is a product or service
        create_product_id: generates a unique product_id for every product or service
        processing_df: combines the aforementioned methods to create a dataframe with a list of products and services and their corresponding product_id
        write_CSV: write the dataframe to a csv file
    """

    def __init__(self, directory):
        self.directory = directory 
        self.df = self.load_files() # the singular dataframe which contains all the data from the csv files

    def load_files(self):
        # load in all files as a list from the directory and make sure to use correct path referencing
        files = [os.path.normpath(i).replace(os.sep, '/') for i in glob.glob(self.directory + '/*.csv')] 
        # create a list in which the panda dataframes will be stored
        df_list = []
        for file in files:
            # create a csv reader that will read all the files, specifying the delimiter and the quotation character to make sure that the fields are parsed correctly
            spamreader = csv.reader(open(file, encoding='utf-8', errors='ignore'), delimiter=';',  quotechar="~")
            # convert output of the csv reader into a list of lists
            df = list(spamreader)
            # create a pandas dataframe from the list of lists in which the first row is the header
            df = pd.DataFrame(df, columns=df[0])
            # add this dataframe to the list of dataframes
            df_list.append(df) 
        # merge the dataframes into a single dataframe
        df = pd.concat(df_list, ignore_index=True)
        # return the dataframe
        return df
    
    
    def processing_df(self, filename):
        # apply split_delimit method to the dataframe
        products_and_services = self.split_delimit(self.df)
        # apply create_product_id method to the dataframe
        products_and_services = self.create_product_id(products_and_services)
        # drop any duplicates in the products_and_services column
        products_and_services = products_and_services.drop_duplicates(subset=['products_and_services'])
        # write the dataframe to a csv file
        self.write_CSV(products_and_services,filename)
        # return the dataframe
        self.df = products_and_services
        return products_and_services


    def create_product_id(self, dataframe):
        # instantiate a UUID column with all 1's
        dataframe.loc[:, "UUID"] = 1
        # create a unique product_id column using UUID package that creates a unique identifier
        dataframe.loc[:, "products_id"] = dataframe.groupby("products_and_services").UUID.transform(lambda g: uuid.uuid4())
        # drop the UUID column as its not needed anymore
        dataframe.drop("UUID", axis=1, inplace=True)
        return dataframe

    def split_delimit(self, dataframe):
        # create a copy of the dataframe
        splitted_df = dataframe.copy()
        # split the products_and_services column into a list of strings
        splitted_df['products_and_services'] = splitted_df['products_and_services'].str.split('|')
        # explode the products_and_services column into multiple rows
        splitted_df = splitted_df.explode('products_and_services')  
        # replace any empty strings with a null value
        splitted_df["products_and_services"] = splitted_df["products_and_services"].replace("", np.nan)
        # drop any rows with a null value in the products_and_services column
        splitted_df.dropna(subset=['products_and_services'], inplace=True)
        splitted_df = splitted_df.reset_index(drop=True)
        # return the dataframe
        return splitted_df[["products_and_services"]].loc[1:]

    def write_CSV(self, dataframe, filename):
        # write the dataframe to a csv file given the path to which it should be written
        dataframe.to_csv(filename, index=False)
