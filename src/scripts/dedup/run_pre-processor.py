from tiltPreProcessor import tiltPreProcessor
from tkinter import filedialog as fd
import os

# run the tiltPreProcessor.py script
if __name__ == "__main__":  
    print('Select files to process (multiple files can be selected). Loading file dialog...')
    filenames = fd.askopenfilenames()
    print("{} file(s) selected".format(len(filenames)))
    for filename in filenames:
        print("Processing {}".format(os.path.basename(filename)))
        src = filename
        dest = str(os.path.join(os.path.dirname(os.path.dirname(filename)), "output/preprocessed_" + 
                                os.path.basename(filename)).replace("_unprocessed", "")).replace("\\", "/")      
        print(dest)
        tiltPreProcessor(src, dest).pre_process()
        print("Done\n")