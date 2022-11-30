from dateutil import parser
import pandas as pd
import pycountry
from .states import germany_federal
from typing import List, Tuple


def find_geo_column(dataframe: pd.DataFrame, column: str)-> bool:
    """
    Checks a column for country information 
    (ISO-3, ISO-2, english country names or german federal states)

    Args:
        dataframe (pd.DataFrame): dataset
        column (str): selected column to check in
        
    Returns:
        bool: whether the column has country information or not
    """

    negative_matches = 0

    for value in dataframe[column].sample(n=10):
        print(value)
        if isinstance(value, str):
            if len(value) == 2:
                is_country = pycountry.countries.get(alpha_2=value) != None
            elif len(value) == 3:
                is_country = pycountry.countries.get(alpha_3=value) != None
            elif len(value) > 3:
                is_country = (
                    pycountry.countries.get(name=value) != None
                    or value in germany_federal
                )
            elif len(value) < 2:
                is_country = False
                
            if is_country is False:
                negative_matches += 1

                
        else:
            negative_matches += 1
            
        if negative_matches > 4:
                    return False
                    
                
    print(f"{column} is geo column")

    return True


def is_datetime(value: str)-> bool:
    """Checks if a string has a datetime format

    Args:
        value (str): value

    Returns:
        bool: whether the value is datetime or not
    """

    try:
        is_date = bool(parser.parse(value))
        print(f"{value} has dates")
    except:
        is_date = False

    return is_date


def infer_feature_options(dataframe: pd.DataFrame) -> Tuple[List[str], str, List[str]]:
    """
    Infer possible options for selectable features and column with geo data
    
    Features in columns:
    - can not be datetime or float
    
    Features in rows:
    - can not be datetime or float
    - for integers and strings, unique count must be less than 15 to be considered a categorical feature

    Args:
        dataframe (pd.DataFrame): stored dataset

    Returns:
        Tuple[List[str], str]: list of selectable features, column with geo data
    """
    
    columns = dataframe.columns.to_list()
    columns = [c.strip() for c in columns]
    geo_col = None
    feature_candidates = []
    
    for feature in columns:
        # find candidates for feature indidicators in columns
        date_in_column = is_datetime(feature)

        if not date_in_column:
            feature_candidates.append(feature)
        else:
            continue

        # find candidates for feature indidicators in rows
        if dataframe[feature].dtype not in (
            "float64",
            "float",
            "float32",
        ):

            print(f"{feature} has no floats")
            date_in_row = is_datetime(dataframe[feature][0])

            if not date_in_row:
                is_geo_column = find_geo_column(dataframe, feature)

                if is_geo_column is True:
                    geo_col = feature

                # if feature == geo_col:
                #     continue

                features_in_rows = dataframe[feature].unique().tolist()

                if len(features_in_rows) <= 15:
                    feature_candidates.extend(features_in_rows)
        else:
            print(f"{feature} has floats")
            
    if geo_col in feature_candidates:
                feature_candidates.remove(geo_col)
                
    return feature_candidates, geo_col, columns
            
    