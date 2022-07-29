import gzip
import json
import base64
import urllib
import dash_daq as daq
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
                                        dcc.Dropdown(
                                            [",", ";", "\\t", "space"],
                                            placeholder="Sep",
                                            id="delimiter-dropdown-1",
                                            clearable=False,
                                            style={
                                                "margin-top": "5px",
                                                "margin-left": "0px",
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                                "font-size": "10px",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex"},
                                ),
                                html.Div(
                                    "Select geo column",
                                    style={"margin-left": "20px"},
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
                                                "width": "80%",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Reshape",
                                            style={
                                                "margin-top": "15px",
                                                "font-weight": "bold",
                                                "margin-left": "20px",
                                            },
                                        ),
                                        daq.BooleanSwitch(
                                            id="reshape-switch-1",
                                            style={"margin-top": "10px"},
                                        ),
                                    ],
                                    style={"display": "flex"},
                                ),
                                html.Div(
                                    "Select time column",
                                    style={
                                        "margin-top": "15px",
                                        "font-weight": "bold",
                                        "margin-left": "20px",
                                    },
                                ),
                                dcc.Dropdown(
                                    ["none"],
                                    placeholder="No values found",
                                    clearable=False,
                                    id="time-dropdown-1",
                                    style={
                                        "margin-top": "5px",
                                        "margin-left": "5px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                        "width": "80%",
                                    },
                                ),
                                html.Div(
                                    "Select feature",
                                    style={
                                        "margin-top": "15px",
                                        "font-weight": "bold",
                                        "margin-left": "20px",
                                    },
                                ),
                                dcc.Dropdown(
                                    ["none"],
                                    placeholder="No values found",
                                    clearable=False,
                                    id="feature-dropdown-1",
                                    style={
                                        "margin-top": "5px",
                                        "margin-left": "5px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                        "width": "80%",
                                    },
                                ),
                                dcc.Store(id="dataset"),
                            ],
                            style={
                                "display": "inline-block",
                                "min-width": "170px",
                            },
                        ),
                        html.Div(
                            [
                                dcc.ConfirmDialog(
                                    id="dataset-2-fail",
                                    message="There was an error while processing your data. Please make sure it comes in one of the supported formats.",
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
                                        dcc.Dropdown(
                                            [",", ";", "\\t", "space"],
                                            placeholder="Sep",
                                            id="delimiter-dropdown-2",
                                            clearable=False,
                                            style={
                                                "margin-top": "5px",
                                                "margin-left": "0px",
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                                "font-size": "10px",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex"},
                                ),
                                html.Div(
                                    "Select geo column", style={"margin-left": "20px"}
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
                                                "width": "80%",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Reshape",
                                            style={
                                                "margin-top": "15px",
                                                "font-weight": "bold",
                                                "margin-left": "20px",
                                            },
                                        ),
                                        daq.BooleanSwitch(
                                            id="reshape-switch-2",
                                            style={"margin-top": "10px"},
                                        ),
                                    ],
                                    style={"display": "flex"},
                                ),
                                html.Div(
                                    "Set time column",
                                    style={
                                        "margin-top": "15px",
                                        "font-weight": "bold",
                                        "margin-left": "20px",
                                    },
                                ),
                                dcc.Dropdown(
                                    ["none"],
                                    placeholder="No values found",
                                    clearable=False,
                                    id="time-dropdown-2",
                                    style={
                                        "margin-top": "5px",
                                        "margin-left": "5px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                        "width": "80%",
                                    },
                                ),
                                html.Div(
                                    "Select feature",
                                    style={
                                        "margin-top": "15px",
                                        "font-weight": "bold",
                                        "margin-left": "20px",
                                    },
                                ),
                                dcc.Dropdown(
                                    ["none"],
                                    placeholder="No values found",
                                    clearable=False,
                                    id="feature-dropdown-2",
                                    style={
                                        "margin-top": "5px",
                                        "margin-left": "5px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                        "width": "80%",
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
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Toggle displayed data",
                                                    style={
                                                        "margin": "10px",
                                                        "font-weight": "bold",
                                                    },
                                                ),
                                                dcc.RadioItems(
                                                    ["Dataset 1", "Dataset 2"],
                                                    "Dataset 1",
                                                    id="data-selector",
                                                    inline=False,
                                                    style={"display": "flex"},
                                                ),
                                            ]
                                        ),
                                        html.Button(
                                            "Demo",
                                            id="demo-button",
                                            n_clicks=0,
                                            style={
                                                "margin-right": "20px",
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
                                # "margin-left": "10px",
                            },
                        ),
                    ],
                    style={
                        "backgroundColor": "#111111",
                        "width": "39%",
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
                        "width": "60%",
                        "max-height": "318px",
                    },
                ),
            ],
            style={
                "backgroundColor": "#232323",
                "height": "440px",
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
    Output("time-dropdown-1", "options"),
    Output("dataset", "data"),
    Output("table-upload", "children"),
    Output("time-dropdown-1", "value"),
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
    Input("reshape-switch-1", "on"),
    Input("dataset", "data"),
)
def preprocess_dataset(
    file: str,
    filename: str,
    upload_children: list,
    demo_button_clicks: int,
    geo_dropdown_1: str,
    delimiter_dropdown_1: str,
    reshape_switch_status: bool,
    data: str,
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

    if delimiter_dropdown_1 == "\\t":
        delimiter_dropdown_1 = "\t"

    if (
        (file is not None or "demo-button" in changed_items)
        and geo_dropdown_1 is not None
        and delimiter_dropdown_1
    ):
        if file:
            try:
                content = file.split(",")
                df, filtered_cols = parse_dataset(
                    content[-1],
                    separator=delimiter_dropdown_1,
                    geo_col=geo_dropdown_1,
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
        else:
            filtered_cols.insert(0, "None")

        show_second_file_upload = {"display": "inline-block"}

        return (
            filtered_cols,
            df,
            upload_children,
            no_update,
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
            columns.insert(0, "None")
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
    elif data and reshape_switch_status:
        df = pd.read_json(data)
        df = DigitalTwinTimeSeries(df=df, geo_col=geo_dropdown_1)
        df = df.reshape_wide_to_long("age")

        return (
            df.columns.to_list(),
            df.to_json(),
            no_update,
            no_update,
            no_update,
            df.columns.to_list(),
            False,
            None,
        )

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("time-dropdown-2", "options"),
    Output("dataset-2", "data"),
    Output("table-upload-2", "children"),
    Output("time-dropdown-2", "value"),
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
    Input("reshape-switch-2", "on"),
    Input("dataset-2", "data"),
    Input("geo-dropdown-1", "value"),
)
def preprocess_second_dataset(
    file: str,
    filename: str,
    upload_children: list,
    data: str,
    demo_button_clicks: int,
    geo_dropdown_2: str,
    delimiter_dropdown_2: str,
    reshape_switch_status_2: bool,
    data_2: str,
    geo_dropdown_1: str,
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
    if delimiter_dropdown_2 == "\\t":
        delimiter_dropdown_2 = "\t"

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

        if geo_dropdown_1 != "None":
            countries_df_1 = pd.read_json(data)[geo_dropdown_1].unique().tolist()
            countries = [c for c in countries_df_1 if c in set(countries)]

        else:
            countries = ["None"]

        if "table-upload" in changed_items or "demo-button" in changed_items:
            upload_children["props"]["children"] = html.Div([filename])

        radio_visibility = {"display": "block"}
        show_compare_dropdown = {"display": "block"}

        return (
            filtered_cols,
            df_2,
            upload_children,
            no_update,
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
        and not data_2
        and geo_dropdown_2 is None
        and delimiter_dropdown_2
        and "geo-dropdown-1" not in changed_items
        and "dataset" not in changed_items
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
    elif data_2 and reshape_switch_status_2:
        df = pd.read_json(data_2)
        df = DigitalTwinTimeSeries(df=df, geo_col=geo_dropdown_2)
        df = df.reshape_wide_to_long("unit")

        return (
            df.columns.to_list(),
            df.to_json(),
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            df.columns.to_list(),
            False,
            None,
        )

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("feature-dropdown-1", "options"),
    Output("feature-dropdown-1", "value"),
    Input("time-dropdown-1", "value"),
    Input("dataset", "data"),
    Input("geo-dropdown-1", "value"),
)
def update_sub_category_dropdown(
    time_dropdown_1: str, dataset: str, geo_dropdown_1: str
) -> tuple:
    """Updates the sub category dropdown based on the selected column

    Args:
        selected_column (str): current column selected in the dropdown
        data (str): Dataset

    Raises:
        exceptions.PreventUpdate: if no data is available and no column selected

    Returns:
        tuple: sub categories and autoselect first sub category
    """
    if dataset and time_dropdown_1:
        df = pd.read_json(dataset)
        # if geo_dropdown_1 != "None":
        #    df = df.drop(columns=[time_dropdown_1, geo_dropdown_1])

        return df.columns.to_list(), no_update

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("feature-dropdown-2", "options"),
    Output("feature-dropdown-2", "value"),
    Input("time-dropdown-2", "value"),
    Input("dataset-2", "data"),
    Input("geo-dropdown-2", "value"),
)
def update_second_sub_category_dropdown(
    time_dropdown_2: str, dataset: str, geo_dropdown_2: str
) -> tuple:
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
    if dataset and time_dropdown_2:
        df = pd.read_json(dataset)
        df = df.drop(columns=[time_dropdown_2, geo_dropdown_2])
        return df.columns.to_list(), no_update

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
    Input("time-dropdown-1", "value"),
    Input("time-dropdown-2", "value"),
)
def update_year_dropdown_stats(
    dataset: str,
    dataset_2: str,
    selected_dataset: str,
    geo_dropdown_1: str,
    geo_dropdown_2: str,
    time_dropdown_1: str,
    time_dropdown_2: str,
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
        dataset
        and geo_dropdown_1
        and time_dropdown_1
        and selected_dataset == "Dataset 1"
    ) or (
        dataset_2
        and geo_dropdown_2
        and time_dropdown_2
        and selected_dataset == "Dataset 2"
    ):

        datasets = {
            "Dataset 1": (dataset, geo_dropdown_1, time_dropdown_1),
            "Dataset 2": (dataset_2, geo_dropdown_2, time_dropdown_2),
        }

        time_column = datasets[selected_dataset][2]
        geo_column = datasets[selected_dataset][1]

        df = pd.read_json(datasets[selected_dataset][0])

        return (
            df[time_column].unique(),
            df[time_column].unique()[0],
            df[geo_column].unique(),
            df[geo_column].unique()[0],
            df[time_column].unique(),
            df[time_column].unique()[0],
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
    Input("feature-dropdown-1", "value"),
    Input("time-dropdown-1", "value"),
    Input("feature-dropdown-2", "value"),
    Input("time-dropdown-2", "value"),
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
    feature_dropdown_1: str,
    time_dropdown_1: str,
    feature_dropdown_2: str,
    time_dropdown_2: str,
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
        and feature_dropdown_1
        and time_dropdown_1
        and geo_dropdown_1
        and selected_dataset == "Dataset 1"
    ) or (
        dataset_2
        and feature_dropdown_2
        and time_dropdown_2
        and geo_dropdown_2
        and selected_dataset == "Dataset 2"
    ):
        datasets = {
            "Dataset 1": [
                dataset,
                feature_dropdown_1,
                time_dropdown_1,
                geo_dropdown_1,
            ],
            "Dataset 2": [
                dataset_2,
                feature_dropdown_2,
                time_dropdown_2,
                geo_dropdown_2,
            ],
        }

        df = pd.read_json(datasets[selected_dataset][0])

        time_column = datasets[selected_dataset][2]
        year = year_dropdown_stats
        geo_column = datasets[selected_dataset][3]
        feature_column = datasets[selected_dataset][1]

        filtered_df = df[df[time_column] == year][[geo_column, feature_column]]

        filtered_df_by_country = df[
            (df[geo_column] == country_dropdown_stats)
            & (df[time_column] >= year_dropdown_stats)
        ]

        avg_stat_children.clear()

        avg_stat_children.append(
            "Mean \n"
            + str(round(filtered_df[datasets[selected_dataset][1]].mean(axis=0), 2))
        )

        start_value = filtered_df_by_country[feature_column].values[0]
        end_value = filtered_df_by_country[feature_column].values[-1]

        growth_rate = ((end_value - start_value) / end_value) * 100

        max_stat_children.clear()

        max_country = filtered_df.loc[
            filtered_df[datasets[selected_dataset][1]].idxmax()
        ][datasets[selected_dataset][3]]

        max_stat_children.append(
            "max:\n"
            + str(round(filtered_df[datasets[selected_dataset][1]].max(), 2))
            + " - "
            + max_country
        )
        min_stat_children.clear()

        min_country = filtered_df.loc[
            filtered_df[datasets[selected_dataset][1]].idxmin()
        ][datasets[selected_dataset][3]]
        min_stat_children.append(
            "min: \n"
            + str(round(filtered_df[datasets[selected_dataset][1]].min(), 2))
            + " - "
            + min_country
        )
        growth_stat_children.clear()
        growth_stat_children.append("Growth rate:\n" + str(round(growth_rate, 2)))

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
    Input("feature-dropdown-1", "value"),
    Input("time-dropdown-1", "value"),
    Input("dataset", "data"),
    Input("feature-dropdown-2", "value"),
    Input("time-dropdown-2", "value"),
    Input("dataset-2", "data"),
    State("line-div", "children"),
    Input("data-selector", "value"),
    Input("geo-dropdown-1", "value"),
    Input("geo-dropdown-2", "value"),
)
def update_line_plot(
    feature_dropdown_1: str,
    time_dropdown_1: str,
    dataset: str,
    feature_dropdown_2: str,
    time_dropdown_2: str,
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
        and feature_dropdown_1
        and time_dropdown_1
        and geo_dropdown_1
        and selected_dataset == "Dataset 1"
    ) or (
        dataset_2
        and feature_dropdown_2
        and time_dropdown_2
        and geo_dropdown_2
        and selected_dataset == "Dataset 2"
    ):

        datasets = {
            "Dataset 1": (
                dataset,
                feature_dropdown_1,
                time_dropdown_1,
                geo_dropdown_1,
            ),
            "Dataset 2": (
                dataset_2,
                feature_dropdown_2,
                time_dropdown_2,
                geo_dropdown_2,
            ),
        }

        df = pd.read_json(datasets[selected_dataset][0])

        time_column = datasets[selected_dataset][2]
        feature_column = datasets[selected_dataset][1]
        geo_column = datasets[selected_dataset][3]

        fig = create_multi_line_plot(
            df,
            geo_col=geo_column,
            time_column=time_column,
            feature_column=feature_column,
        )

        timeline_children.clear()

        timeline_children.append(dcc.Graph(figure=fig))

        return timeline_children

    elif dataset and time_dropdown_1 == "none":

        df = pd.read_json(dataset)
        fig = create_multi_line_plot(df)

        timeline_children.clear()

        timeline_children.append(dcc.Graph(figure=fig))

        return timeline_children

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("map-div", "children"),
    Input("feature-dropdown-1", "value"),
    Input("time-dropdown-1", "value"),
    Input("dataset", "data"),
    State("map-div", "children"),
    Input("feature-dropdown-2", "value"),
    Input("time-dropdown-2", "value"),
    Input("dataset-2", "data"),
    Input("geo-dropdown-2", "value"),
    Input("geo-dropdown-1", "value"),
    Input("year-dropdown-map", "value"),
    Input("data-selector", "value"),
)
def update_choropleth(
    feature_dropdown_1: str,
    time_dropdown_1: str,
    dataset: str,
    map_children: list,
    feature_dropdown_2: str,
    time_dropdown_2: str,
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
        and feature_dropdown_1
        and time_dropdown_1
        and geo_dropdown_1
        and selected_dataset == "Dataset 1"
    ) or (
        dataset_2
        and feature_dropdown_2
        and time_dropdown_2
        and geo_dropdown_2
        and selected_dataset == "Dataset 2"
    ):

        datasets = {
            "Dataset 1": (
                dataset,
                feature_dropdown_1,
                time_dropdown_1,
                geo_dropdown_1,
            ),
            "Dataset 2": (
                dataset_2,
                feature_dropdown_2,
                time_dropdown_2,
                geo_dropdown_2,
            ),
        }

        geo_column = datasets[selected_dataset][3]
        feature_column = datasets[selected_dataset][1]
        time_column = datasets[selected_dataset][2]

        df = pd.read_json(datasets[selected_dataset][0])

        filtered_df = df[df[time_column] == selected_year_map]

        fig = create_choropleth_plot(
            filtered_df, geo_column=geo_column, feature_column=feature_column
        )

        if map_children:
            map_children.clear()

        map_children.append(dcc.Graph(figure=fig))

        return map_children

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("max_country-comparison-div", "children"),
    Input("feature-dropdown-1", "value"),
    Input("time-dropdown-1", "value"),
    Input("dataset", "data"),
    Input("feature-dropdown-2", "value"),
    Input("time-dropdown-2", "value"),
    Input("country-dropdown", "value"),
    Input("dataset-2", "data"),
    State("max_country-comparison-div", "children"),
    Input("geo-dropdown-2", "value"),
    Input("geo-dropdown-1", "value"),
)
def update_max_country_compare(
    feature_dropdown_1: str,
    time_dropdown_1: str,
    dataset: str,
    feature_dropdown_2: str,
    time_dropdown_2: str,
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
        and feature_dropdown_2
        and feature_dropdown_1
        and dataset
        and dataset_2
        and geo_dropdown_1
        and geo_dropdown_2
    ):
        df = pd.read_json(dataset)
        df_2 = pd.read_json(dataset_2)

        filtered_dfs = []
        selected_values = (
            (time_dropdown_1, feature_dropdown_1, geo_dropdown_1),
            (time_dropdown_2, feature_dropdown_2, geo_dropdown_2),
        )

        for i, df in enumerate((df, df_2)):
            geo_column = selected_values[i][2]

            if selected_country != "None":
                filtered_df = df[df[geo_column] == selected_country]
            else:
                filtered_df = df

            filtered_dfs.append(filtered_df)

        fig = create_two_line_plot(
            filtered_dfs,
            (feature_dropdown_1, feature_dropdown_2),
            (time_dropdown_1, time_dropdown_2),
        )

        comparison_children.clear()

        comparison_children.append(dcc.Graph(figure=fig))

        return comparison_children
    else:
        raise exceptions.PreventUpdate


if __name__ == "__main__":
    app.run_server(debug=True)
