from pathlib import Path
import pandas as pd


def create_merged_data(counties_file, fips_file, output_file="data/merged_data.csv"):
    """
    Create a merged data CSV file by combining county data with FIPS codes.

    Args:
        counties_file (str): Path to the counties.csv file.
        fips_file (str): Path to the fips.csv file.
        output_file (str): Path to save the merged_data.csv file (default is 'data/merged_data.csv').

    Returns:
        None
    """
    # Convert paths to Path objects
    counties_path = Path(counties_file)
    fips_path = Path(fips_file)
    output_path = Path(output_file)

    # Check if the output file already exists
    if output_path.exists():
        print(f"The file '{output_path}' already exists. Skipping processing.")
        return

    # Load the input files
    df = pd.read_csv(
        counties_path,
        dtype={'pop': int},
        float_precision='round_trip',
    )
    fips = pd.read_csv(
        fips_path,
        dtype={'state_code': str, 'county_code': str},
    )

    # Split 'name' column into 'state' and 'county'
    df[['state_name', 'county']] = df['name'].str.split(',', expand=True)

    # Standardize county names and state names for merging
    fips['county'] = (fips['county']
        .str.replace(" county", "", case=False)
        .str.lower()
    )
    fips['state_name'] = fips['state_name'].str.lower()
    df['county'] = df['county'].str.lower()

    # Merge dataframes on 'state_name' and 'county'
    merged_data = pd.merge(df, fips, on=['state_name', 'county'], how='left')

    # Add full FIPS code as 'fips'
    merged_data['fips'] = merged_data['state_code'] + merged_data['county_code']
    merged_data['fips'] = merged_data['fips'].astype(str).str.zfill(5)

    # Ensure the parent directory of the output file exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save the merged dataframe to a CSV file
    merged_data.to_csv(output_path, index=False, float_format="%.1f")

    print(f"Merged data saved to '{output_path}'.")


def load_merged_data(counties_file, fips_file, output_file="data/merged_data.csv"):
    """
    Load the merged data from the specified file.
    If the file does not exist, it automatically creates it by calling create_merged_data().

    Args:
        counties_file (str): Path to the counties.csv file.
        fips_file (str): Path to the fips.csv file.
        output_file (str): Path to the merged_data.csv file (default is 'data/merged_data.csv').

    Returns:
        pd.DataFrame: The loaded DataFrame.
    """
    # Convert output_file to a Path object
    output_path = Path(output_file)

    # Check if the output file exists; if not, create it
    if not output_path.exists():
        print(f"'{output_file}' not found. Creating the file...")
        create_merged_data(counties_file, fips_file, output_file)

    # Load and return the DataFrame
    return pd.read_csv(output_path, dtype={'state_code': str, 'county_code': str, 'fips': str})
