import gzip
import json
import base64
import urllib
from dash import (
    no_update,
    Dash,
    dcc,
    html,
    Input,
    Output,
    exceptions,
    State,
    dash_table,
    callback_context,
)
import numpy as np
import pandas as pd
import re
import requests

from preprocessing.dataset import DigitalTwinTimeSeries
from preprocessing.parse import parse_dataset, get_available_columns

from helpers.layout import (
    get_selected_category_column,
    find_column_intersection_indeces,
)
from helpers.plots import (
    create_multi_line_plot,
    create_choropleth_plot,
    create_two_line_plot,
)

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0,-25",
        "rel": "stylesheet",
    }
]
app = Dash(__name__, external_stylesheets=external_stylesheets)

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
                                                "display": "flex",
                                                "margin-left": "200px",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Span(
                                                    "help",
                                                    className="material-symbols-outlined",
                                                ),
                                                html.Span(
                                                    "Supported column formats:\n [feature, country, (n timestamps..)],\n [timestamp, country, (n_features...)]",
                                                    className="tooltiptext",
                                                    style={
                                                        "font-size": "10px",
                                                        "font-weight": "normal",
                                                        "white-space": "pre-line",
                                                    },
                                                ),
                                            ],
                                            className="tooltip",
                                            style={
                                                "font-weight": "bold",
                                                "textAlign": "center",
                                                "display": "flex",
                                                "margin-right": "0",
                                                "margin-left": "auto",
                                                "padding-top": "7px",
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
                            [
                                dcc.ConfirmDialog(
                                    id="dataset-1-fail",
                                    message="There was an error processing your data. Please make sure it comes in one of the supported formats.",
                                ),
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
                                html.Div(
                                    [
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
                                        dcc.Dropdown(
                                            [",", ";", "\t", "space"],
                                            placeholder="Delimiter",
                                            id="delimiter-dropdown-1",
                                            style={
                                                "margin-top": "5px",
                                                "margin-left": "0px",
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                                # "width": "5px",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex"},
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
                                dcc.ConfirmDialog(
                                    id="dataset-2-fail",
                                    message="There was an error while processing your data. Please make sure it comes in one of the supported formats.",
                                ),
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
                                html.Div(
                                    [
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
                                                "width": "85%",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            [",", ";", "\t", "space"],
                                            placeholder="Delimiter",
                                            id="delimiter-dropdown-2",
                                            style={
                                                "margin-top": "5px",
                                                "margin-left": "0px",
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                                # "width": "5px",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex"},
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
                                html.Div(
                                    [
                                        dcc.RadioItems(
                                            ["Dataset 1", "Dataset 2"],
                                            "Dataset 1",
                                            id="data-selector",
                                            inline=False,
                                            style={"display": "flex"},
                                        ),
                                        html.Button(
                                            "Demo",
                                            id="demo-button",
                                            n_clicks=0,
                                            style={
                                                "margin-right": "5px",
                                                "float": "right",
                                                "display": "flex",
                                                "margin-left": "auto",
                                                "border-color": "#5c6cfa",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex", "margin-top": "15px"},
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
                    },
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
                "height": "400px",
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
                                                "width": "110px",
                                                # "display": "flex",
                                                "font-size": "14px",
                                                "border-top": "0px",
                                                "border-left": "0px",
                                                "border-right": "0px",
                                                "border-bottom": "0px",
                                                "backgroundColor": "#111111",
                                                "border-color": "#5c6cfa",
                                                "border-radius": "0px",
                                                "padding": "0",
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
                                        html.Div(
                                            [
                                                html.Span(
                                                    "help",
                                                    className="material-symbols-outlined",
                                                ),
                                                html.Span(
                                                    "The statistics shown in this section are computed from the selected timestamp until the last time stamp. \n (eg. 2017-2021)",
                                                    className="tooltiptext",
                                                    style={
                                                        "font-size": "10px",
                                                        "font-weight": "normal",
                                                        "white-space": "pre-line",
                                                    },
                                                ),
                                            ],
                                            className="tooltip",
                                            style={
                                                "font-weight": "bold",
                                                "textAlign": "center",
                                                "display": "flex",
                                                "margin-right": "10px",
                                                "margin-left": "auto",
                                                "padding-top": "7px",
                                                "backgroundColor": "#111111",
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
                                                "border-bottom": "0px",
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
                        "padding-top": "15px",
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
                                        "width": "110px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                        "border-top": "0px",
                                        "border-left": "0px",
                                        "border-right": "0px",
                                        "border-bottom": "0px",
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
    Output("dataset-1-fail", "displayed"),
    Output("table-upload", "contents"),
    Input("table-upload", "contents"),
    Input("table-upload", "filename"),
    State("table-upload", "children"),
    Input("demo-button", "n_clicks"),
    Input("geo-dropdown-1", "value"),
    Input("delimiter-dropdown-1", "value"),
)
def preprocess_dataset(
    file: str,
    filename: str,
    upload_children: list,
    demo_button_clicks: int,
    geo_dropdown_1: str,
    delimiter_dropdown_1: str,
) -> tuple:
    """Processes file upload

    Args:
        file (str): _description_
        filename (str): _description_
        children (list): _description_

    Raises:
        exceptions.PreventUpdate: _description_

    Returns:
        _type_: _description_
    """
    changed_items = [p["prop_id"] for p in callback_context.triggered][0]

    if (
        (file is not None or "demo-button" in changed_items)
        and geo_dropdown_1 is not None
        and delimiter_dropdown_1
    ):
        if file:
            try:
                content = file.split(",")
                df, filtered_cols = parse_dataset(
                    content[-1], separator=delimiter_dropdown_1, geo_col=geo_dropdown_1
                )
            except Exception as e:
                print(e)
                return (
                    no_update,
                    None,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    True,
                    None,
                )
        elif "demo-button" in changed_items:
            filename = "arbeitslosenquote_eu.tsv"
            df_url = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/tipsun20.tsv.gz"

            df, filtered_cols = parse_dataset(df_url, upload_file=False, separator="\t")

        if "table-upload" in changed_items or "demo-button" in changed_items:
            upload_children["props"]["children"] = html.Div([filename])

        if not filtered_cols:

            filtered_cols = ["none"]

        show_second_file_upload = {"display": "inline-block"}

        return (
            filtered_cols,
            df,
            upload_children,
            filtered_cols[0],
            show_second_file_upload,
            filtered_cols,
            False,
            None,
        )
    elif (
        (file is not None or "demo-button" in changed_items)
        and geo_dropdown_1 is None
        and delimiter_dropdown_1
    ):
        if file:
            columns = get_available_columns(file, separator=delimiter_dropdown_1)
        elif "demo-button" in changed_items:
            filename = "arbeitslosenquote_eu.tsv"
            df_url = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/tipsun20.tsv.gz"

            content = urllib.request.urlopen(df_url).read()
            content = gzip.decompress(content)

            columns = get_available_columns(content, upload_file=False, separator="\t")
            file = base64.b64encode(content).decode("utf-8")

        upload_children["props"]["children"] = html.Div([filename])

        return (
            no_update,
            None,
            upload_children,
            no_update,
            no_update,
            columns,
            False,
            file,
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
    Output("dataset-2-fail", "displayed"),
    Output("table-upload-2", "contents"),
    Input("table-upload-2", "contents"),
    Input("table-upload-2", "filename"),
    State("table-upload-2", "children"),
    Input("dataset", "data"),
    Input("demo-button", "n_clicks"),
    Input("geo-dropdown-2", "value"),
    Input("delimiter-dropdown-2", "value"),
)
def preprocess_second_dataset(
    file: str,
    filename: str,
    upload_children: list,
    data: str,
    demo_button_clicks: int,
    geo_dropdown_2: str,
    delimiter_dropdown_2: str,
) -> tuple:
    """Processes additional dataset

    Args:
        file (str): _description_
        filename (str): _description_
        children (list): _description_
        data (str): _description_

    Raises:
        exceptions.PreventUpdate: _description_

    Returns:
        _type_: _description_
    """

    changed_items = [p["prop_id"] for p in callback_context.triggered][0]

    if (
        (file is not None or "demo-button" in changed_items)
        and geo_dropdown_2 is not None
        and delimiter_dropdown_2
    ):
        if file:
            try:
                content = file.split(",")
                df_2, filtered_cols, countries = parse_dataset(
                    content[-1],
                    get_countries=True,
                    geo_col=geo_dropdown_2,
                    separator=delimiter_dropdown_2,
                )
            except Exception as e:
                print(e)
                return (
                    no_update,
                    None,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    True,
                    None,
                )
        elif "demo-button" in changed_items:
            filename = "bip_europa.tsv"
            df_url = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/tec00001.tsv.gz"
            df_2, filtered_cols, countries = parse_dataset(
                df_url, upload_file=False, get_countries=True
            )

        countries_df_1 = pd.read_json(data)["geo\\time"].unique().tolist()
        countries = [c for c in countries_df_1 if c in set(countries)]

        if "table-upload" in changed_items or "demo-button" in changed_items:
            upload_children["props"]["children"] = html.Div([filename])

        radio_visibility = {"display": "block"}
        show_compare_dropdown = {"display": "block"}

        return (
            filtered_cols,
            df_2,
            upload_children,
            filtered_cols[0],
            countries,
            countries[0],
            radio_visibility,
            show_compare_dropdown,
            filtered_cols,
            False,
            None,
        )
    elif (
        (file is not None or "demo-button" in changed_items)
        and geo_dropdown_2 is None
        and not data
        and delimiter_dropdown_2
    ):
        if file:
            columns = get_available_columns(file, separator=delimiter_dropdown_2)
        elif "demo-button" in changed_items:
            filename = "bip_europa.tsv"
            df_url = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/tec00001.tsv.gz"

            content = urllib.request.urlopen(df_url).read()
            content = gzip.decompress(content)

            columns = get_available_columns(content, upload_file=False, separator="\t")
            file = base64.b64encode(content).decode("utf-8")

        upload_children["props"]["children"] = html.Div([filename])

        return (
            no_update,
            None,
            upload_children,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            columns,
            False,
            file,
        )

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("category-dropdown", "options"),
    Output("category-dropdown", "value"),
    Input("columns-dropdown", "value"),
    Input("dataset", "data"),
)
def update_sub_category_dropdown(selected_column: str, dataset: str) -> tuple:
    """Updates the sub category dropdown based on the selected column

    Args:
        selected_column (str): current column selected in the dropdown
        data (str): Dataset

    Raises:
        exceptions.PreventUpdate: if no data is available and no column selected

    Returns:
        tuple: sub categories and autoselect first sub category
    """
    if dataset and selected_column != "none":
        sub_categories = get_selected_category_column(dataset, selected_column)
        return sub_categories, sub_categories[0]

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("category-dropdown-2", "options"),
    Output("category-dropdown-2", "value"),
    Input("columns-dropdown-2", "value"),
    Input("dataset-2", "data"),
)
def update_second_sub_category_dropdown(selected_column: str, dataset: str) -> tuple:
    """Updates the second sub category dropdown based on the selected column
    in the second dataset

    Args:
        selected_column (str): current column selected in the dropdown
        data (str): Dataset

    Raises:
        exceptions.PreventUpdate: if no data is available and no column selected

    Returns:
        tuple: sub categories and autoselect first sub category
    """
    if dataset and selected_column != "none":
        sub_categories = get_selected_category_column(dataset, selected_column)
        return sub_categories, sub_categories[0]

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
    Input("geo-dropdown-1", "value"),
    Input("geo-dropdown-2", "value"),
)
def update_year_dropdown_stats(
    dataset: str,
    dataset_2: str,
    selected_dataset: str,
    geo_dropdown_1: str,
    geo_dropdown_2: str,
) -> tuple:
    """Fills dropdown in stats section with available years in the selected dataset

    Args:
        data (str): First dataset (JSON)
        data_2 (str): Second dataset (JSON)
        selected_dataset (str): value of the selected dataset

    Raises:
        exceptions.PreventUpdate: prevents update if no dataset is available and no dataset is selected

    Returns:
        tuple: available years, first year value, available countries, first country value, available years, first year value
    """

    if (
        (dataset and geo_dropdown_1) or (dataset_2 and geo_dropdown_2)
    ) and selected_dataset:

        datasets = {
            "Dataset 1": [dataset, geo_dropdown_1],
            "Dataset 2": [dataset_2, geo_dropdown_2],
        }

        df = pd.read_json(datasets[selected_dataset][0])

        year_re = re.compile("[1-2][0-9]{3}")

        year_columns = [
            column for column in df.columns.to_list() if year_re.match(column)
        ]

        return (
            year_columns,
            year_columns[0],
            df[datasets[selected_dataset][1]].unique(),
            df[datasets[selected_dataset][1]].unique()[0],
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
def update_table_content(
    dataset_1: str, dataset_2: str, selected_dataset: str
) -> pd.DataFrame:
    """Fills table section with data from the selected dataset

    Args:
        dataset_1 (str): First dataset
        dataset_2 (str): Second dataset
        selected_dataset (str): value of selectd dataset

    Raises:
        exceptions.PreventUpdate: update prevented if no dataset is available

    Returns:
        pd.DataFrame: Dataframe of selected dataset
    """

    if (dataset_1 and selected_dataset == "Dataset 1") or (
        dataset_2 and selected_dataset == "Dataset 2"
    ):
        datasets = {"Dataset 1": dataset_1, "Dataset 2": dataset_2}

        df = pd.read_json(datasets[selected_dataset]).round(2).to_dict("records")

        return df
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
    selected_dataset: str,
    avg_stat_children: list,
    max_stat_children: list,
    min_stat_children: list,
    growth_stat_children: list,
    year_dropdown_stats: str,
    country_dropdown_stats: str,
    geo_dropdown_1: str,
    geo_dropdown_2: str,
    dataset: str,
    dataset_2: str,
    selected_column: str,
    selected_subcategory: str,
    selected_column_2: str,
    selected_sub_category_2: str,
) -> tuple:
    """Compute and display mean, max, min and growth value (per country) for selected dataset

    Args:
        selected_dataset (str): selected dataset
        avg_stat_children (list): container which display mean stat
        max_stat_children (list): container which displays max stat
        min_stat_children (list): container which displays min stat
        growth_stat_children (list): container which display growth stat per country
        year_dropdown_stats (str): year selector dropdown in stats section
        country_dropdown_stats (str): country selector in growth rate container
        geo_dropdown_1 (str): "geo" colum selector for first dataset
        geo_dropdown_2 (str): "geo" colum selector for second dataset
        dataset (str): first dataset
        dataset_2 (str): second dataset
        selected_column (str): selected column in first dataset
        selected_subcategory (str): selected subcategory in first dataset
        selected_column_2 (str): selected column in second dataset
        selected_sub_category_2 (str): selected subcategory in second dataset

    Raises:
        exceptions.PreventUpdate: prevents update when dataset, column selection, subcategory selection and "geo" column selection are empty

    Returns:
        tuple: mean stat container, max stat container, min stat container, growth stat container
    """

    if (
        dataset
        and selected_column
        and selected_subcategory != "none"
        and (geo_dropdown_1 or geo_dropdown_2)
    ):
        datasets = {
            "Dataset 1": [
                dataset,
                selected_column,
                selected_subcategory,
                geo_dropdown_1,
            ],
            "Dataset 2": [
                dataset_2,
                selected_column_2,
                selected_sub_category_2,
                geo_dropdown_2,
            ],
        }

        df = pd.read_json(datasets[selected_dataset][0])
        filtered_df = df[
            df[datasets[selected_dataset][2]] == datasets[selected_dataset][1]
        ]

        year_column_i = filtered_df.columns.get_loc(year_dropdown_stats)

        avg_stat_children.clear()

        avg_stat_children.append(
            "Mean \n" + str(round(filtered_df.iloc[:, year_column_i].mean(axis=0), 2))
        )

        max_val_country = filtered_df.iloc[:, year_column_i].max()
        i_max = np.where(filtered_df.iloc[:, year_column_i] == max_val_country)[0]

        max_country = str(filtered_df.iloc[i_max, 1].values[0])

        min_val_country = (
            filtered_df[filtered_df.iloc[:, year_column_i] >= 0.01]
            .iloc[:, year_column_i]
            .min()
        )
        i_min = np.where(filtered_df.iloc[:, year_column_i] == min_val_country)[0]

        min_country = str(filtered_df.iloc[i_min, 1].values[0])

        i_country = np.where(
            filtered_df[datasets[selected_dataset][3]] == country_dropdown_stats
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

        max_stat_children.clear()
        max_stat_children.append(
            "max:\n"
            + str(round(filtered_df.iloc[i_max, year_column_i].values[0], 2))
            + " - "
            + max_country
        )
        min_stat_children.clear()
        min_stat_children.append(
            "min: \n"
            + str(round(filtered_df.iloc[i_min, year_column_i].values[0], 2))
            + " - "
            + min_country
        )
        growth_stat_children.clear()
        growth_stat_children.append("Growth rate:\n" + growth_rate)

        return (
            avg_stat_children,
            max_stat_children,
            min_stat_children,
            growth_stat_children,
        )
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
    selected_sub_category: str,
    selected_column: str,
    dataset: str,
    selected_sub_category_2: str,
    selected_column_2: str,
    dataset_2: str,
    timeline_children: list,
    selected_dataset: str,
    geo_dropdown_1: str,
    geo_dropdown_2: str,
) -> list:
    """Draws a line plot with the selected data specified in the dropdowns

    Args:
        selected_sub_category (str): first selected sub-category
        selected_column (str): first selected column
        dataset (str): first dataset
        selected_sub_category_2 (str): second selected sub-category
        selected_column_2 (str): second selected column
        dataset_2 (str): second dataset
        timeline_children (list): container for timeline section
        selected_dataset (str): value of selected dataset
        geo_dropdown_1 (str): "geo" column selector for first dataset
        geo_dropdown_2 (str): "geo" column selector for second datset

    Raises:
        exceptions.PreventUpdate: _description_

    Returns:
        list: container with line plot
    """

    if (
        dataset
        and selected_sub_category
        and selected_column != "none"
        and (geo_dropdown_1 or geo_dropdown_2)
    ):

        datasets = {
            "Dataset 1": (
                dataset,
                selected_sub_category,
                selected_column,
                geo_dropdown_1,
            ),
            "Dataset 2": (
                dataset_2,
                selected_sub_category_2,
                selected_column_2,
                geo_dropdown_2,
            ),
        }

        df = pd.read_json(datasets[selected_dataset][0])
        filtered_df = df[
            df[datasets[selected_dataset][2]] == datasets[selected_dataset][1]
        ]

        fig = create_multi_line_plot(filtered_df, geo_col=datasets[selected_dataset][3])

        timeline_children.clear()

        timeline_children.append(dcc.Graph(figure=fig))

        return timeline_children

    elif dataset and selected_column == "none":

        df = pd.read_json(dataset)
        fig = create_multi_line_plot(df)

        timeline_children.clear()

        timeline_children.append(dcc.Graph(figure=fig))

        return timeline_children

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
    selected_sub_category: str,
    selected_column: str,
    dataset: str,
    map_children: list,
    selected_sub_category_2: str,
    selected_column_2: str,
    dataset_2: str,
    geo_dropdown_2: str,
    geo_dropdown_1: str,
    selected_year_map: str,
    selected_dataset: str,
) -> list:
    """Displays choropleth mapbox in countries section

    Args:
        selected_sub_category (str): selected sub-category in first dataset
        selected_column (str): selected column in first dataset
        dataset (str): first dataset
        map_children (list): container that holds the mapbox
        selected_sub_category_2 (str): selected sub-category in second dataset
        selected_column_2 (str): selected column in second dataset
        dataset_2 (str): second dataset
        geo_dropdown_2 (str): first "geo" dropdown selection
        geo_dropdown_1 (str): second "geo" dropdown selection
        selected_year_map (str): selected year in countries section
        selected_dataset (str): value of selected dataset

    Raises:
        exceptions.PreventUpdate: update prevented unless atleast one dataset is uploaded

    Returns:
        list: container with choropleth mapbox
    """

    if (
        dataset
        and selected_sub_category
        and selected_column != "none"
        and geo_dropdown_1
    ) or (
        dataset_2
        and selected_sub_category_2
        and selected_column_2 != "none"
        and geo_dropdown_2
    ):

        datasets = {
            "Dataset 1": (
                dataset,
                selected_sub_category,
                selected_column,
                geo_dropdown_1,
            ),
            "Dataset 2": (
                dataset_2,
                selected_sub_category_2,
                selected_column_2,
                geo_dropdown_2,
            ),
        }

        df = pd.read_json(datasets[selected_dataset][0])

        filtered_df = DigitalTwinTimeSeries(
            df=df, geo_col=datasets[selected_dataset][3]
        )
        filtered_df = filtered_df.melt_data(
            category_column=datasets[selected_dataset][2]
        )

        filtered_df = filtered_df[datasets[selected_dataset][1]]

        fig = create_choropleth_plot(filtered_df, year=selected_year_map)

        if map_children:
            map_children.clear()

        map_children.append(dcc.Graph(figure=fig))

        return map_children

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
    selected_sub_category: str,
    selected_column: str,
    dataset: str,
    selected_sub_category_2: str,
    selected_column_2: str,
    selected_country: str,
    dataset_2: str,
    comparison_children: str,
    geo_dropdown_2: str,
    geo_dropdown_1: str,
) -> list:
    """Creates a line plot with two subplots (one for each dataset respectively)

    Args:
        selected_sub_category (str): selected sub-category in first dataset
        selected_column (str): selected column in first dataset
        dataset (str): first dataset
        selected_sub_category_2 (str): selected sub-category in second dataset
        selected_column_2 (str): selected column in second dataset
        selected_country (str): selected country in comparison section
        dataset_2 (str): second dataset
        comparison_children (str): container that holds the line plot
        geo_dropdown_2 (str): value of "geo" of first dataset
        geo_dropdown_1 (str): value of "geo" in second dataset

    Raises:
        exceptions.PreventUpdate: update prevented until two datasets are loaded

    Returns:
        list: container with line plots
    """

    if (
        selected_country
        and selected_sub_category_2
        and selected_sub_category
        and dataset
        and dataset_2
        and geo_dropdown_1
        and geo_dropdown_2
    ):
        df = pd.read_json(dataset)
        df_2 = pd.read_json(dataset_2)

        filtered_dfs = []
        rows = []
        selected_values = (
            (selected_column, selected_sub_category, geo_dropdown_1),
            (selected_column_2, selected_sub_category_2, geo_dropdown_2),
        )

        for i, df in enumerate((df, df_2)):
            filtered_df = df[
                df[selected_values[i][0]] == selected_values[i][1]
            ].reset_index(drop=True)

            row = filtered_df[
                filtered_df[selected_values[i][2]] == selected_country
            ].index[0]

            filtered_dfs.append(filtered_df)
            rows.append(row)

        i_1, i_2 = find_column_intersection_indeces(
            (filtered_dfs[0].columns.tolist(), filtered_dfs[1].columns.tolist())
        )

        fig = create_two_line_plot(
            filtered_dfs[0],
            filtered_dfs[1],
            rows[0],
            rows[1],
            i_1,
            i_2,
            selected_sub_category,
            selected_sub_category_2,
        )

        comparison_children.clear()

        comparison_children.append(dcc.Graph(figure=fig))

        return comparison_children
    else:
        raise exceptions.PreventUpdate


if __name__ == "__main__":
    app.run_server(debug=True)
