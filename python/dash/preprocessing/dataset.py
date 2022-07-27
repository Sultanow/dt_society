import numpy as np
import pandas as pd
import pycountry
import re
from typing import Tuple, List, Dict
import gzip


class DigitalTwinTimeSeries:
    def __init__(
        self,
        path: str = None,
        sep: str = "\t",
        to_iso3: bool = True,
        df: pd.DataFrame = None,
        country_codes: bool = True,
        geo_col: str = "geo",
    ):
        """
        Preprocesses and stores time series data

        Args:
            path (str): path or URL to dataset
            sep (str): seperator value in dataset
            to_iso3 (bool, optional): converts country codes to Alpha-3. Defaults to True.
            df (pd.DataFrame, optional): Processed pandas dataframe. Defaults to None.
            country_codes (bool, optional): _description_. Defaults to True.
            geo_col (str, optional): name of the column containing geographical information. Defaults to "geo".
        """
        self.geo_col = geo_col
        self.country_codes = country_codes
        self.sep = sep
        self.to_iso3 = to_iso3
        self.data = self._preprocess(path) if df is None else df

    def _preprocess(self, path: str) -> pd.DataFrame:
        """Preprocesses dataframe into required format

        Args:
            path (str): Path to dataset

        Returns:
            pd.DataFrame: Reshaped preprocessed dataset
        """

        data = pd.read_csv(path, encoding="ISO-8859–1", sep=self.sep)

        columns = data.columns.tolist()

        fused_cols_i = None
        unnamed_cols_i = []

        for col in columns:
            # Check for columns with multiple sub values
            if "," in col:
                fused_cols_i = columns.index(col)
                # Create seperate columns for each sub column
                meta_column = data.columns[fused_cols_i].split(",")
                n_meta_columns = len(meta_column)

                data[meta_column] = data.iloc[:, fused_cols_i].str.split(
                    ",", expand=True
                )
                data = data.drop(data.columns[fused_cols_i], axis=1)

                # Restore original column order
                data = data[
                    data.columns[-n_meta_columns:].tolist()
                    + data.columns[:-n_meta_columns].tolist()
                ]
            # Unnamed columns in csv files are automatically named Unnamed:X by pandas -> to be dropped
            elif "Unnamed" in col:
                unnamed_cols_i.append(columns.index(col))

        if fused_cols_i is not None:
            # Clean numerical values
            numerical_columns_i = n_meta_columns
            data.iloc[:, numerical_columns_i:] = (
                data.iloc[:, numerical_columns_i:]
                .replace("[a-zA-Z: ]", "", regex=True)
                .replace("", 0, regex=True)
                .astype(np.float32)
            )

        if unnamed_cols_i:
            data = data.drop(data.columns[unnamed_cols_i], axis=1)

        if self.country_codes:
            data = self._format_country_codes(data)

        data = self._drop_redundant_columns(data)

        return data

    def _format_country_codes(self, data: pd.DataFrame) -> pd.DataFrame:
        """Check for valid/invalid country codes and convert to ISO-3

        Args:
            data (pd.DataFrame): Dataset

        Returns:
            pd.DataFrame: Dataset with adjusted country codes
        """

        def iso2_to_iso3(iso2_code):
            country = pycountry.countries.get(alpha_2=iso2_code)

            if country is None:
                unknown_country_code = "UNK"
                return unknown_country_code

            return country.alpha_3

        assert self.geo_col in data.columns, "No 'geo' column found in dataset."

        # EA = Eurasian Patent Organization
        invalid_country_codes = ["EA", "XK"]
        old_iso2_codes = {"UK": "GB", "EL": "GR"}

        for key in old_iso2_codes:
            data.loc[data[self.geo_col] == key, self.geo_col] = old_iso2_codes[key]

        # Drop invalid country codes
        data = data.drop(data[data[self.geo_col].str.len() > 2].index)
        data = data.drop(data[data[self.geo_col].isin(invalid_country_codes)].index)

        data[self.geo_col] = data[self.geo_col].apply(iso2_to_iso3)

        return data

    def _drop_redundant_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Drops columns that contain the same value throughout the entire dataset.

        Args:
            data (pd.DataFrame): Dataset

        Returns:
            pd.DataFrame: Dataset
        """
        redundant_columns = []

        for column in data.columns:
            if len(data[column].unique()) == 1:
                redundant_columns.append(column)

        data = data.drop(columns=redundant_columns, axis=1)

        return data

    def melt_data(self, category_column: str) -> Dict[str, pd.DataFrame]:
        """Transform dataset to have a row for each pair of year/country.

        Args:
            category_column (str): Name of additional category column such as age group

        Returns:
            Dict[pd.DataFrame]: Dict containing a dataset for each category (categories are keys)
        """
        categories = self.data[category_column].unique()

        melted_datasets = {}

        year_pattern = re.compile("[1-2][0-9]{3}")

        first_year = next(i for i in self.data.columns if year_pattern.match(i))

        first_year_i = self.data.columns.tolist().index(first_year)

        for category in categories:
            data_slice = self.data[self.data[category_column] == category]

            data_slice_melted = data_slice.melt(
                id_vars=self.geo_col,
                value_vars=self.data.columns[first_year_i:],
                var_name="year",
            )
            data_slice_melted[self.geo_col] = data_slice_melted[self.geo_col].astype(
                str
            )
            data_slice_melted["value"] = data_slice_melted["value"].astype(np.float32)
            data_slice_melted["year"] = data_slice_melted["year"].astype(str)

            melted_datasets[category] = data_slice_melted

        return melted_datasets
