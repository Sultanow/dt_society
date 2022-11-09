import numpy as np
import pandas as pd
import pycountry


class DigitalTwinTimeSeries:
    def __init__(
        self,
        path: str = None,
        sep: str = "\t",
        to_iso3: bool = True,
        df: pd.DataFrame = None,
        geo_col: str = None,
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
        self.geo_col: str = geo_col
        self.sep: str = sep
        self.to_iso3: bool = to_iso3
        self.data: pd.DataFrame = self._preprocess(path) if df is None else df

    def _preprocess(self, path: str) -> pd.DataFrame:
        """Preprocesses dataframe into required format

        Args:
            path (str): Path to dataset

        Returns:
            pd.DataFrame: Reshaped preprocessed dataset
        """
        if self.sep == "dict":
            data = pd.DataFrame.from_records(path)
        else:
            data = pd.read_csv(path, sep=self.sep)

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

        data = self._drop_redundant_columns(data)

        return data

    def _format_country_codes(self, data: pd.DataFrame) -> pd.DataFrame:
        """Check for valid/invalid country codes and convert to ISO-3

        Args:
            data (pd.DataFrame): Dataset

        Returns:
            pd.DataFrame: Dataset with adjusted country codes
        """

        def get_iso3(country, from_iso2: bool):
            germany_states = {
                "Rheinland-Pfalz": "DE-RP",
                "Hessen": "DE-HE",
                "Brandenburg": "DE-BB",
                "Schleswig-Holstein": "DE-SH",
                "Hamburg": "DE-HH",
                "Berlin": "DE-BE",
                "Saarland": "DE-SL",
                "Mecklenburg-Vorpommern": "DE-MV",
                "Baden-Württemberg": "DE-BW",
                "Sachsen": "DE-SN",
                "Niedersachsen": "DE-NI",
                "Bayern": "DE-BY",
                "Sachsen-Anhalt": "DE-ST",
                "Nordrhein-Westfalen": "DE-NW",
                "Bremen": "DE-HB",
                "Thüringen": "DE-TH",
            }

            if from_iso2:
                country = pycountry.countries.get(alpha_2=country)
            else:
                if country in germany_states.keys():
                    return germany_states[country]
                country = pycountry.countries.get(name=country)

            if country is None:
                unknown_country_code = "UNK"
                return unknown_country_code

            return country.alpha_3

        assert self.geo_col in data.columns, "No 'geo' column found in dataset."

        # if not (data[self.geo_col].str.len() > 10).any():
        # EA = Eurasian Patent Organization
        if (data[self.geo_col].str.isupper()).all():
            invalid_country_codes = ["EA", "XK"]
            old_iso2_codes = {"UK": "GB", "EL": "GR"}

            for key in old_iso2_codes:
                data.loc[data[self.geo_col] == key, self.geo_col] = old_iso2_codes[key]

            # Drop invalid country codes
            data = data.drop(data[data[self.geo_col].str.len() > 2].index)
            data = data.drop(data[data[self.geo_col].isin(invalid_country_codes)].index)

            data[self.geo_col] = data[self.geo_col].apply(get_iso3, from_iso2=True)

        else:
            # territories = {"Mainland China": "China", "US": "United States"}
            # for key in territories:
            #     data.loc[data[self.geo_col] == key, self.geo_col] = territories[key]
            data[self.geo_col] = data[self.geo_col].apply(get_iso3, from_iso2=False)

        assert not data.empty, "Column did not contain correct country codes."

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

    def reshape_wide_to_long(self, value_id_column):

        assert (
            self.geo_col != value_id_column
        ), "Column to reshape on can not be the column that has been set as geo column."

        if value_id_column == "None":
            reshaped_data = self.data.melt(id_vars=[self.geo_col], var_name="Time")

        else:
            reshaped_data = (
                self.data.set_index([self.geo_col, value_id_column])
                .rename_axis(["Time"], axis=1)
                .stack()
                .unstack(value_id_column)
                .reset_index()
            )

            reshaped_data["Time"] = reshaped_data["Time"].str.strip()

        return reshaped_data
