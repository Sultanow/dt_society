import numpy as np
import pandas as pd
import pycountry
import re
from typing import Tuple, List, Dict
import gzip


class DigitalTwinTimeSeries:
    def __init__(self, path: str = None, to_iso3: bool = True, df: pd.DataFrame = None):
        """
        Preprocesses and stores geographical year-based data
        Expected format: [meta, country_code, (N year columns)..]

        Args:
            path (str): Path to dataset (can also be URL)
            to_iso3 (bool, optional): Converts country codes to ISO-3 if necessary. Defaults to True.
        """
        self.data = self._preprocess(path) if df is None else df
        self.to_iso3 = to_iso3

    def _preprocess(self, path: str) -> pd.DataFrame:
        """Preprocesses dataframe into required format

        Args:
            path (str): Path to dataset

        Returns:
            pd.DataFrame: Reshaped preprocessed dataset
        """
        data = pd.read_table(path, encoding="ISO-8859–1")

        # Create seperate columns for meta column
        meta_column = data.columns[0].split(",")
        meta_column[-1] = meta_column[-1].split("\\")[0]
        n_meta_columns = len(meta_column)
        data[meta_column] = data.iloc[:, 0].str.split(",", expand=True)
        data = data.drop(data.columns[0], axis=1)

        # Reorder meta columns
        data = data[
            data.columns[-n_meta_columns:].tolist()
            + data.columns[:-n_meta_columns].tolist()
        ]

        # Clean numerical values
        numerical_columns_i = n_meta_columns
        data.iloc[:, numerical_columns_i:] = (
            data.iloc[:, numerical_columns_i:]
            .replace("[a-zA-Z: ]", "", regex=True)
            .replace("", 0, regex=True)
            .astype(np.float32)
        )

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

        assert "geo" in data.columns, "No 'geo' column found in dataset."

        # EA = Eurasian Patent Organization
        invalid_country_codes = ["EA", "XK"]
        old_iso2_codes = {"UK": "GB", "EL": "GR"}

        for key in old_iso2_codes:
            data.loc[data["geo"] == key, "geo"] = old_iso2_codes[key]

        # Drop invalid country codes
        data = data.drop(data[data.geo.str.len() > 2].index)
        data = data.drop(data[data["geo"].isin(invalid_country_codes)].index)

        data["geo"] = data["geo"].apply(iso2_to_iso3)

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
                id_vars="geo",
                value_vars=self.data.columns[first_year_i:],
                var_name="year",
            )
            data_slice_melted["geo"] = data_slice_melted["geo"].astype(str)
            data_slice_melted["value"] = data_slice_melted["value"].astype(np.float32)
            data_slice_melted["year"] = data_slice_melted["year"].astype(int)

            melted_datasets[category] = data_slice_melted

        return melted_datasets
