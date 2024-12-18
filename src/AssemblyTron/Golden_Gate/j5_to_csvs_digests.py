'''AssemblyTron j5 parsing script. This variation of the script accomodates desingns that inculde destination plasmid backbones. It functions similarly to j5_to_csvs

This script guides the user through finding the j5 DNA assembly design saved on their local machine. 

The script does not require any input files, and it transfers parsed CSV files to the correct directory in AssemblyTron. 

This script requires that `pandas` be installed in the python environment where the script is run. 

This script should not be executed except when copied to a folder with a j5 combinatorial design file, and then it can also be run as a module by calling `AssemblyTron.j5_to_csvs_digests`

'''

        
import os
import pandas as pd
import re

def find_section_index(lines, section_name):
    for i, line in enumerate(lines):
        if section_name in line:
            return i
    return -1

def parse_j5(path=os.getcwd(), file_suffix="_combinatorial.csv"):
    file_list = [f for f in os.listdir(path) if f.endswith(file_suffix)]

    for input_file in file_list:
        with open(os.path.join(path, input_file), 'r') as file:
            j5lines = file.readlines()

        # Extract line numbers for different sections
        digests = find_section_index(j5lines, "Digest Linearized Pieces")
        oligo = find_section_index(j5lines, "Oligo Synthesis")
        pcr = find_section_index(j5lines, "PCR Reactions")
        gibson = find_section_index(j5lines, "Assembly Pieces (SLIC/Gibson/CPEC)")
        golden_gate = find_section_index(j5lines, "Assembly Pieces (Golden-gate)")
        combinations = find_section_index(j5lines, "Combinations of Assembly Pieces")

        # Check if sections were found; if not, set them to -1
        sections = [oligo, pcr, gibson, golden_gate, combinations]

        # Read Oligo Synthesis section of the CSV file
        oligo_read = pd.read_csv(input_file, skiprows=oligo + 1, nrows=pcr - oligo - 3)
        oligo_read.to_csv(os.path.join(path, "oligo.csv"), index=False)

        pcr_read = None  # Define pcr_read before the conditional block
        assembly_read= None
        combinations_read=None
        digests_read=None
        # Read PCR Reactions section of the CSV file
        if gibson and golden_gate:
            pcr_read = pd.read_csv(input_file, skiprows=pcr + 1, nrows=golden_gate - pcr - 3)
        elif golden_gate:
            pcr_read = pd.read_csv(input_file, skiprows=pcr + 1, nrows=golden_gate - pcr - 3)
        elif gibson:
            pcr_read = pd.read_csv(input_file, skiprows=pcr + 1, nrows=gibson - pcr - 3)
            
        if pcr_read is not None:
            pcr_read.to_csv(os.path.join(path, "pcr.csv"), index=False)
            print("pcr file created successfully")

        # Read Assembly Pieces section of the CSV file
        if gibson and golden_gate:
            assembly_read = pd.read_csv(input_file, skiprows=golden_gate + 1, nrows=combinations - golden_gate - 3)
        elif golden_gate:
            assembly_read = pd.read_csv(input_file, skiprows=golden_gate + 1, nrows=combinations - golden_gate - 3)
        elif gibson:
            assembly_read = pd.read_csv(input_file, skiprows=gibson + 1, nrows=combinations - gibson - 3)
        if assembly_read is not None:
            assembly_read.to_csv(os.path.join(path, "assembly.csv"), index=False)
            print("assembly file created successfully")

        # Read Combinations section of the CSV file
            
        combinations_read = pd.read_csv(input_file, skiprows=combinations + 2)
        if combinations_read is not None:
            combinations_read.to_csv(os.path.join(path, "combinations.csv"), index=False)
            print("combination file created successfully")

        # Read Digest Linearized Pieces section of the CSV file
        digests_read = pd.read_csv(input_file, skiprows=digests + 1, nrows=oligo - digests - 3)
        if combinations_read is not None:
            digests_read.to_csv(os.path.join(path, "digests.csv"), index=False)
            print("digest file created successfully")

if __name__ == "__main__":
     parse_j5()
