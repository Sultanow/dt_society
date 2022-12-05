import numpy as np
import pandas as pd
import pycountry
from .states import germany_federal


class DigitalTwinTimeSeries:
    def __init__(
        self,
        path: str,
        sep: str = "\t",
        geo_col: str = None,
        filename: str = None,
    ):
        """
        Preprocesses time series data for Digital Twin of Society

        Args:
            path (str): path to the dataset (URL, file path or pd.Dataframe as JSON).
            sep (str, optional): value of separator in file. Defaults to "\t".
            geo_col (str, optional): value of the column with country data. Defaults to None.
            filename (str, optional): name of the dataset file. Defaults to None.
        """

        self.geo_col: str = geo_col
        self.sep: str = sep
        self.data: pd.DataFrame = self._preprocess(path, filename)

    def _preprocess(self, path: str, filename: str) -> pd.DataFrame:
        """Preprocesses dataframe into required format

        Args:
            path (str): Path to dataset
            filename (str): name of the dataset file

        Returns:
            pd.DataFrame: Preprocessed dataset
        """

        if self.sep == "dict":
            data = pd.read_json(path, orient="records")

        else:
            if filename is not None:
                if filename.endswith(".tsv"):
                    data = pd.read_table(path)
                else:
                    data = pd.read_csv(path, sep=None)

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
                .astype("float")
            )

        if unnamed_cols_i:
            data = data.drop(data.columns[unnamed_cols_i], axis=1)

        if self.geo_col != None:
            data = self._format_country_codes(data)

        return data

    def _format_country_codes(self, data: pd.DataFrame) -> pd.DataFrame:
        """Check for valid/invalid country codes and convert to ISO-3

        Args:
            data (pd.DataFrame): Dataset

        Returns:
            pd.DataFrame: Dataset with adjusted country codes
        """

        def get_iso3(country_id: str, from_iso2: bool):

            country_id_split = country_id.split(",")[0]
            if from_iso2:
                country = pycountry.countries.get(alpha_2=country_id)
            else:
                if country_id in germany_federal.keys():

                    return germany_federal[country_id]
                else:
                    country = pycountry.countries.get(name=country_id_split)

            if country is None:
                try:
                    country = pycountry.countries.search_fuzzy(country_id_split)[0]
                except:
                    unknown_country_code = "UNK"
                    print(f"{country_id} is unknown")
                    return unknown_country_code

            return country.alpha_3

        assert self.geo_col in data.columns, "No 'geo' column found in dataset."

        len_counts = data[self.geo_col].map(len).value_counts()

        highest_unique_count = len_counts.iloc[0]
        most_occuring_len = len_counts[len_counts == highest_unique_count].index[0]

        geo_ids = data[self.geo_col].unique().tolist()

        if (data[self.geo_col].str.isupper()).all():
            # ISO-2 to ISO-3
            if most_occuring_len == 2:
                # non ISO-2 lengths should be removed if they occur as well
                data = data.drop(data[data[self.geo_col].str.len() != 2].index)

                geo_codes = {
                    geo_id: get_iso3(geo_id, from_iso2=True) for geo_id in geo_ids
                }
        else:
            geo_codes = {
                geo_id: get_iso3(geo_id, from_iso2=False) for geo_id in geo_ids
            }

        data[self.geo_col] = data[self.geo_col].replace(geo_codes)

        data = data[data[self.geo_col] != "UNK"]

        assert not data.empty, "Column did not contain correct country codes."

        return data

    def reshape_wide_to_long(self, feature_column: str) -> pd.DataFrame:
        """
        Pivots time series data along a column into a "long" format.

        Wide -> time dimension expands column wise
        Long -> time dimension expands row wise

        Args:
            feature_column (str): name of the column that contains features

        Returns:
            pd.DataFrame: transformed dataset
        """

        assert (
            self.geo_col != feature_column
        ), "Column to reshape on can not be the column that has been set as geo column."

        if feature_column == "None":
            reshaped_data = self.data.melt(id_vars=[self.geo_col], var_name="Time")

        else:
            reshaped_data = (
                self.data.set_index([self.geo_col, feature_column])
                .rename_axis(["Time"], axis=1)
                .stack()
                .unstack(feature_column)
                .reset_index()
            )

            reshaped_data["Time"] = reshaped_data["Time"].str.strip()

        return reshaped_data
