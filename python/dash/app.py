from dash import Dash, dcc, html, Input, Output, exceptions, State, dash_table
import numpy as np
import pandas as pd
import re

from sklearn import datasets

from preprocessing.dataset import DigitalTwinTimeSeries
from preprocessing.parse import parse_dataset

from helpers.layout import (
    get_selected_category_column,
    find_column_intersection_indeces,
)
from helpers.plots import (
    create_multi_line_plot,
    create_choropleth_plot,
    create_two_line_plot,
)

app = Dash(__name__)

app.config.suppress_callback_exceptions = True

df = pd.read_table(
    "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/tec00001.tsv.gz"
)

app.layout = html.Div(
    [
        html.Div(
            [html.H1("Digital Twin of Society")],
            style={
                "textAlign": "center",
                "padding-top": "10px",
                "padding-bottom": "10px",
                "backgroundColor": "#232323",
                "color": "#f2f2f2",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    "Files",
                                    style={
                                        "padding-top": "10px",
                                        "padding-left": "10px",
                                        "padding-bottom": "10px",
                                        "backgroundColor": "#111111",
                                        "font-weight": "bold",
                                        "textAlign": "center",
                                    },
                                ),
                                html.Hr(
                                    style={
                                        "padding": "0px",
                                        "margin": "0px",
                                        "backgroundColor": "#5c6cfa",
                                        "border-color": "#5c6cfa",
                                    }
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                dcc.Upload(
                                    id="table-upload",
                                    children=html.Div(
                                        [
                                            "Drag and Drop or ",
                                            html.A("Select Files"),
                                        ]
                                    ),
                                    style={
                                        # "width": "70%",
                                        # "height": "60px",
                                        "lineHeight": "60px",
                                        "borderWidth": "1px",
                                        "borderStyle": "dashed",
                                        "borderRadius": "5px",
                                        "textAlign": "center",
                                        "margin": "10px",
                                        "font-size": "12px",
                                        "padding": "5px",
                                        "width": "85%",
                                        "min-width": "170px",
                                        "max-width": "200px",
                                    },
                                ),
                                html.Div(
                                    "Select geo column",
                                    style={"margin-left": "5px", "textAlign": "center"},
                                ),
                                dcc.Dropdown(
                                    ["none"],
                                    placeholder="No values found",
                                    clearable=False,
                                    id="geo-dropdown-1",
                                    style={
                                        "margin-top": "5px",
                                        "margin-left": "5px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                        "width": "90%",
                                    },
                                ),
                                html.Div(
                                    "Available Columns",
                                    style={
                                        "margin-top": "15px",
                                        "textAlign": "center",
                                        "font-weight": "bold",
                                        "margin-left": "5px",
                                    },
                                ),
                                dcc.Dropdown(
                                    ["none"],
                                    placeholder="No values found",
                                    clearable=False,
                                    id="columns-dropdown",
                                    style={
                                        "margin-top": "5px",
                                        "margin-left": "5px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                        "width": "90%",
                                    },
                                ),
                                dcc.Dropdown(
                                    ["none"],
                                    placeholder="No values found",
                                    clearable=False,
                                    id="category-dropdown",
                                    style={
                                        "margin-top": "5px",
                                        "margin-left": "5px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                        "width": "90%",
                                    },
                                ),
                                dcc.Store(id="dataset"),
                            ],
                            style={
                                "display": "inline-block",
                                "min-width": "180",
                            },
                        ),
                        html.Div(
                            [
                                dcc.Upload(
                                    id="table-upload-2",
                                    children=html.Div(
                                        [
                                            "Drag and Drop or ",
                                            html.A("Select second file"),
                                        ]
                                    ),
                                    style={
                                        "lineHeight": "60px",
                                        "borderWidth": "1px",
                                        "borderStyle": "dashed",
                                        "borderRadius": "5px",
                                        "textAlign": "center",
                                        "margin": "10px",
                                        "font-size": "12px",
                                        "padding": "5px",
                                        "width": "85%",
                                        "min-width": "200px",
                                    },
                                ),
                                html.Div(
                                    "Select geo column", style={"textAlign": "center"}
                                ),
                                dcc.Dropdown(
                                    ["none"],
                                    placeholder="No values found",
                                    clearable=False,
                                    id="geo-dropdown-2",
                                    style={
                                        "margin-top": "5px",
                                        "margin-left": "5px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                        "width": "90%",
                                    },
                                ),
                                html.Div(
                                    "Available Columns",
                                    style={
                                        "margin-top": "15px",
                                        "textAlign": "center",
                                        "font-weight": "bold",
                                        "margin-left": "5px",
                                    },
                                ),
                                dcc.Dropdown(
                                    ["none"],
                                    placeholder="No values found",
                                    clearable=False,
                                    id="columns-dropdown-2",
                                    style={
                                        "margin-top": "5px",
                                        "margin-left": "5px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                        "width": "90%",
                                    },
                                ),
                                dcc.Dropdown(
                                    ["none"],
                                    placeholder="No values found",
                                    clearable=False,
                                    id="category-dropdown-2",
                                    style={
                                        "margin-top": "5px",
                                        "margin-left": "5px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                        "width": "90%",
                                    },
                                ),
                                dcc.Store(id="dataset-2"),
                            ],
                            id="second-file-upload",
                            style={
                                "display": "inline-block",
                                "margin-left": "10px",
                                "min-width": "235px",
                            },
                        ),
                        html.Div(
                            [
                                html.Div(
                                    "Toggle displayed data",
                                    style={"margin": "10px", "font-weight": "bold"},
                                ),
                                dcc.RadioItems(
                                    ["Dataset 1", "Dataset 2"],
                                    "Dataset 1",
                                    id="data-selector",
                                    inline=False,
                                    style={"display": "inline-block"},
                                ),
                            ],
                            style={
                                "margin-top": "20px",
                                "margin-bottom": "10px",
                                "margin-left": "10px",
                            },
                        ),
                    ],
                    style={
                        "backgroundColor": "#111111",
                        "width": "30%",
                    }
                    # style={"box-shadow": "2px 2px 2px lightgrey"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    "Table",
                                    style={
                                        "padding-top": "10px",
                                        "padding-left": "10px",
                                        "padding-bottom": "10px",
                                        "backgroundColor": "#111111",
                                        "font-weight": "bold",
                                        "textAlign": "center",
                                    },
                                ),
                                html.Hr(
                                    style={
                                        "padding": "0px",
                                        "margin": "0px",
                                        "backgroundColor": "#5c6cfa",
                                        "border-color": "#5c6cfa",
                                    }
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                dash_table.DataTable(
                                    id="data-table",
                                    style_data={
                                        "backgroundColor": "#232323",
                                        "border": "solid 1px #5c6cfa",
                                    },
                                    style_cell={"padding": "5px"},
                                    style_header={
                                        "backgroundColor": "#454545",
                                        "border": "solid 1px #5c6cfa",
                                    },
                                )
                            ],
                            style={
                                "backgroundColor": "#5c6cfa",
                                "overflow": "auto",
                                "max-height": "inherit",
                            },
                        ),
                    ],
                    style={
                        "backroundColor": "#ffffff",
                        "margin-left": "10px",
                        "width": "65%",
                        "max-height": "318px",
                    },
                ),
            ],
            style={
                "backgroundColor": "#232323",
                "height": "385px",
                "display": "flex",
            },
        ),
        html.Div(
            [
                html.Div(style={"backgroundColor": "#232323", "padding": "10px"}),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            options=["1111", "1111"],
                                            placeholder="Select year",
                                            clearable=False,
                                            id="year-dropdown-stats",
                                            style={
                                                "width": "100px",
                                                # "display": "flex",
                                                "font-size": "14px",
                                                "border-top": "0px",
                                                "border-left": "0px",
                                                "border-right": "0px",
                                                "backgroundColor": "#111111",
                                                "border-color": "#5c6cfa",
                                                "border-radius": "0px",
                                                "padding": "0",
                                                "textAlign": "center",
                                            },
                                        ),
                                        html.Div(
                                            "Stats",
                                            style={
                                                "padding-top": "10px",
                                                "padding-left": "10px",
                                                "padding-bottom": "10px",
                                                "backgroundColor": "#111111",
                                                "font-weight": "bold",
                                                "textAlign": "center",
                                                "width": "92%",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex", "width": "99%"},
                                ),
                                html.Hr(
                                    style={
                                        "padding": "0px",
                                        "margin": "0px",
                                        "backgroundColor": "#5c6cfa",
                                        "border-color": "#5c6cfa",
                                        "width": "98%",
                                    }
                                ),
                            ],
                        ),
                        html.Div(
                            style={"padding": "5px", "backgroundColor": "#232323"}
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            html.Div(
                                                ["text"],
                                                style={
                                                    "margin-top": "40px",
                                                    "white-space": "pre-line",
                                                    "display": "flex",
                                                    "margin-left": "150px",
                                                },
                                                id="avg-stat",
                                            ),
                                            style={
                                                "backgroundColor": "#111111",
                                                "display": "flex",
                                                "height": "100px",
                                                "width": "90%",
                                                "textAlign": "center",
                                                "font-size": "20px",
                                            },
                                        ),
                                    ],
                                    style={"display": "inline-block", "width": "25%"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            html.Div(
                                                ["text"],
                                                style={
                                                    "margin-top": "40px",
                                                    "white-space": "pre-line",
                                                    "display": "flex",
                                                    "margin-left": "120px",
                                                },
                                                id="max-stat",
                                            ),
                                            style={
                                                "backgroundColor": "#111111",
                                                "display": "flex",
                                                "height": "100px",
                                                "width": "90%",
                                                "textAlign": "center",
                                                "font-size": "20px",
                                            },
                                        ),
                                    ],
                                    style={"display": "inline-block", "width": "25%"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            html.Div(
                                                ["text"],
                                                style={
                                                    "margin-top": "40px",
                                                    "white-space": "pre-line",
                                                    "display": "flex",
                                                    "margin-left": "100px",
                                                },
                                                id="min-stat",
                                            ),
                                            style={
                                                "backgroundColor": "#111111",
                                                "display": "flex",
                                                "height": "100px",
                                                "width": "90%",
                                                "textAlign": "center",
                                                "font-size": "20px",
                                            },
                                        ),
                                    ],
                                    style={"display": "inline-block", "width": "25%"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                dcc.Dropdown(
                                                    options=["1111", "1111"],
                                                    placeholder="Country",
                                                    id="country-dropdown-stats",
                                                    clearable=False,
                                                    style={
                                                        "width": "100px",
                                                        # "display": "flex",
                                                        "font-size": "14px",
                                                        "border-top": "0px",
                                                        "border-left": "0px",
                                                        "border-right": "0px",
                                                        "backgroundColor": "#111111",
                                                        "border-color": "#5c6cfa",
                                                        "border-radius": "0px",
                                                        "padding": "0",
                                                    },
                                                ),
                                                html.Div(
                                                    ["text"],
                                                    style={
                                                        "margin-top": "40px",
                                                        "white-space": "pre-line",
                                                        "display": "flex",
                                                        "margin-left": "50px",
                                                    },
                                                    id="growth-stat",
                                                ),
                                            ],
                                            style={
                                                "backgroundColor": "#111111",
                                                "display": "flex",
                                                # "padding": "10px",
                                                "height": "100px",
                                                "width": "90%",
                                                "textAlign": "center",
                                                "font-size": "20px",
                                            },
                                        ),
                                    ],
                                    style={"display": "inline-block", "width": "25%"},
                                ),
                            ],
                            style={"display": "flex"},
                        ),
                    ],
                    style={"margin-bottom": "10px"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            "Timeline",
                                            style={
                                                "padding-top": "10px",
                                                "padding-left": "10px",
                                                "padding-bottom": "10px",
                                                "backgroundColor": "#111111",
                                                "font-weight": "bold",
                                                "textAlign": "center",
                                            },
                                        ),
                                        html.Hr(
                                            style={
                                                "padding": "0px",
                                                "margin": "0px",
                                                "border-color": "#5c6cfa",
                                                "backgroundColor": "#5c6cfa",
                                            }
                                        ),
                                    ]
                                ),
                            ],
                            style={"backgroundColor": "#111111"},
                        ),
                        html.Div(
                            [],
                            id="line-div",
                        ),
                    ],
                    style={
                        "display": "inline-block",
                        "width": "40%",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            options=["1111", "1111"],
                                            placeholder="Select year",
                                            clearable=False,
                                            id="year-dropdown-map",
                                            style={
                                                "width": "110px",
                                                # "display": "flex",
                                                "font-size": "14px",
                                                "border-top": "0px",
                                                "border-left": "0px",
                                                "border-right": "0px",
                                                "backgroundColor": "#111111",
                                                "border-color": "#5c6cfa",
                                                "border-radius": "0px",
                                                "padding": "0",
                                                # "textAlign": "center",
                                            },
                                        ),
                                        html.Div(
                                            "Countries",
                                            style={
                                                "padding-top": "10px",
                                                "padding-left": "10px",
                                                "padding-bottom": "10px",
                                                "backgroundColor": "#111111",
                                                "font-weight": "bold",
                                                "textAlign": "center",
                                                "width": "92%",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex"},
                                ),
                                html.Hr(
                                    style={
                                        "padding": "0px",
                                        "margin": "0px",
                                        "backgroundColor": "#5c6cfa",
                                        "border-color": "#5c6cfa",
                                    }
                                ),
                            ]
                        ),
                        html.Div(
                            [],
                            id="map-div",
                        ),
                    ],
                    style={
                        "display": "inline-block",
                        "width": "59.3%",
                        "margin-left": "10px",
                    },
                ),
            ],
            style={"backgroundColor": "#232323"},
        ),
        html.Div(
            [
                html.Div(
                    style={
                        "backgroundColor": "#232323",
                        "display": "block",
                        "padding": "10px",
                    }
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Dropdown(
                                    ["none"],
                                    placeholder="No values found",
                                    clearable=False,
                                    id="country-dropdown",
                                    style={
                                        "width": "150px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                        "border-top": "0px",
                                        "border-left": "0px",
                                        "border-right": "0px",
                                        "border-radius": "0px",
                                        "textAlign": "center",
                                    },
                                ),
                                html.Div(
                                    "Country comparison",
                                    style={
                                        "padding-top": "10px",
                                        "padding-left": "10px",
                                        "padding-bottom": "10px",
                                        "backgroundColor": "#111111",
                                        "font-weight": "bold",
                                        "textAlign": "center",
                                        "width": "85%",
                                    },
                                ),
                            ],
                            style={"display": "flex"},
                        ),
                        html.Hr(
                            style={
                                "padding": "0px",
                                "margin": "0px",
                                "border-color": "#5c6cfa",
                                "backgroundColor": "#5c6cfa",
                            }
                        ),
                    ]
                ),
                html.Div(
                    html.Div(
                        [],
                        id="max_country-comparison-div",
                        style={"display": "inline-block", "width": "100%"},
                    ),
                ),
            ],
            id="compare-div",
            # style={"display": "none"},
        ),
    ],
    style={
        "fontFamily": "helvetica",
        "backgroundColor": "#111111",
        "color": "#f2f2f2",
        "min-width": "1500px",
        "max-width": "1500px",
    },
)


