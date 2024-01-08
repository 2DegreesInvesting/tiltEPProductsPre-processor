from utils import * # our helper functions are stored here
import pandas as pd
import logging
import os

class tiltPreProcessor():

    def __init__(self, data_path, write_path) :
        self.data_path = data_path
        self.write_path = write_path
        # required input files
        
        self.ep_catalogue= "src/data/example_data/input/scraped_data/scraped_EP_products_catalogue.csv"
        self.dedup_settings_file = 'src/dedupe_files/dedup_learned_settings'
        self.dedup_training_file = 'src/dedupe_files/dedup_training.json'
        self.rl_settings_file = 'src/dedupe_files/record_linkage_learned_settings'
        self.rl_training_file = 'src/dedupe_files/record_linkage_training.json'               

    def pre_process(self): 
        # read in data as Pandas dataframe
        dataframe = pd.read_csv(self.data_path)

        # apply typo correction algorithm
        print ("------------ PREPROCESSING STEP {} ------------".format(1))
        corrected_df = typo_correct_df(dataframe)

        # apply translation algorithm
        print ("------------ PREPROCESSING STEP {} ------------".format(2))
        translated_df = translate_df(corrected_df)

        # apply deduplication x record linkage algorithm
        print ("------------ PREPROCESSING STEP {} ------------".format(3))
        deduplicated_and_linked_df = dedup_and_link(translated_df, self.ep_catalogue, self.dedup_settings_file, self.dedup_training_file, self.rl_settings_file, self.rl_training_file)

        # write to csv
        print('Writing results to "{}"'.format(self.write_path))
        deduplicated_and_linked_df.to_csv(self.write_path, index=False)



