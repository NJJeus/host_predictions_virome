import pandas as pd
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Concatenate csv files')
    parser.add_argument('-f', '--files', type=str, nargs='+')
    parser.add_argument('-o', '--output', type=str)

    args = parser.parse_args()

    return args.files, args.output

def concatenate_csv(files):
    dfs = [pd.read_csv(i, index_col=None) for i in files]

    return pd.concat(dfs)

def main():

    files, output_path = parse_args()

    data = concatenate_csv(files)

    data.to_csv(output_path)

if __name__ == "__main__":
    main()

