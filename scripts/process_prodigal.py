
import sys
import argparse
import re
import csv
import os

def process_prodigal_gff(input_file, output_file, min_length_bp):
    """
    Processes a Prodigal GFF3-like output file.
    
    Extracts SequenceID, start, and stop coordinates for CDS entries, 
    filters by length, uses the input file's basename as the 'Name',
    and swaps coordinates for negative strand genes.
    """
    sequences = []
    
    # 1. Get the basename of the input file for the 'Name' column
    file_basename = os.path.basename(input_file)
    
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            # --- Skip comment and header lines (starting with #) ---
            if line.startswith('#') or not line:
                continue
                
            # --- Process CDS feature line ---
            # Prodigal GFF fields are typically separated by tabs/spaces.
            fields = line.split()
            
            # A standard GFF line has 9 or more fields.
            if len(fields) >= 9:
                seqid = fields[0]        # Field 1: Sequence ID (e.g., NC_031751.1)
                feature_type = fields[2] # Field 3: Feature type (e.g., CDS)
                strand = fields[6]       # Field 7: Strand (+ or -)
                
                # We are only interested in CDS features
                if feature_type != 'CDS':
                    continue
                
                # Fields 4 and 5 are start and end coordinates (always min..max in GFF format)
                try:
                    start_gff = int(fields[3])
                    stop_gff = int(fields[4])
                except ValueError:
                    # Skip lines where coordinates aren't integers
                    continue
                
                # 2. Calculate CDS length
                # Length is calculated as |max - min| + 1, which is stop_gff - start_gff + 1
                orf_length = stop_gff - start_gff + 1
                
                # 3. Skip ORFs shorter than the minimum length
                if orf_length < min_length_bp:
                    continue
                
                # 4. Apply strand logic to determine CodingStart and CodingStop
                # For '+': start_gff is CodingStart, stop_gff is CodingStop
                # For '-': The coordinates must be swapped (end to start)
                if strand == '+':
                    coding_start = start_gff
                    coding_stop = stop_gff
                elif strand == '-':
                    # Swap coordinates for negative strand
                    coding_start = stop_gff
                    coding_stop = start_gff
                else:
                    # Skip if strand information is missing or unexpected
                    continue
                
                # 5. Append the results
                sequences.append({
                    'Name': file_basename,
                    'SequenceID': seqid,
                    'CodingStart': coding_start,
                    'CodingStop': coding_stop
                })

    # 6. Write the output CSV file
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'SequenceID', 'CodingStart', 'CodingStop'])
        writer.writeheader()
        writer.writerows(sequences)

def main():
    parser = argparse.ArgumentParser(description="Process Prodigal GFF3-like output and filter by CDS length, handling strand direction.")
    parser.add_argument("input_file", help="Input file containing Prodigal GFF3-like output")
    parser.add_argument("output_file", help="Output CSV file")
    # Default is 150 bp (50 amino acids * 3)
    parser.add_argument("-l", "--min_length", type=int, default=150, help="Minimum CDS length in base pairs (default: 150)") 

    args = parser.parse_args()

    process_prodigal_gff(args.input_file, args.output_file, args.min_length)
    print(f"Processed data has been written to {args.output_file}")

if __name__ == "__main__":
    main()
