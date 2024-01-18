from utils import * # our helper functions are stored here
import pandas as pd

class tiltPreProcessor():

    def __init__(self, data_path, write_path) :
        self.data_path = data_path
        self.write_path = write_path
        # required input files
        self.ep_catalogue= pd.read_csv("src/data/example_data/input/scraped_data/scraped_EP_products_catalogue.csv")
        self.dedup_settings_file = 'src/dedupe_files/dedup_learned_settings'
        self.dedup_training_file = 'src/dedupe_files/dedup_training.json'
        self.rl_settings_file = 'src/dedupe_files/record_linkage_learned_settings'
        self.rl_training_file = 'src/dedupe_files/record_linkage_training.json'               

    def pre_process(self): 
        # read in data as Pandas dataframe
        dataframe = pd.read_csv(self.data_path)
        
        # apply filtering step (exlcude rows that can directly be linked to EP catalogue)
        print ("------------ PREPROCESSING STEP {} ------------".format(1))
        flagged_df = flagging_df(dataframe, self.ep_catalogue)

        # apply typo correction algorithm
        print ("------------ PREPROCESSING STEP {} ------------".format(2))
        corrected_df = typo_correct_df(flagged_df)

        # apply translation algorithm
        print ("------------ PREPROCESSING STEP {} ------------".format(3))
        translated_df = translate_df(corrected_df)

        # apply deduplication x record linkage algorithm
        print ("------------ PREPROCESSING STEP {} ------------".format(4))
        deduplicated_df = deduplication(translated_df, self.dedup_settings_file, self.dedup_training_file)

        # if write_path string contains the word base then we are also merging it with the manual clustered data
        if 'base' in self.write_path:
            # read in manual clustered datax 
            manual_clustered_df = pd.read_csv('src/data/example_data/input/manual_clustering.csv')
            # merge the two dataframes on products_id
            deduplicated_df = pd.merge(manual_clustered_df, deduplicated_df, on='products_id')
            # drop cluster_id, clustered_delimited_id,delimited_id
            deduplicated_df = deduplicated_df.drop(['clustered_id', 'clustered_delimited_id', 'delimited_id', 'delimited_products_id'], axis=1).rename(columns = {"clustered": "manual_processed_products_and_services"})
            # reorder columns
            deduplicated_df = deduplicated_df[['products_id','raw_products_and_services', 'manual_processed_products_and_services', 'automatic_processed_products_and_services', 'linked_EP_products_id','linked_EP_products_and_services']]
        # write to csv
        print('Writing results to "{}"'.format(self.write_path))
        deduplicated_df.to_csv(self.write_path, index=False)





