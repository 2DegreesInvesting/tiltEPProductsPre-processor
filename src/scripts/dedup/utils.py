from langdetect import detect_langs, DetectorFactory
from googletrans import Translator
from unidecode import unidecode
from textblob import TextBlob
from tqdm import tqdm
import pandas as pd
import numpy as np
import datetime
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)
import dedupe
import spacy
import time
import os
import re
from transformers import pipeline

tqdm.pandas() # to show progress_apply progress bar

nlp = spacy.load('en_core_web_sm') 

language_detector = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection") # this model is 1.1 gigabyte so it will take around 5 mins to download it
DetectorFactory.seed = 0 # to get deterministic results

translator = Translator()

def conf_ld_detect_language(text, model="def"):
    """Language detection wrapper.
    
    Returns detected language (ISO-code) and confidence of detection. In case of 
    failure of detection string 'ident_fail' and a pd.NA value for confidence is 
    returned.
    
    Args:
        text (str): The string for which language shall be detected.
        model (str): The model to be used for language detection. Defaults to langdetect model.
    Returns:
        result (str): The detected language (ISO-code).
    """
    try:
        if model == "def":
            highest_conf = detect_langs(text)[0]
            return highest_conf.lang
        else:
            result = language_detector(text)[0]
            return str(result["label"])
    except:   
        return "ident_fail", pd.NA
    
def typo_correction(text=""):
    """Typo correction wrapper.
    
    Returns corrected text. In case of failure of correction the original text 
    is returned. 
    
    Args:
        text (str): The string to be corrected.
    Returns:
        corrected_text (str): The corrected string.
    """
    try:
        # contextualspellcheck only works for english. the same applies to textblob and the huggingface pipeline. pyspellcheck does work with different languages but requires single words as input. (aka splitted)
        return(TextBlob(text).correct().string)
    except:
        return text
    
def translate_Google(text):
    """
    This function translates the text into English using Google Translator

    Args:
        text (str): The string to be translated.
    Returns:
        translated_text (str): The translated string.
    """
    try:
        translated = translator.translate(text).text
        return translated
    except:
        return np.nan
    