@app.callback(
    Output("columns-dropdown", "options"),
    Output("dataset", "data"),
    Output("table-upload", "children"),
    Output("columns-dropdown", "value"),
    Output("second-file-upload", "style"),
    Output("geo-dropdown-1", "options"),
    Input("table-upload", "contents"),
    Input("table-upload", "filename"),
    State("table-upload", "children"),
)
def preprocess_dataset(file, filename, children):
    if file is not None:
        df, filtered_cols = parse_dataset(file)

        children["props"]["children"] = html.Div([filename])

        if not filtered_cols:

            filtered_cols = ["none"]

        show_second_file_upload = {"display": "inline-block"}

        return (
            filtered_cols,
            df,
            children,
            filtered_cols[0],
            show_second_file_upload,
            filtered_cols,
        )

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("columns-dropdown-2", "options"),
    Output("dataset-2", "data"),
    Output("table-upload-2", "children"),
    Output("columns-dropdown-2", "value"),
    Output("country-dropdown", "options"),
    Output("country-dropdown", "value"),
    Output("data-selector", "style"),
    Output("compare-div", "style"),
    Output("geo-dropdown-2", "options"),
    Input("table-upload-2", "contents"),
    Input("table-upload-2", "filename"),
    State("table-upload-2", "children"),
    Input("dataset", "data"),
)
def preprocess_second_dataset(file, filename, children, data):
    if file is not None:
        df_2, filtered_cols, countries = parse_dataset(file, get_countries=True)

        countries_df_1 = pd.read_json(data)["geo"].unique().tolist()
        countries = [c for c in countries_df_1 if c in set(countries)]

        children["props"]["children"] = html.Div([filename])

        radio_visibility = {"display": "block"}
        show_compare_dropdown = {"display": "block"}

        return (
            filtered_cols,
            df_2,
            children,
            filtered_cols[0],
            countries,
            countries[0],
            radio_visibility,
            show_compare_dropdown,
            filtered_cols,
        )

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("category-dropdown", "options"),
    Output("category-dropdown", "value"),
    Input("columns-dropdown", "value"),
    Input("dataset", "data"),
)
def update_category_dropdown(selected_category, data):
    if data and selected_category != "none":
        categories = get_selected_category_column(data, selected_category)
        return categories, categories[0]

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("category-dropdown-2", "options"),
    Output("category-dropdown-2", "value"),
    Input("columns-dropdown-2", "value"),
    Input("dataset-2", "data"),
)
def update_second_category_dropdown(selected_category, data):
    if data and selected_category != "none":
        categories = get_selected_category_column(data, selected_category)
        return categories, categories[0]

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("year-dropdown-stats", "options"),
    Output("year-dropdown-stats", "value"),
    Output("country-dropdown-stats", "options"),
    Output("country-dropdown-stats", "value"),
    Output("year-dropdown-map", "options"),
    Output("year-dropdown-map", "value"),
    Input("dataset", "data"),
    Input("dataset-2", "data"),
    Input("data-selector", "value"),
)
def update_year_dropdown_stats(data, data_2, data_selector):

    if (data or data_2) and data_selector:

        datasets = {
            "Dataset 1": data,
            "Dataset 2": data_2,
        }

        df = pd.read_json(datasets[data_selector])

        year_re = re.compile("[1-2][0-9]{3}")

        year_columns = [
            column for column in df.columns.to_list() if year_re.match(column)
        ]

        return (
            year_columns,
            year_columns[0],
            df["geo"].unique(),
            df["geo"].unique()[0],
            year_columns,
            year_columns[0],
        )
    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("data-table", "data"),
    Input("dataset", "data"),
    Input("dataset-2", "data"),
    Input("data-selector", "value"),
)
def update_table_content(dataset_1, dataset_2, data_selector):
    if dataset_1 or dataset_2:
        datasets = {"Dataset 1": dataset_1, "Dataset 2": dataset_2}

        df_json = pd.read_json(datasets[data_selector]).round(2).to_dict("records")

        return df_json
    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("avg-stat", "children"),
    Output("max-stat", "children"),
    Output("min-stat", "children"),
    Output("growth-stat", "children"),
    Input("data-selector", "value"),
    State("avg-stat", "children"),
    State("max-stat", "children"),
    State("min-stat", "children"),
    State("growth-stat", "children"),
    Input("year-dropdown-stats", "value"),
    Input("country-dropdown-stats", "value"),
    Input("geo-dropdown-1", "value"),
    Input("geo-dropdown-2", "value"),
    Input("dataset", "data"),
    Input("dataset-2", "data"),
    Input("category-dropdown", "value"),
    Input("columns-dropdown", "value"),
    Input("category-dropdown-2", "value"),
    Input("columns-dropdown-2", "value"),
)
def update_stats(
    dataset_selection,
    avg_stat,
    max_stat,
    min_stat,
    growth_stat,
    year_dropdown_stats,
    country_dropdown_stats,
    geo_dropdown_1,
    geo_dropdown_2,
    dataframe,
    dataframe_2,
    selected_unit,
    category_column,
    selected_unit_2,
    category_column_2,
):
    if (
        dataframe
        and selected_unit
        and category_column != "none"
        and (geo_dropdown_1 or geo_dropdown_2)
    ):
        datasets = {
            "Dataset 1": [dataframe, selected_unit, category_column, geo_dropdown_1],
            "Dataset 2": [
                dataframe_2,
                selected_unit_2,
                category_column_2,
                geo_dropdown_2,
            ],
        }

        df = pd.read_json(datasets[dataset_selection][0])
        filtered_df = df[
            df[datasets[dataset_selection][2]] == datasets[dataset_selection][1]
        ]

        year_column_i = filtered_df.columns.get_loc(year_dropdown_stats)

        avg_stat.clear()

        avg_stat.append(
            "Mean \n" + str(round(filtered_df.iloc[:, year_column_i].mean(axis=0), 2))
        )

        max_val_max_country = filtered_df.iloc[:, year_column_i].max()
        i_max = np.where(filtered_df.iloc[:, year_column_i] == max_val_max_country)[0]

        max_country = str(filtered_df.iloc[i_max, 1].values[0])

        min_val_country = (
            filtered_df[filtered_df.iloc[:, year_column_i] >= 0.01]
            .iloc[:, year_column_i]
            .min()
        )
        i_min = np.where(filtered_df.iloc[:, year_column_i] == min_val_country)[0]

        min_country = str(filtered_df.iloc[i_min, 1].values[0])

        i_country = np.where(
            filtered_df[datasets[dataset_selection][3]] == country_dropdown_stats
        )[0]
        growth_rate = (
            (
                filtered_df.iloc[i_country, -1]
                - filtered_df.iloc[i_country, year_column_i]
            )
            / filtered_df.iloc[i_country, year_column_i]
        ) * 100

        if np.isinf(growth_rate.values[0]):
            growth_rate = "Data incomplete"
        else:
            growth_rate = str(round(growth_rate.values[0], 2)) + "%"

        max_stat.clear()
        max_stat.append(
            "max:\n"
            + str(round(filtered_df.iloc[i_max, year_column_i].values[0], 2))
            + " - "
            + max_country
        )
        min_stat.clear()
        min_stat.append(
            "min: \n"
            + str(round(filtered_df.iloc[i_min, year_column_i].values[0], 2))
            + " - "
            + min_country
        )
        growth_stat.clear()
        growth_stat.append("Growth rate:\n" + growth_rate)

        return avg_stat, max_stat, min_stat, growth_stat
    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("line-div", "children"),
    Input("category-dropdown", "value"),
    Input("columns-dropdown", "value"),
    Input("dataset", "data"),
    Input("category-dropdown-2", "value"),
    Input("columns-dropdown-2", "value"),
    Input("dataset-2", "data"),
    State("line-div", "children"),
    Input("data-selector", "value"),
    Input("geo-dropdown-1", "value"),
    Input("geo-dropdown-2", "value"),
)
def update_line_plot(
    selected_unit,
    category_column,
    dataframe,
    selected_unit_2,
    category_column_2,
    dataframe_2,
    children,
    dataset_selection,
    geo_dropdown_1,
    geo_dropdown_2,
):

    if (
        dataframe
        and selected_unit
        and category_column != "none"
        and (geo_dropdown_1 or geo_dropdown_2)
    ):

        datasets = {
            "Dataset 1": [dataframe, selected_unit, category_column],
            "Dataset 2": [
                dataframe_2,
                selected_unit_2,
                category_column_2,
            ],
        }

        df = pd.read_json(datasets[dataset_selection][0])
        filtered_df = df[
            df[datasets[dataset_selection][2]] == datasets[dataset_selection][1]
        ]

        fig = create_multi_line_plot(filtered_df)

        children.clear()

        children.append(dcc.Graph(figure=fig))

        return children
    elif dataframe and category_column == "none":
        df = pd.read_json(dataframe)
        fig = create_multi_line_plot(df)

        children.clear()

        children.append(dcc.Graph(figure=fig))

        return children

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("map-div", "children"),
    Input("category-dropdown", "value"),
    Input("columns-dropdown", "value"),
    Input("dataset", "data"),
    State("map-div", "children"),
    Input("category-dropdown-2", "value"),
    Input("columns-dropdown-2", "value"),
    Input("dataset-2", "data"),
    Input("geo-dropdown-2", "value"),
    Input("geo-dropdown-1", "value"),
    Input("year-dropdown-map", "value"),
    Input("data-selector", "value"),
)
def update_choropleth(
    selected_unit,
    category_column,
    dataframe,
    children,
    selected_unit_2,
    category_column_2,
    dataframe_2,
    geo_dropdown_2,
    geo_dropdown_1,
    year_dropdown_map,
    selected_data,
):

    if dataframe and selected_unit and category_column != "none" and geo_dropdown_1:

        datasets = {
            "Dataset 1": [dataframe, selected_unit, category_column],
            "Dataset 2": [
                dataframe_2,
                selected_unit_2,
                category_column_2,
            ],
        }

        df = pd.read_json(datasets[selected_data][0])

        filtered_df = DigitalTwinTimeSeries(df=df)
        filtered_df = filtered_df.melt_data(category_column=datasets[selected_data][2])

        filtered_df = filtered_df[datasets[selected_data][1]]

        fig = create_choropleth_plot(filtered_df, year=year_dropdown_map)

        if children:
            children.clear()

        children.append(dcc.Graph(figure=fig))

        return children

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("max_country-comparison-div", "children"),
    Input("category-dropdown", "value"),
    Input("columns-dropdown", "value"),
    Input("dataset", "data"),
    Input("category-dropdown-2", "value"),
    Input("columns-dropdown-2", "value"),
    Input("country-dropdown", "value"),
    Input("dataset-2", "data"),
    State("max_country-comparison-div", "children"),
    Input("geo-dropdown-2", "value"),
    Input("geo-dropdown-1", "value"),
)
def update_max_country_compare(
    selected_unit,
    category_column,
    dataframe,
    selected_unit_2,
    category_column_2,
    selected_max_country,
    dataframe_2,
    children,
    geo_dropdown_2,
    geo_dropdown_1,
):

    if (
        selected_max_country
        and selected_unit_2
        and selected_unit
        and dataframe
        and dataframe_2
        and geo_dropdown_1
        and geo_dropdown_2
    ):
        df = pd.read_json(dataframe)
        df_2 = pd.read_json(dataframe_2)

        filtered_df = df[df[category_column] == selected_unit].reset_index(drop=True)
        filtered_df_2 = df_2[df_2[category_column_2] == selected_unit_2].reset_index(
            drop=True
        )

        i_1, i_2 = find_column_intersection_indeces(
            (filtered_df.columns.tolist(), filtered_df_2.columns.tolist())
        )

        row_1, row_2 = map(
            lambda x: x[x["geo"] == selected_max_country].index[0],
            [filtered_df, filtered_df_2],
        )

        fig = create_two_line_plot(
            filtered_df,
            filtered_df_2,
            row_1,
            row_2,
            i_1,
            i_2,
            selected_unit,
            selected_unit_2,
        )

        children.clear()

        children.append(dcc.Graph(figure=fig))

        return children
    else:
        raise exceptions.PreventUpdate


if __name__ == "__main__":
    app.run_server(debug=True)
