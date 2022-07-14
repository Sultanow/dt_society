from typing import List
import pandas as pd
import re
from typing import List, Tuple


def get_selected_category_column(data: str, selected_category: str) -> List:
    """Gets all possible values of the selected category present in the dataset

    Args:
        data (str): dataset
        selected_category (str): selected value in category dropdown

    Returns:
        List: list with all possible values
    """
    df = pd.read_json(data)

    categories = df[selected_category].unique()

    return categories


def find_column_intersection_indeces(columns: tuple) -> Tuple[int, int]:
    """Finds common values in both columns of two datasets and their indeces

    Args:
        columns (tuple): tuple containing columns of two datasets

    Returns:
        Tuple[int, int]: indeces of first common value in both columns
    """

    intersection = list(set(columns[0]).intersection(columns[1]))

    intersection.sort()

    numeric_pattern = re.compile("[0-9]+")

    intersection = [i for i in intersection if numeric_pattern.match(i)]

    index_1, index_2 = map(lambda x: x.index(intersection[0]), columns)

    return index_1, index_2