def preProcess(column):
    """
    This function preprocesses the text by removing special characters, converting to lowercase, and removing extra spaces.

    Args:
        column (str): The string to be preprocessed.
    Returns:
        processed_column (str): The preprocessed string.
    """
    column = unidecode(column)
    column = re.sub('\n', ' ', column)
    column = re.sub('-', '', column)
    column = re.sub('/', ' ', column)
    column = re.sub("'", '', column)
    column = re.sub(",", '', column)
    column = re.sub(":", ' ', column)
    column = re.sub('  +', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    if not column:
        column = None
    return column

def convert_pandas_to_dict(dataframe, which = "None", type = "dedup"):
    """
    This function converts the pandas dataframe to a dictionary. The key will be the index of the row and the value will be the contents of the row (column values)
    
    Args:
        dataframe (pd.DataFrame): The dataframe to be converted.
        which (str): Indicates which of the two dataframes it is (left or right or any arbitrary opposites).
        type (str): Indicates whether the dataframe is for deduplication or record linkage.
    Returns:
        dictionary_data (dict): The converted dictionary.
    """
    data_d = {}
    for i, row in dataframe.iterrows():
        x = zip(row.index, row.values)
        clean_row = dict([(k, preProcess(str(v))) for (k, v) in x])
        if type != "dedup":
            data_d[which + str(i)] = clean_row
        else:
            data_d[i] = dict(clean_row)
    return data_d

def seconds_conversion(seconds):
    """
    This function converts seconds to hours, minutes, and seconds.

    Args:
        seconds (int): The number of seconds to be converted.
    Returns:
        tuple: The converted hours, minutes, and seconds.
    """
    # Convert the time difference to a timedelta object
    time_delta = datetime.timedelta(seconds=seconds)

    # Extract the hours, minutes, and seconds from the timedelta object
    hours = time_delta.seconds // 3600
    minutes = (time_delta.seconds % 3600) // 60
    seconds = time_delta.seconds % 60
    return (hours, minutes, seconds)

def typo_correct_df(df):
    """Typo correction wrapper for dataframes.
    
    Returns dataframe with corrected text. In case of failure of correction the 
    original text is returned. 
    
    Args:
        df (pd.DataFrame): The dataframe containing the text to be corrected.
    Returns:
        corrected_df (pd.DataFrame): The dataframe with corrected text.
    """
    #df['ID'] = range(1, len(df) + 1)
    # detect the language of the text
    print("Detecting the language of the text...")
    df.loc[:, "language (ISO-code)"] = df["products_and_services"].progress_apply(lambda x: conf_ld_detect_language(x))

    # then take subset of english texts
    print("Taking subset of English texts...")
    english_df = df[df["language (ISO-code)"] == "en"]
    # exclude enlgish texts from the original df
    df = df[df["language (ISO-code)"] != "en"]

    # apply typo correction to english texts
    print("Applying typo correction...")
    english_df = english_df.copy()
    english_df.loc[:, "typo_corrected"] = english_df["products_and_services"].progress_apply(lambda x: typo_correction(x))

    # merge the corrected english texts with the original df
    print("Merging the corrected english texts with the original df...\n")
    df = pd.concat([df, english_df], ignore_index=True)
    # replace empty values in typo_corrected with the original text
    df["typo_corrected"].fillna(df["products_and_services"], inplace=True)
    return df

def translate_df(df):
    """
    This function translates the dataframe into English using Google Translator

    Args:
        df (pd.DataFrame): The dataframe to be translated.
    Returns:
        translated_df (pd.DataFrame): The translated dataframe.
    """
    # then take subset of english texts
    print("Taking subset of non-english texts...")
    non_english_df = df[df["language (ISO-code)"] != "en"]
    # exclude enlgish texts from the original df
    df = df[df["language (ISO-code)"] == "en"]

    # apply typo correction to english texts
    print("Applying translation...")
    non_english_df = non_english_df.copy()
    non_english_df.loc[:, 'translated_text'] = non_english_df['typo_corrected'].progress_apply(translate_Google)

    # merge the corrected english texts with the original df
    print("Merging the corrected english texts with the original df...\n")
    df = pd.concat([df, non_english_df], ignore_index=True)
    
    # replace empty values in translated column with the typo corrected text
    df["translated_text"].fillna(df["typo_corrected"], inplace=True)
    translated_df = df.copy().drop(columns=["typo_corrected", "language (ISO-code)"]).rename(columns={"products_and_services":"raw_products_and_services","translated_text": "products_and_services"})
    return translated_df

def deduplication(file, settings, training, write = False, out = "None"):
   """
   This function deduplicates the dataframe using the dedupe library.

   Args:
       file (str or pd.Dataframe): The path to the file to be deduplicated or a pandas dataframe.
       settings (str): The path to the settings file.
       training (str): The path to the training file.
       write (bool): Indicates whether to write the deduplicated output to file.
       out (str): The path to the output file.
    Returns:
        df (pd.DataFrame): The deduplicated dataframe.
   """
   # Read the csv files
   print('Importing data ...')
   if isinstance(file, str):
       df = pd.read_csv(file)
   else:
       df = file

   # stage 1: Deduplication using dedupe library
   print("----Start of stage 1----")
   print('Preparing dedupe data ...')
   dedup_data = convert_pandas_to_dict(df, "dedup")

   if os.path.exists(settings):
      print('Settings file found! Reading settings from "{}"'.format(settings))
      with open(settings, 'rb') as sf:
         deduper = dedupe.StaticDedupe(sf)
   # If no settings file exists, create train a new linker object
   else:
      # Define the fields that will be used for the record linkage
      fields = [
               {'field': 'products_and_services', 'type': 'String'}] # consider Text type instead of String
      
      # Create a new linker object and pass the fields to it
      deduper = dedupe.Dedupe(fields)
      print("Preparing training...")
      if os.path.exists(training):
         print('Reading labeled examples from ', training)
         with open(training) as tf:
               deduper.prepare_training(dedup_data,
                                       training_file=tf)
      else:
         # Prepare the linker object for training using the two datasets
         deduper.prepare_training(dedup_data)
      # Start the active labeling
      print('Starting active labeling...')
      dedupe.console_label(deduper)
      # Train the linker object using the active labeling as additional input
      print("Training...")
      deduper.train()
      print("Training finished!")
      # write the labelled training examples to disk
      with open(training, 'w') as tf:
         deduper.write_training(tf)
      # write the settings file to disk
      with open(settings, 'wb') as sf:
         deduper.write_settings(sf)

   print('Clustering..')
   clustered_dupes = deduper.partition(dedup_data, 0.5)
   print('Clustering finished!. {} duplicates found'.format(len(df)-len(clustered_dupes)))

   print('Dropping duplicates...')
   rows_to_drop = []
   for _, (records, scores) in enumerate(clustered_dupes):
      rows_to_drop.append(records[1:])

   # flatten list of lists
   rows_to_drop = [item for sublist in rows_to_drop for item in sublist]
   df = df.drop(df.index[rows_to_drop])
   
   print ("Duplicates dropped!")
   print("----Finished stage 1----")
   
   if write: 
      print('Writing deduplicated output to file...')
      df.to_csv(out, index=False)

   return df

def record_linkage(left_df, right_df, settings, training, write = False, out = "None"):
    """
    This function performs record linkage on the two dataframes using the dedupe library.

    Args:
        left_df (pd.DataFrame): The left dataframe.
        right_df (pd.DataFrame): The right dataframe.
        settings (str): The path to the settings file.
        training (str): The path to the training file.
        write (bool): Indicates whether to write the deduplicated output to file.
        out (str): The path to the output file.
    Returns:
        merged_df (pd.DataFrame): The merged dataframe.
    """
    print('Importing data ...')
    if isinstance(left_df, str):
        root_l_df = pd.read_csv(left_df)
        root_r_df = pd.read_csv(right_df)
    else:
        root_l_df = left_df.copy()
        root_r_df = right_df.copy()

    # Stage 1: Direct products_and_services linkage using merging
    print("----Start of stage 1----")
    print('Directly merging data...')
    # Merge the two dataframes based on the 'products_and_services' column
    merged_df = root_l_df.merge(root_r_df, on='products_and_services', how='left', suffixes=['_x', '_y']).drop(columns="ID")
    merged_df = merged_df.merge(root_r_df, left_on='products_id_y', right_on='products_id', how="left").drop(columns=["ID","products_id"])
    # Create a new dataframe that contains rows from company_based_p_and_s that could not be directly matched
    non_matched_products = merged_df[merged_df.isna().any(axis=1)].drop(columns=["products_id_y", "products_and_services_y"]).rename(columns={"products_and_services_x": "products_and_services"})
    # Get the percentage of products_and_services that could be directly matched
    percentage_matched = len(merged_df.dropna())/len(root_l_df)*100
    print('Percentage of products_and_services that could be directly matched: {0:.2f}%'.format(percentage_matched))
    print("----Finished stage 1----\n")

    # Stage 2: Remaining products_and_services linkage using dedupe
    print("----Start of stage 2----")
    print('Preparing record linkage data...')
    # Convert the dataframes to dictionaries
    linkage_data_1 = convert_pandas_to_dict(non_matched_products, "left", "linkage")
    linkage_data_2 = convert_pandas_to_dict(root_r_df, "right", "linkage")
    print('Attempting products_and_services linkage on the remainder using dedupe...')
    # Check if a settings file already exists and use if can be found
    if os.path.exists(settings):
        print('Settings file found! Reading settings from "{}"'.format(settings))
        with open(settings, 'rb') as sf:
            linker = dedupe.StaticRecordLink(sf)
    # If no settings file exists, create train a new linker object
    else:
        # Define the fields that will be used for the record linkage
        fields = [
                {'field': 'products_and_services', 'type': 'String'}] # consider Text type instead of String
        
        # Create a new linker object and pass the fields to it
        linker = dedupe.RecordLink(fields)
        print("Preparing training...")
        if os.path.exists(training):
            print('Reading labeled examples from ', training)
            with open(training) as tf:
                linker.prepare_training(linkage_data_1,
                                        linkage_data_2,
                                        training_file=tf,
                                        sample_size=10000)
        else:
            # Prepare the linker object for training using the two datasets
            linker.prepare_training(linkage_data_1, linkage_data_2, sample_size=10000)
        # Start the active labeling
        print('Starting active labeling...')
        dedupe.console_label(linker)
        # Train the linker object using the active labeling as additional input
        print("Training...")
        linker.train()
        print("Training finished!")
        # write the labelled training examples to disk
        with open(training, 'w') as tf:
            linker.write_training(tf)
        # write the settings file to disk
        with open(settings, 'wb') as sf:
            linker.write_settings(sf)
    # Perform the record linkage
    print('Performing linking...')
    linked_records = linker.join(linkage_data_1, linkage_data_2, 0.0)
    print('Succesfully linked {} records'.format(len(linked_records)))
    for _, (cluster, score) in enumerate(linked_records):
        non_matched_products.loc[int(re.search(r"\d+", cluster[0]).group()), 'products_and_services_y'] = root_r_df.loc[int(re.search(r"\d+", cluster[1]).group()), 'products_and_services']
        non_matched_products.loc[int(re.search(r"\d+", cluster[0]).group()), 'products_id_y'] = root_r_df.loc[int(re.search(r"\d+", cluster[1]).group()), 'products_id']
    
    merged_df = merged_df.fillna(non_matched_products)
    merged_df = merged_df.rename(columns = {"products_id_x": "products_id", 
                                                                         "products_and_services_x": "processed_products_and_services",
                                                                         "products_id_y": "linked_EP_products_id",
                                                                         "products_and_services_y": "linked_EP_products_and_services"})
    print("Coverage increased to {0:.2f}%".format(len(merged_df.dropna())/len(root_l_df)*100))
    print("----Finished stage 2----\n")
    if write:
        print('Writing results to "{}"'.format(out))
        merged_df.to_csv(out, index=False)

    return merged_df

def dedup_and_link(df, ep_df_path, dedup_settings_file, dedup_training_file, linking_settings_file, linking_training_file):
    """
    This function performs deduplication and record linkage on the dataframe.
    
    Args:
        df (pd.DataFrame): The dataframe to be deduplicated and linked.
        ep_df_path (str): The path to the EuroPages catalogue.
        dedup_settings_file (str): The path to the deduplication settings file.
        dedup_training_file (str): The path to the deduplication training file.
        linking_settings_file (str): The path to the record linkage settings file.
        linking_training_file (str): The path to the record linkage training file.
    Returns:
        linked_data (pd.DataFrame): The deduplicated and linked dataframe.
    """
    # Start timer
    print("\n/=========== Dedup x Record Linkage started ===========/")
    start_time = time.time()
    # Phase 1: applying deduplication module to the data
    print("/=========== Start of phase 1: Deduplication ===========/")
    deduped_data = deduplication(df, dedup_settings_file, dedup_training_file)

    # Phase 2: applying record linkage module to the data
    print("\n\n/=========== Start of phase 2: Record Linkage ===========/")
    linked_data = record_linkage(deduped_data, pd.read_csv(ep_df_path), linking_settings_file, linking_training_file)
    end_time = time.time()

    print("\n/=========== Dedup x Record Linkage finished. Duration: {} hours, {} minutes, {} seconds ===========/".format(*seconds_conversion(end_time - start_time)))

    return linked_data
