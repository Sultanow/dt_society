import dash_daq as daq
from dash import (
    Dash,
    dcc,
    html,
    Input,
    Output,
    exceptions,
    State,
    dash_table,
    callback_context,
    no_update,
)
import pandas as pd

from helpers.plots import (
    create_multi_line_plot,
    create_choropleth_plot,
    create_choropleth_slider_plot,
    create_two_line_plot,
    create_correlation_heatmap,
    create_forecast_plot,
    create_multivariate_forecast,
    create_var_forecast_plot,
)
from helpers.models import (
    prophet_fit_and_predict,
    fit_and_predict,
    prophet_fit_and_predict_multi,
    var_fit_and_predict,
    hw_es_fit_and_predict,
)
from helpers.layout import (
    preprocess_dataset,
    get_year_and_country_options_stats,
    get_time_marks,
    compute_stats,
    compute_growth_rate,
    export_settings,
)

from preprocessing.parse import merge_dataframes


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
                                                "margin": "auto",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Span(
                                                    "help",
                                                    className="material-symbols-outlined",
                                                ),
                                                html.Span(
                                                    """File format: .csv, .tsv \n 
                                                    Geo column: column that contains either country names or ISO codes \n
                                                    Reshape: pivots the dataset from a wide to long format (adds new columns for unique values of selected column, if there is no additional identifier select "None") \n
                                                    Time column: column that contains time data / timestamps (represents x-axis in figures)\n
                                                    Feature: column that contains the feature of interest (represents y-axis in figures)\n
                                                    Preset: upload/download a preset file that contains pre-selected column values""",
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
                                    message="An error occured while processing your data. Please make sure that the data is in the correct format and select the appropriate separator.",
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
                                                "color": "white",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Select geo column",
                                            style={
                                                "width": "200px",
                                                "textAlign": "center",
                                                "margin-bottom": "20px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            ["none"],
                                            placeholder="No values found",
                                            clearable=False,
                                            id="geo-dropdown-1",
                                            style={
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                            },
                                        ),
                                    ],
                                    style={"margin-left": "20px", "padding": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Reshape",
                                                    style={
                                                        "font-weight": "bold",
                                                    },
                                                ),
                                                daq.BooleanSwitch(
                                                    id="reshape-switch-1",
                                                    style={
                                                        "margin-bottom": "10px",
                                                        "margin-left": "20px",
                                                    },
                                                ),
                                            ],
                                            style={"display": "flex"},
                                        ),
                                        dcc.Dropdown(
                                            ["none"],
                                            placeholder="No values found",
                                            clearable=False,
                                            id="reshape-dropdown-1",
                                            style={
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                            },
                                        ),
                                    ],
                                    style={"margin-left": "20px", "padding": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Select time column",
                                            style={
                                                "font-weight": "bold",
                                                "width": "200px",
                                                "margin-bottom": "20px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            ["none"],
                                            placeholder="No values found",
                                            clearable=False,
                                            id="time-dropdown-1",
                                            style={
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                            },
                                        ),
                                    ],
                                    style={"margin-left": "20px", "padding": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Select feature",
                                            style={
                                                "font-weight": "bold",
                                                "width": "200px",
                                                "margin-bottom": "20px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            ["none"],
                                            placeholder="No values found",
                                            clearable=False,
                                            id="feature-dropdown-1",
                                            style={
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                            },
                                        ),
                                        dcc.Loading(
                                            children=[
                                                dcc.Store(id="dataset"),
                                            ],
                                            fullscreen=True,
                                            style={
                                                "backgroundColor": "rgba(8,8,8,0.8)"
                                            },
                                        ),
                                    ],
                                    style={"margin-left": "20px", "padding": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Preset",
                                            style={
                                                "font-weight": "bold",
                                                "width": "200px",
                                                "margin-bottom": "20px",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                dcc.Upload(
                                                    id="preset-upload-1",
                                                    children=html.Button(
                                                        "Import",
                                                        id="preset-up-button-1",
                                                        n_clicks=0,
                                                        style={
                                                            "border-color": "#5c6cfa",
                                                            "width": "120px",
                                                            "margin-right": "4px",
                                                        },
                                                    ),
                                                ),
                                                dcc.Download(id="preset-download-1"),
                                                html.Button(
                                                    "Export",
                                                    id="preset-down-button-1",
                                                    n_clicks=0,
                                                    style={
                                                        "border-color": "#5c6cfa",
                                                        "width": "120px",
                                                    },
                                                ),
                                            ],
                                            style={"display": "flex"},
                                        ),
                                    ],
                                    style={"margin-left": "20px", "padding": "10px"},
                                ),
                            ],
                            style={
                                "display": "flex",
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
                                                    html.A("Select files"),
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
                                    [
                                        html.Div(
                                            "Select geo column",
                                            style={
                                                "margin-bottom": "20px",
                                                "width": "200px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            ["none"],
                                            placeholder="No values found",
                                            clearable=False,
                                            id="geo-dropdown-2",
                                            style={
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                            },
                                        ),
                                    ],
                                    style={"margin-left": "20px", "padding": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Reshape",
                                                    style={
                                                        "font-weight": "bold",
                                                    },
                                                ),
                                                daq.BooleanSwitch(
                                                    id="reshape-switch-2",
                                                    style={
                                                        "margin-bottom": "10px",
                                                        "margin-left": "20px",
                                                    },
                                                ),
                                            ],
                                            style={"display": "flex"},
                                        ),
                                        dcc.Dropdown(
                                            ["none"],
                                            placeholder="No values found",
                                            clearable=False,
                                            id="reshape-dropdown-2",
                                            style={
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                            },
                                        ),
                                    ],
                                    style={"margin-left": "20px", "padding": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Set time column",
                                            style={
                                                "font-weight": "bold",
                                                "width": "200px",
                                                "margin-bottom": "20px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            ["none"],
                                            placeholder="No values found",
                                            clearable=False,
                                            id="time-dropdown-2",
                                            style={
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                            },
                                        ),
                                    ],
                                    style={"margin-left": "20px", "padding": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Select feature",
                                            style={
                                                "font-weight": "bold",
                                                "width": "200px",
                                                "margin-bottom": "20px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            ["none"],
                                            placeholder="No values found",
                                            clearable=False,
                                            id="feature-dropdown-2",
                                            style={
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                            },
                                        ),
                                        dcc.Loading(
                                            children=[
                                                dcc.Store(id="dataset-2"),
                                            ],
                                            fullscreen=True,
                                            style={
                                                "backgroundColor": "rgba(8,8,8,0.8)"
                                            },
                                        ),
                                    ],
                                    style={"margin-left": "20px", "padding": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Preset",
                                            style={
                                                "font-weight": "bold",
                                                "width": "200px",
                                                "margin-bottom": "20px",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                dcc.Upload(
                                                    id="preset-upload-2",
                                                    children=html.Button(
                                                        "Import",
                                                        id="preset-up-button-2",
                                                        n_clicks=0,
                                                        style={
                                                            "border-color": "#5c6cfa",
                                                            "width": "120px",
                                                            "margin-right": "4px",
                                                        },
                                                    ),
                                                ),
                                                dcc.Download(id="preset-download-2"),
                                                html.Button(
                                                    "Export",
                                                    id="preset-down-button-2",
                                                    n_clicks=0,
                                                    style={
                                                        "border-color": "#5c6cfa",
                                                        "width": "120px",
                                                    },
                                                ),
                                            ],
                                            style={"display": "flex"},
                                        ),
                                    ],
                                    style={"margin-left": "20px", "padding": "10px"},
                                ),
                            ],
                            id="second-file-upload",
                            style={
                                "display": "flex",
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
                                                        "margin-left": "10px",
                                                        "margin-bottom": "10px",
                                                        "font-weight": "bold",
                                                    },
                                                ),
                                                dcc.RadioItems(
                                                    ["Dataset 1", "Dataset 2"],
                                                    "Dataset 1",
                                                    id="data-selector",
                                                    inline=False,
                                                    style={
                                                        "display": "flex",
                                                        "padding": "20px",
                                                    },
                                                ),
                                            ],
                                            id="data-selector-div",
                                            style={
                                                "display": "none",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Button(
                                                    "Reset",
                                                    id="reset-button",
                                                    n_clicks=0,
                                                    style={
                                                        "border-color": "#5c6cfa",
                                                        "width": "120px",
                                                        "margin-right": "4px",
                                                    },
                                                ),
                                                html.Button(
                                                    "Demo",
                                                    id="demo-button",
                                                    n_clicks=0,
                                                    style={
                                                        "border-color": "#5c6cfa",
                                                        "width": "120px",
                                                    },
                                                ),
                                            ],
                                            style={
                                                "margin-right": "40px",
                                                "float": "right",
                                                "display": "flex",
                                                "margin-left": "auto",
                                                "border-color": "#5c6cfa",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex"},
                                ),
                            ],
                            style={"margin-top": "15px", "padding-bottom": "10px"},
                        ),
                        dcc.Checklist(
                            [
                                "Table",
                                "Stats",
                                "Timeline",
                                "Map",
                                "Country comparison",
                                "Correlation Heatmap",
                                "Univariate Forecast",
                                "Multivariate Forecast",
                            ],
                            value=[
                                "Table",
                                "Stats",
                                "Timeline",
                                "Map",
                                "Country comparison",
                                "Correlation Heatmap",
                                "Univariate Forecast",
                                "Multivariate Forecast",
                            ],
                            labelStyle={
                                "margin-left": "10px",
                                "font-weight": "lighter",
                                "font-size": "14px",
                                "padding-bottom": "20px",
                            },
                            inline=True,
                            id="visibility-checklist",
                            style={"margin-bottom": "10px"},
                        ),
                    ],
                    style={
                        "backgroundColor": "#111111",
                    },
                ),
            ],
            style={
                "backgroundColor": "#232323",
                "height": "340px",
                "display": "block",
            },
        ),
        html.Div(
            [
                html.Div(style={"backgroundColor": "#232323", "padding": "10px"}),
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
                        dcc.Loading(
                            parent_style={"backgroundColor": "transparent"},
                            style={"backgroundColor": "transparent"},
                            children=[
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
                        ),
                    ],
                    style={
                        "backgroundColor": "#5c6cfa",
                        "overflow": "auto",
                        "max-height": "250px",
                    },
                ),
            ],
            id="table-div",
            style={"backroundColor": "#ffffff", "display": "none"},
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
                                                "width": "100%",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Span(
                                                    "help",
                                                    className="material-symbols-outlined",
                                                ),
                                                html.Span(
                                                    "Mean, max and min are computed for complete dataset. \n The slider sets the window for the growth rate computation.",
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
                                                "margin-left": "auto",
                                                "padding-top": "7px",
                                                "backgroundColor": "#111111",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex", "width": "100%"},
                                ),
                                html.Hr(
                                    style={
                                        "padding": "0px",
                                        "margin": "0px",
                                        "backgroundColor": "#5c6cfa",
                                        "border-color": "#5c6cfa",
                                        "width": "100%",
                                    }
                                ),
                            ],
                        ),
                        html.Div(
                            style={"padding": "5px", "backgroundColor": "#232323"}
                        ),
                        html.Div(
                            "Growth rate window",
                            style={"padding": "15px"},
                        ),
                        dcc.RangeSlider(
                            0,
                            20,
                            step=1,
                            id="year-range-slider",
                            marks=None,
                            allowCross=False,
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Mean",
                                                    style={
                                                        "backgroundColor": "#111111",
                                                        "font-weight": "bolder",
                                                        "textAlign": "center",
                                                        "margin-left": "auto",
                                                        "margin-right": "auto",
                                                        "padding": "15px",
                                                    },
                                                ),
                                                dcc.Loading(
                                                    type="circle",
                                                    children=[
                                                        html.Div(
                                                            ["text"],
                                                            style={
                                                                "white-space": "pre-line",
                                                                "margin-left": "auto",
                                                                "margin-right": "auto",
                                                                "textAlign": "center",
                                                                "font-size": "40px",
                                                            },
                                                            id="avg-stat",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            style={
                                                "backgroundColor": "#111111",
                                                "height": "100px",
                                                "width": "90%",
                                                # "font-size": "20px",
                                            },
                                        ),
                                    ],
                                    style={"display": "inline-block", "width": "25%"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Max",
                                                    style={
                                                        "backgroundColor": "#111111",
                                                        "font-weight": "bolder",
                                                        "textAlign": "center",
                                                        "margin-left": "auto",
                                                        "margin-right": "auto",
                                                        "padding": "15px",
                                                    },
                                                ),
                                                dcc.Loading(
                                                    type="circle",
                                                    children=[
                                                        html.Div(
                                                            ["text"],
                                                            style={
                                                                "white-space": "pre-line",
                                                                "text-align": "center",
                                                                "font-size": "40px",
                                                            },
                                                            id="max-stat",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            style={
                                                "backgroundColor": "#111111",
                                                "height": "100px",
                                                "width": "90%",
                                            },
                                        ),
                                    ],
                                    style={"display": "inline-block", "width": "25%"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Min",
                                                    style={
                                                        "backgroundColor": "#111111",
                                                        "font-weight": "bolder",
                                                        "textAlign": "center",
                                                        "margin-left": "auto",
                                                        "margin-right": "auto",
                                                        "padding": "15px",
                                                    },
                                                ),
                                                dcc.Loading(
                                                    type="circle",
                                                    children=[
                                                        html.Div(
                                                            ["text"],
                                                            style={
                                                                "white-space": "pre-line",
                                                                "textAlign": "center",
                                                                "font-size": "40px",
                                                            },
                                                            id="min-stat",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            style={
                                                "backgroundColor": "#111111",
                                                "height": "100px",
                                                "width": "90%",
                                            },
                                        ),
                                    ],
                                    style={"display": "inline-block", "width": "25%"},
                                ),
                                html.Div(
                                    [
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
                                                                "width": "75px",
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
                                                            "Growth",
                                                            style={
                                                                "backgroundColor": "#111111",
                                                                "font-weight": "bolder",
                                                                "textAlign": "center",
                                                                "padding": "15px",
                                                                "margin-left": "65px",
                                                                "margin-right": "auto",
                                                            },
                                                        ),
                                                    ],
                                                    style={
                                                        "display": "flex",
                                                        "margin-left": "auto",
                                                        "margin-right": "auto",
                                                    },
                                                ),
                                                dcc.Loading(
                                                    type="circle",
                                                    children=[
                                                        html.Div(
                                                            ["text"],
                                                            style={
                                                                "white-space": "pre-line",
                                                                "textAlign": "center",
                                                                "font-size": "40px",
                                                            },
                                                            id="growth-stat",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            style={
                                                "backgroundColor": "#111111",
                                                "height": "100px",
                                                "width": "100%",
                                            },
                                        ),
                                    ],
                                    style={"display": "inline-block", "width": "25%"},
                                ),
                            ],
                            style={"display": "flex"},
                        ),
                    ],
                    id="stats-div",
                    style={"margin-bottom": "10px", "display": "none"},
                ),
                html.Div(style={"backgroundColor": "#232323", "padding": "10px"}),
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
                        dcc.Loading(
                            type="circle",
                            children=[
                                html.Div(
                                    [],
                                    id="line-div",
                                ),
                            ],
                        ),
                    ],
                    id="line-plot",
                    style={
                        "display": "none",
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
                                                "font-size": "14px",
                                                "border-top": "0px",
                                                "border-left": "0px",
                                                "border-right": "0px",
                                                "border-bottom": "0px",
                                                "backgroundColor": "#111111",
                                                "border-color": "#5c6cfa",
                                                "border-radius": "0px",
                                                "padding-top": "1.5px",
                                                "display": "none",  # disabled
                                            },
                                        ),
                                        html.Div(
                                            "Map",
                                            style={
                                                "padding-top": "10px",
                                                "padding-left": "10px",
                                                "padding-bottom": "10px",
                                                "backgroundColor": "#111111",
                                                "font-weight": "bold",
                                                "textAlign": "center",
                                                "width": "100%",
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
                        dcc.Loading(
                            type="circle",
                            children=[
                                html.Div(
                                    [],
                                    id="map-div",
                                ),
                            ],
                        ),
                    ],
                    id="map-plot",
                    style={"display": "none"},
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
                                    placeholder="Select country",
                                    clearable=False,
                                    id="country-dropdown",
                                    style={
                                        "width": "140px",
                                        "font-size": "14px",
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
                                        "width": "80%",
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
                    dcc.Loading(
                        type="circle",
                        children=[
                            html.Div(
                                [],
                                id="max_country-comparison-div",
                                style={"display": "inline-block", "width": "100%"},
                            ),
                        ],
                    ),
                ),
            ],
            id="compare-div",
            style={"display": "none"},
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
                                    placeholder="Select country",
                                    clearable=False,
                                    id="country-dropdown-corr",
                                    style={
                                        "width": "140px",
                                        "font-size": "14px",
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
                                    "Correlation heatmap",
                                    style={
                                        "padding-top": "10px",
                                        "padding-left": "10px",
                                        "padding-bottom": "10px",
                                        "backgroundColor": "#111111",
                                        "font-weight": "bold",
                                        "textAlign": "center",
                                        "width": "80%",
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
                dcc.Loading(
                    type="circle",
                    children=[
                        html.Div(
                            html.Div(
                                [],
                                id="heatmap-plot-div",
                                style={"display": "inline-block", "width": "100%"},
                            ),
                        ),
                    ],
                ),
            ],
            id="heatmap-div",
            style={"display": "none"},
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
                                    placeholder="Select country",
                                    clearable=False,
                                    id="country-dropdown-forecast",
                                    style={
                                        "width": "140px",
                                        "font-size": "14px",
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
                                    "Univariate forecast",
                                    style={
                                        "padding-top": "10px",
                                        "padding-left": "10px",
                                        "padding-bottom": "10px",
                                        "backgroundColor": "#111111",
                                        "font-weight": "bold",
                                        "textAlign": "center",
                                        "width": "80%",
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
                    [
                        html.Div(
                            [
                                html.Div(
                                    "Specify time frequency",
                                    style={
                                        "padding-top": "15px",
                                        "padding-bottom": "15px",
                                        "padding-right": "15px",
                                    },
                                ),
                                dcc.Dropdown(
                                    ["Yearly", "Monthly", "Weekly", "Daily"],
                                    placeholder="Select frequency",
                                    clearable=False,
                                    id="frequency-dropdown-forecast",
                                    style={
                                        "width": "140px",
                                        "font-size": "14px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                    },
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.Div(
                                    "Select model",
                                    style={
                                        "padding-top": "15px",
                                        "padding-bottom": "15px",
                                        "padding-right": "15px",
                                    },
                                ),
                                dcc.Dropdown(
                                    ["Prophet", "Regression"],
                                    placeholder="Select model",
                                    clearable=False,
                                    id="model-dropdown-forecast",
                                    style={
                                        "width": "140px",
                                        "font-size": "14px",
                                        "border-color": "#5c6cfa",
                                        "background-color": "#111111",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={"display": "flex", "margin-left": "10px"},
                ),
                html.Div(
                    [
                        html.Div("Set future prediction", style={"padding": "15px"}),
                        dcc.Slider(1, 30, 1, id="forecast-slider"),
                    ],
                    id="forecast-slider-div",
                    style={"display": "none"},
                ),
                dcc.Loading(
                    type="circle",
                    children=[
                        html.Div(
                            html.Div(
                                [],
                                id="fit-plot-div",
                                style={"display": "inline-block", "width": "100%"},
                            ),
                        ),
                    ],
                ),
            ],
            id="trend-div",
            style={"display": "none"},
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
                                    placeholder="Select country",
                                    clearable=False,
                                    id="country-dropdown-multi-forecast",
                                    style={
                                        "width": "140px",
                                        "font-size": "14px",
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
                                    "Multivariate forecast",
                                    style={
                                        "padding-top": "10px",
                                        "padding-left": "10px",
                                        "padding-bottom": "10px",
                                        "backgroundColor": "#111111",
                                        "font-weight": "bold",
                                        "textAlign": "center",
                                        "width": "80%",
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
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            "Specify time frequency",
                                            style={
                                                "padding-top": "15px",
                                                "padding-bottom": "15px",
                                                "padding-right": "15px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            ["Yearly", "Monthly", "Weekly", "Daily"],
                                            placeholder="Select frequency",
                                            clearable=False,
                                            id="multi-frequency-dropdown-forecast",
                                            style={
                                                "width": "140px",
                                                "font-size": "14px",
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                                # "textAlign": "center",
                                            },
                                        ),
                                    ],
                                    style={"margin-left": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Select model",
                                            style={
                                                "padding-top": "15px",
                                                "padding-bottom": "15px",
                                                "padding-right": "15px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            [
                                                "Prophet",
                                                "Vector AR",
                                                "HW Smoothing",
                                            ],
                                            placeholder="Select model",
                                            clearable=False,
                                            id="model-dropdown-multi-forecast",
                                            style={
                                                "width": "140px",
                                                "font-size": "14px",
                                                "border-color": "#5c6cfa",
                                                "background-color": "#111111",
                                                # "textAlign": "center",
                                            },
                                        ),
                                    ]
                                ),
                            ],
                            style={"display": "flex"},
                        ),
                        html.Div(
                            [
                                html.Div(
                                    "Set future prediction", style={"padding": "15px"}
                                ),
                                dcc.Slider(1, 30, 1, id="var-forecast-slider"),
                            ],
                            id="var-slider-div",
                            style={"display": "none"},
                        ),
                        html.Div(
                            [
                                dcc.Store(id="maxlags-store"),
                                html.Div("Set maximum lags", style={}),
                                # dcc.Slider(1, 7, 1, id="var-maxlags-slider"),
                                dcc.Input(
                                    value=1,
                                    min=1,
                                    max=7,
                                    step=1,
                                    id="var-maxlags-slider",
                                    type="number",
                                    style={
                                        "backgroundColor": "#111111",
                                        "color": "#f2f2f2",
                                        "padding": "10px",
                                        "border-top": "0px",
                                        "border-left": "0px",
                                        "border-right": "0px",
                                        "border-color": "#5c6cfa",
                                        "width": "300px",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.Button(
                                            "Predict",
                                            id="submit-maxlags-button",
                                            n_clicks=0,
                                            style={
                                                "border-color": "#5c6cfa",
                                                "width": "120px",
                                                "margin-top": "10px",
                                            },
                                        ),
                                    ]
                                ),
                            ],
                            id="var-lags-div",
                            style={
                                "display": "none",
                                "padding-left": "10px",
                                "margin-top": "10px",
                            },
                        ),
                        html.Div(
                            [
                                dcc.Store(id="alpha-store"),
                                html.Div(
                                    "Set \u03B1-parameter",
                                    style={},
                                ),
                                dcc.Input(
                                    value=0.5,
                                    id="alpha-coefficient",
                                    type="number",
                                    min=1e-4,
                                    max=1 - 1e-4,
                                    step=1e-4,
                                    style={
                                        "backgroundColor": "#111111",
                                        "color": "#f2f2f2",
                                        "padding": "10px",
                                        "border-top": "0px",
                                        "border-left": "0px",
                                        "border-right": "0px",
                                        "border-color": "#5c6cfa",
                                        "width": "300px",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.Button(
                                            "Predict",
                                            id="submit-alpha-button",
                                            n_clicks=0,
                                            style={
                                                "border-color": "#5c6cfa",
                                                "width": "120px",
                                                "margin-top": "10px",
                                            },
                                        ),
                                    ]
                                ),
                            ],
                            id="alpha-div",
                            style={
                                "padding-left": "10px",
                                "margin-top": "10px",
                                "display": "none",
                            },
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div("Select dependent dataset"),
                                        dcc.RadioItems(
                                            [],
                                            id="forecast-data-selector",
                                            labelStyle={
                                                "display": "block",
                                                "padding": "5px",
                                                "font-size": "12px",
                                                "font-weight": "lighter",
                                            },
                                            style={
                                                "padding-bottom": "10px",
                                                "padding-top": "5px",
                                            },
                                        ),
                                        dcc.Store(id="scenario-store"),
                                        html.Div(
                                            "Specify future scenario for independent dataset",
                                            style={
                                                "padding-top": "10px",
                                                "padding-bottom": "5px",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                dcc.Input(
                                                    id="scenario-input",
                                                    type="text",
                                                    style={
                                                        "backgroundColor": "#111111",
                                                        "color": "#f2f2f2",
                                                        "border-top": "0px",
                                                        "border-left": "0px",
                                                        "border-right": "0px",
                                                        "border-color": "#5c6cfa",
                                                        "width": "300px",
                                                        "font-size": "14px",
                                                        "font-weight": "lighter",
                                                    },
                                                ),
                                            ],
                                            style={
                                                "padding-top": "5px",
                                                "padding-bottom": "5px",
                                            },
                                        ),
                                        html.Button(
                                            "Predict",
                                            id="submit-scenario-button",
                                            n_clicks=0,
                                            style={
                                                "border-color": "#5c6cfa",
                                                "width": "120px",
                                                # "margin-left": "5px",
                                                "margin-top": "5px",
                                            },
                                        ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        dash_table.DataTable(
                                            id="forecast-data-table",
                                            style_data={
                                                "backgroundColor": "#232323",
                                                "border": "solid 1px #5c6cfa",
                                            },
                                            style_cell={"padding": "5px"},
                                            style_header={
                                                "backgroundColor": "#454545",
                                                "border": "solid 1px #5c6cfa",
                                            },
                                        ),
                                    ],
                                    style={
                                        "margin-left": "auto",
                                        "float": "right",
                                        "margin-right": "20px",
                                        "overflow": "auto",
                                        "max-height": "175px",
                                        "width": "50%",
                                    },
                                ),
                            ],
                            id="scenario-div",
                            style={
                                "padding-left": "10px",
                                "margin-top": "10px",
                                "display": "none",
                            },
                        ),
                        dcc.Loading(
                            type="circle",
                            children=[
                                html.Div(
                                    html.Div(
                                        [],
                                        id="multi-fit-plot-div",
                                        style={
                                            "display": "inline-block",
                                            "width": "100%",
                                        },
                                    ),
                                ),
                            ],
                        ),
                    ]
                ),
            ],
            id="multi-forecast-div",
            style={"display": "none"},
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
    Output("preset-download-1", "data"),
    Input("delimiter-dropdown-1", "value"),
    Input("geo-dropdown-1", "value"),
    Input("reshape-dropdown-1", "value"),
    Input("reshape-switch-1", "on"),
    Input("time-dropdown-1", "value"),
    Input("feature-dropdown-1", "value"),
    Input("preset-down-button-1", "n_clicks"),
    Input("table-upload", "filename"),
)
def export_dropdown_settings(
    delimiter_value: str,
    geo_column_value: str,
    reshape_column_value: str,
    reshape_switch_status: str,
    time_column_value: str,
    feature_column_value: str,
    download_button_n_clicks: int,
    filename: str,
):
    """Downloads a JSON file containing the selected values for each dropdown. Resulting file can be uploaded as preset as well.

    Args:
        delimiter_value (str): value of delimiter
        geo_column_value (str): value of geo column
        reshape_column_value (str): value of reshape column
        reshape_switch_status (str): status of reshape toggle
        time_column_value (str): value of time column
        feature_column_value (str): value of feature column
        download_button_n_clicks (int): number of clicks for download button (used to listen for button press)
        filename (str): name of the uploaded dataset

    Raises:
        exceptions.PreventUpdate: Update prevented unless button is pressed

    Returns:
        dict: JSON object, file name
    """
    changed_item = [p["prop_id"] for p in callback_context.triggered][0]

    if "preset-down-button-1" in changed_item:

        return export_settings(
            delimiter_value,
            geo_column_value,
            reshape_column_value,
            reshape_switch_status,
            time_column_value,
            feature_column_value,
            filename,
        )

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("preset-download-2", "data"),
    Input("delimiter-dropdown-2", "value"),
    Input("geo-dropdown-2", "value"),
    Input("reshape-dropdown-2", "value"),
    Input("reshape-switch-2", "on"),
    Input("time-dropdown-2", "value"),
    Input("feature-dropdown-2", "value"),
    Input("preset-down-button-2", "n_clicks"),
    Input("table-upload-2", "filename"),
)
def export_second_dropdown_settings(
    delimiter_value: str,
    geo_column_value: str,
    reshape_column_value: str,
    reshape_switch_status: str,
    time_column_value: str,
    feature_column_value: str,
    download_button_n_clicks: int,
    filename: str,
):
    """Downloads a JSON file containing the selected values for each dropdown. Resulting file can be imported as preset.

    Args:
        delimiter_value (str): value of delimiter
        geo_column_value (str): value of geo column
        reshape_column_value (str): value of reshape column
        reshape_switch_status (str): status of reshape toggle
        time_column_value (str): value of time column
        feature_column_value (str): value of feature column
        download_button_n_clicks (int): number of clicks for download button (used to listen for button press)
        filename (str): name of the uploaded dataset

    Raises:
        exceptions.PreventUpdate: Update prevented unless button is pressed

    Returns:
        dict: JSON object, file name
    """
    changed_item = [p["prop_id"] for p in callback_context.triggered][0]

    if "preset-down-button-2" in changed_item:

        return export_settings(
            delimiter_value,
            geo_column_value,
            reshape_column_value,
            reshape_switch_status,
            time_column_value,
            feature_column_value,
            filename,
        )

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("dataset", "data"),
    Output("geo-dropdown-1", "options"),
    Output("reshape-dropdown-1", "options"),
    Output("table-upload", "children"),
    Output("feature-dropdown-1", "options"),
    Output("time-dropdown-1", "options"),
    Output("table-upload", "contents"),
    Output("delimiter-dropdown-1", "value"),
    Output("table-upload", "filename"),
    Output("reshape-switch-1", "on"),
    Output("geo-dropdown-1", "value"),
    Output("dataset-1-fail", "displayed"),
    Output("feature-dropdown-1", "value"),
    Output("time-dropdown-1", "value"),
    Output("preset-upload-1", "contents"),
    Output("reshape-dropdown-1", "value"),
    Output("dataset-1-fail", "message"),
    Input("delimiter-dropdown-1", "value"),
    Input("geo-dropdown-1", "value"),
    Input("table-upload", "contents"),
    Input("table-upload", "filename"),
    Input("reshape-dropdown-1", "value"),
    Input("reshape-switch-1", "on"),
    State("table-upload", "children"),
    Input("demo-button", "n_clicks"),
    Input("preset-upload-1", "contents"),
    Input("reset-button", "n_clicks"),
    prevent_initial_call=True,
)
def preprocess_data(
    delimiter_value: str,
    geo_column_value: str,
    file_content: str,
    file_name: str,
    reshape_column_value: str,
    reshape_switch_status: bool,
    file_upload_children: str,
    demo_button_n_clicks: int,
    preset_file: str,
    reset_button_n_clicks: int,
):
    """Handles the preprocessing of an uploaded dataset. In demo mode, a predefined dataset is loaded instead.

    Args:
        delimiter_value (str): value of delimiter dropdown
        geo_column_value (str): value of geo column
        file_content (str): uploaded file content
        file_name (str): uploaded file name
        reshape_column_value (str): value of column to reshape on
        reshape_switch_status (bool): value of reshape toggle
        file_upload_children (str): container of file upload element
        demo_button_n_clicks (int): number of clicks of demo button (used to listen for presses)
        preset_file (str): content of uploaded preset file

    Returns:
        tuple:
    """

    return preprocess_dataset(
        delimiter_value,
        geo_column_value,
        file_content,
        file_name,
        reshape_column_value,
        reshape_switch_status,
        file_upload_children,
        demo_button_n_clicks,
        "Demo 1",
        preset_file,
    )


@app.callback(
    Output("dataset-2", "data"),
    Output("geo-dropdown-2", "options"),
    Output("reshape-dropdown-2", "options"),
    Output("table-upload-2", "children"),
    Output("feature-dropdown-2", "options"),
    Output("time-dropdown-2", "options"),
    Output("table-upload-2", "contents"),
    Output("delimiter-dropdown-2", "value"),
    Output("table-upload-2", "filename"),
    Output("reshape-switch-2", "on"),
    Output("geo-dropdown-2", "value"),
    Output("dataset-2-fail", "displayed"),
    Output("feature-dropdown-2", "value"),
    Output("time-dropdown-2", "value"),
    Output("preset-upload-2", "contents"),
    Output("reshape-dropdown-2", "value"),
    Output("dataset-2-fail", "message"),
    Output("data-selector", "style"),
    Output("data-selector-div", "style"),
    Input("delimiter-dropdown-2", "value"),
    Input("geo-dropdown-2", "value"),
    Input("table-upload-2", "contents"),
    Input("table-upload-2", "filename"),
    Input("reshape-dropdown-2", "value"),
    Input("reshape-switch-2", "on"),
    State("table-upload-2", "children"),
    Input("demo-button", "n_clicks"),
    Input("preset-upload-2", "contents"),
    Input("reset-button", "n_clicks"),
    prevent_initial_call=True,
)
def preprocess_second_data(
    delimiter_value: str,
    geo_column_value: str,
    file_content: str,
    file_name: str,
    reshape_column_value: str,
    reshape_switch_status: bool,
    file_upload_children: str,
    demo_button_n_clicks: int,
    preset_file,
    reset_button_n_clicks: int,
):
    """Handles the preprocessing of an uploaded dataset. In demo mode, a predefined dataset is loaded instead.

    Args:
        delimiter_value (str): value of delimiter dropdown
        geo_column_value (str): value of geo column
        file_content (str): uploaded file content
        file_name (str): uploaded file name
        reshape_column_value (str): value of column to reshape on
        reshape_switch_status (bool): value of reshape toggle
        file_upload_children (str): container of file upload element
        demo_button_n_clicks (int): number of clicks of demo button (used to listen for presses)
        preset_file (str): content of uploaded preset file

    Returns:
        tuple:
    """
    radio_div_visibility = {
        "display": "block",
        "padding-bottom": "10px",
        "padding-left": "5px",
    }

    selector_visibility = {"display": "block", "padding-left": "5px"}

    return (
        *preprocess_dataset(
            delimiter_value,
            geo_column_value,
            file_content,
            file_name,
            reshape_column_value,
            reshape_switch_status,
            file_upload_children,
            demo_button_n_clicks,
            "Demo 2",
            preset_file,
        ),
        radio_div_visibility,
        selector_visibility,
    )


@app.callback(
    Output("country-dropdown", "options"),
    Output("country-dropdown", "value"),
    Input("dataset", "data"),
    Input("dataset-2", "data"),
    Input("geo-dropdown-1", "value"),
    Input("geo-dropdown-2", "value"),
)
def update_country_dropdown_comparison(
    dataset_1: str, dataset_2: str, geo_dropdown_value_1: str, geo_dropdown_value_2: str
):
    """Fills the dropdown in comparison section with countries that occur in both datasets

    Args:
        dataset_1 (str): first dataset
        dataset_2 (str): second dataset
        geo_dropdown_value_1 (str): value of first geo column
        geo_dropdown_value_2 (str): value of second geo column

    Raises:
        exceptions.PreventUpdate: Update prevented unless both datasets and geo-columns are available

    Returns:
        tuple: _description_
    """
    if dataset_1 and dataset_2 and geo_dropdown_value_1 and geo_dropdown_value_2:
        dataset_1_countries = pd.read_json(dataset_1)[geo_dropdown_value_1].unique()

        dataset_2_countries = pd.read_json(dataset_2)[geo_dropdown_value_2].unique()

        joint_countries = [
            country
            for country in dataset_1_countries
            if country in set(dataset_2_countries)
        ]

        return joint_countries, joint_countries[0]

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("year-dropdown-stats", "options"),
    Output("year-dropdown-stats", "value"),
    Output("country-dropdown-stats", "options"),
    Output("country-dropdown-stats", "value"),
    Output("year-dropdown-map", "options"),
    Output("year-dropdown-map", "value"),
    Output("year-range-slider", "min"),
    Output("year-range-slider", "max"),
    Output("country-dropdown-corr", "options"),
    Output("country-dropdown-corr", "value"),
    Output("country-dropdown-forecast", "options"),
    Output("country-dropdown-forecast", "value"),
    Output("year-range-slider", "value"),
    Output("year-range-slider", "marks"),
    Output("country-dropdown-multi-forecast", "options"),
    Output("country-dropdown-multi-forecast", "value"),
    Input("dataset", "data"),
    Input("dataset-2", "data"),
    Input("data-selector", "value"),
    Input("geo-dropdown-1", "value"),
    Input("geo-dropdown-2", "value"),
    Input("time-dropdown-1", "value"),
    Input("time-dropdown-2", "value"),
)
def update_year_and_country_dropdown_stats(
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

        return get_year_and_country_options_stats(
            df, geo_column=geo_column, time_column=time_column
        )
    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("data-table", "data"),
    Output("table-div", "style"),
    Input("dataset", "data"),
    Input("dataset-2", "data"),
    Input("data-selector", "value"),
    Input("table-upload", "contents"),
    Input("delimiter-dropdown-1", "value"),
    Input("delimiter-dropdown-2", "value"),
    Input("visibility-checklist", "value"),
)
def update_table_content(
    dataset_1: str,
    dataset_2: str,
    selected_dataset: str,
    file: str,
    delimiter_dropdown_1: str,
    delimiter_dropdown_2: str,
    visibility_checklist: list,
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

    if (
        (dataset_1 and selected_dataset == "Dataset 1" and delimiter_dropdown_1)
        or (dataset_2 and selected_dataset == "Dataset 2" and delimiter_dropdown_2)
    ) and "Table" in visibility_checklist:
        datasets = {"Dataset 1": dataset_1, "Dataset 2": dataset_2}

        df = pd.read_json(datasets[selected_dataset]).round(2).to_dict("records")

        table_div_style = {"backroundColor": "#ffffff", "display": "block"}

        return df, table_div_style

    else:
        table_div_style = {"display": "none"}
        return no_update, table_div_style


@app.callback(
    Output("avg-stat", "children"),
    Output("max-stat", "children"),
    Output("min-stat", "children"),
    Output("growth-stat", "children"),
    Output("stats-div", "style"),
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
    [Input("year-range-slider", "value")],
    Input("table-upload", "contents"),
    Input("visibility-checklist", "value"),
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
    year_range: list,
    file: str,
    visibility_checklist: list,
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
        (
            dataset
            and feature_dropdown_1
            and time_dropdown_1
            and geo_dropdown_1
            and selected_dataset == "Dataset 1"
        )
        or (
            dataset_2
            and feature_dropdown_2
            and time_dropdown_2
            and geo_dropdown_2
            and selected_dataset == "Dataset 2"
        )
    ) and "Stats" in visibility_checklist:
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

        filtered_df_by_country = df[(df[geo_column] == country_dropdown_stats)]

        mean, max, min, max_country, min_country = compute_stats(
            filtered_df, feature_column, geo_column
        )

        growth_rate = compute_growth_rate(
            filtered_df_by_country, feature_column, year_range
        )

        avg_stat_children.clear()
        avg_stat_children.append(str(mean))

        max_stat_children.clear()
        max_stat_children.append(str(max) + " - " + max_country)

        min_stat_children.clear()
        min_stat_children.append(str(min) + " - " + min_country)

        growth_stat_children.clear()
        growth_stat_children.append(str(growth_rate) + "%")

        stats_div_style = {"display": "block"}

        return (
            avg_stat_children,
            max_stat_children,
            min_stat_children,
            growth_stat_children,
            stats_div_style,
        )
    else:
        table_div_style = {"display": "none"}
        return no_update, no_update, no_update, no_update, table_div_style


@app.callback(
    Output("line-div", "children"),
    Output("line-plot", "style"),
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
    Input("visibility-checklist", "value"),
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
    visibility_checklist: list,
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
        (
            dataset
            and feature_dropdown_1
            and time_dropdown_1
            and geo_dropdown_1
            and selected_dataset == "Dataset 1"
        )
        or (
            dataset_2
            and feature_dropdown_2
            and time_dropdown_2
            and geo_dropdown_2
            and selected_dataset == "Dataset 2"
        )
    ) and "Timeline" in visibility_checklist:

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

        line_plot_style = {"display": "inline-block", "width": "57%"}

        return timeline_children, line_plot_style

    elif dataset and time_dropdown_1 == "none":

        df = pd.read_json(dataset)
        fig = create_multi_line_plot(df)

        timeline_children.clear()

        timeline_children.append(dcc.Graph(figure=fig))

        line_plot_style = {"display": "inline-block", "width": "40%"}

        return timeline_children, line_plot_style

    else:
        line_plot_style = {"display": "none"}

        return timeline_children, line_plot_style


@app.callback(
    Output("map-div", "children"),
    Output("map-plot", "style"),
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
    Input("visibility-checklist", "value"),
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
    visiblity_checklist: list,
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
        (
            dataset
            and feature_dropdown_1
            and time_dropdown_1
            and geo_dropdown_1
            and selected_dataset == "Dataset 1"
        )
        or (
            dataset_2
            and feature_dropdown_2
            and time_dropdown_2
            and geo_dropdown_2
            and selected_dataset == "Dataset 2"
        )
    ) and "Map" in visiblity_checklist:

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

        # mapbox choropleth
        # fig = create_choropleth_plot(
        #     filtered_df, geo_column=geo_column, feature_column=feature_column
        # )

        fig = create_choropleth_slider_plot(
            df,
            geo_column=geo_column,
            feature_column=feature_column,
            time_column=time_column,
        )

        if map_children:
            map_children.clear()

        map_children.append(dcc.Graph(figure=fig))

        map_div_style = {
            "display": "inline-block",
            "width": "42.3%",
            "margin-left": "10px",
        }

        return map_children, map_div_style

    else:
        map_div_style = {"display": "none"}

        return map_children, map_div_style


@app.callback(
    Output("max_country-comparison-div", "children"),
    Output("compare-div", "style"),
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
    Input("visibility-checklist", "value"),
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
    visibility_checklist: list,
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
    ) and "Country comparison" in visibility_checklist:
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

        compare_div_style = {"display": "block"}

        return comparison_children, compare_div_style
    else:
        compare_div_style = {"display": "none"}

        return comparison_children, compare_div_style


@app.callback(
    Output("forecast-slider", "marks"),
    Output("forecast-slider-div", "style"),
    Input("dataset", "data"),
    Input("dataset-2", "data"),
    Input("time-dropdown-1", "value"),
    Input("time-dropdown-2", "value"),
    Input("data-selector", "value"),
    Input("frequency-dropdown-forecast", "value"),
)
def update_forecast_slider(
    dataset: str,
    dataset_2: str,
    time_dropdown_1: str,
    time_dropdown_2: str,
    selected_dataset: str,
    frequency_dropdown: str,
):
    if (
        dataset
        and time_dropdown_1
        and selected_dataset == "Dataset 1"
        and frequency_dropdown
    ) or (
        dataset_2
        and time_dropdown_2
        and selected_dataset == "Dataset 2"
        and frequency_dropdown
    ):

        datasets = {
            "Dataset 1": (dataset, time_dropdown_1),
            "Dataset 2": (dataset_2, time_dropdown_2),
        }

        df = pd.read_json(datasets[selected_dataset][0])
        time_column = datasets[selected_dataset][1]

        marks = get_time_marks(df, time_column, frequency_dropdown)

        slider_visibility = {"display": "block"}

        return marks, slider_visibility

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("fit-plot-div", "children"),
    Output("trend-div", "style"),
    Input("dataset", "data"),
    Input("dataset-2", "data"),
    Input("feature-dropdown-1", "value"),
    Input("feature-dropdown-2", "value"),
    Input("geo-dropdown-1", "value"),
    Input("geo-dropdown-2", "value"),
    Input("time-dropdown-1", "value"),
    Input("time-dropdown-2", "value"),
    Input("data-selector", "value"),
    State("fit-plot-div", "children"),
    Input("country-dropdown-forecast", "value"),
    Input("forecast-slider", "value"),
    Input("frequency-dropdown-forecast", "value"),
    Input("model-dropdown-forecast", "value"),
    Input("visibility-checklist", "value"),
)
def update_forecast(
    dataset: str,
    dataset_2: str,
    feature_dropdown_1: str,
    feature_dropdown_2: str,
    geo_dropdown_1: str,
    geo_dropdown_2: str,
    time_dropdown_1: str,
    time_dropdown_2: str,
    selected_dataset: str,
    fit_plot_children: list,
    country_dropdown: str,
    forecast_slider_value: str,
    frequency_dropdown: str,
    model_dropdown: str,
    visibility_checklist: list,
) -> tuple:
    """Creates a forecast using the Prophet model

    Args:
        dataset (str): First dataset
        dataset_2 (str): Second dataset
        feature_dropdown_1 (str): value of the first selected feature column
        feature_dropdown_2 (str): value of the second selected feature column
        geo_dropdown_1 (str): value of the first selected geo column
        geo_dropdown_2 (str): value of the second selected geo column
        time_dropdown_1 (str): value of the first selected time column
        time_dropdown_2 (str): value of the second selected time column
        selected_dataset (str): value of the dataset selector
        fit_plot_children (list): container for the forecast plot
        country_dropdown (str): selected country to forecast
        forecast_slider_value (str): number of periods to forecast (set by slider)

    Raises:
        exceptions.PreventUpdate: update prevented if neither dataset is loaded with all columns selected

    Returns:
        tuple: container with forecast plot, style component
    """

    if (
        (
            dataset
            and feature_dropdown_1
            and geo_dropdown_1
            and selected_dataset == "Dataset 1"
            and country_dropdown
            and frequency_dropdown
            and model_dropdown
        )
        or (
            dataset_2
            and feature_dropdown_2
            and geo_dropdown_2
            and selected_dataset == "Dataset 2"
            and country_dropdown
            and frequency_dropdown
            and model_dropdown
        )
    ) and "Univariate Forecast" in visibility_checklist:

        datasets = {
            "Dataset 1": (dataset, feature_dropdown_1, geo_dropdown_1, time_dropdown_1),
            "Dataset 2": (
                dataset_2,
                feature_dropdown_2,
                geo_dropdown_2,
                time_dropdown_2,
            ),
        }

        geo_column = datasets[selected_dataset][2]
        feature_column = datasets[selected_dataset][1]
        time_column = datasets[selected_dataset][3]

        df = pd.read_json(datasets[selected_dataset][0])

        if not forecast_slider_value:
            forecast_slider_value = 1

        df = df[df[geo_column] == country_dropdown]

        if model_dropdown == "Prophet":
            forecast, df = prophet_fit_and_predict(
                df,
                time_column=time_column,
                feature_column=feature_column,
                periods=forecast_slider_value,
                frequency=frequency_dropdown,
            )

        else:
            forecast, df = fit_and_predict(
                df,
                time_column,
                feature_column,
                frequency_dropdown,
                forecast_slider_value,
                model=model_dropdown,
            )

        fig = create_forecast_plot(
            forecast=forecast,
            df=df,
            time_column=time_column,
            feature_column=feature_column,
        )

        if fit_plot_children:
            fit_plot_children.clear()

        fit_plot_children.append(dcc.Graph(figure=fig))

        forecast_div_style = {"display": "block"}

        return fit_plot_children, forecast_div_style

    elif (
        (
            dataset
            and feature_dropdown_1
            and geo_dropdown_1
            and selected_dataset == "Dataset 1"
        )
        or (
            dataset_2
            and feature_dropdown_2
            and geo_dropdown_2
            and selected_dataset == "Dataset 2"
        )
    ) and "Univariate Forecast" in visibility_checklist:
        forecast_div_style = {"display": "block"}

        return fit_plot_children, forecast_div_style

    else:
        forecast_div_style = {"display": "none"}

        return fit_plot_children, forecast_div_style


@app.callback(
    Output("heatmap-plot-div", "children"),
    Output("heatmap-div", "style"),
    Input("dataset", "data"),
    Input("dataset-2", "data"),
    Input("time-dropdown-1", "value"),
    Input("time-dropdown-2", "value"),
    Input("geo-dropdown-1", "value"),
    Input("geo-dropdown-2", "value"),
    Input("data-selector", "value"),
    State("heatmap-plot-div", "children"),
    Input("country-dropdown-corr", "value"),
    Input("feature-dropdown-1", "value"),
    Input("feature-dropdown-2", "value"),
    Input("visibility-checklist", "value"),
)
def update_heatmap(
    dataset: str,
    dataset_2: str,
    time_dropdown_1: str,
    time_dropdown_2: str,
    geo_dropdown_1: str,
    geo_dropdown_2: str,
    selected_dataset: str,
    heatmap_children: list,
    country_dropdown: str,
    feature_dropdown_1: str,
    feature_dropdown_2: str,
    visibility_checklist: list,
):
    """Creates a heatmap from the correlation matrix of features

    Args:
        dataset (str): First dataset
        dataset_2 (str): Second dataset
        time_dropdown_1 (str): value of the selected time column value of the first dataset
        time_dropdown_2 (str): value of the selcted time column value of the second dataset
        geo_dropdown_1 (str): value of the selected geo column value of the first dataset
        geo_dropdown_2 (str): value of the selected geo column value of the second dataset
        selected_dataset (str): value of the dataset selector
        heatmap_children (list): container that holds the figure
        country_dropdown (str): selected country

    Raises:
        exceptions.PreventUpdate: update prevented if neither dataset is loaded with all columns selected

    Returns:
        list: container with heatmap plot
    """

    if (
        (
            dataset
            and time_dropdown_1
            and geo_dropdown_1
            and feature_dropdown_1
            and selected_dataset == "Dataset 1"
        )
        or (
            dataset_2
            and time_dropdown_2
            and geo_dropdown_2
            and feature_dropdown_2
            and selected_dataset == "Dataset 2"
        )
    ) and "Correlation Heatmap" in visibility_checklist:

        datasets = {
            "Dataset 1": (
                dataset,
                time_dropdown_1,
                geo_dropdown_1,
            ),
            "Dataset 2": (
                dataset_2,
                time_dropdown_2,
                geo_dropdown_2,
            ),
        }

        geo_column = datasets[selected_dataset][2]
        time_column = datasets[selected_dataset][1]

        df = pd.read_json(datasets[selected_dataset][0])

        df = df[df[geo_column] == country_dropdown]

        df = df.drop(columns=time_column)

        fig = create_correlation_heatmap(df)

        if heatmap_children:
            heatmap_children.clear()

        heatmap_children.append(dcc.Graph(figure=fig))

        heatmap_div_style = {"display": "block"}

        return heatmap_children, heatmap_div_style
    else:

        heatmap_div_style = {"display": "none"}

        return heatmap_children, heatmap_div_style


@app.callback(
    Output("alpha-store", "data"),
    Output("maxlags-store", "data"),
    Output("scenario-store", "data"),
    Input("alpha-coefficient", "value"),
    Input("submit-alpha-button", "n_clicks"),
    Input("var-maxlags-slider", "value"),
    Input("submit-maxlags-button", "n_clicks"),
    Input("scenario-input", "value"),
    Input("submit-scenario-button", "n_clicks"),
)
def update_parameter_stores(
    alpha: int,
    button_n_clicks: int,
    max_lags: int,
    max_lags_button_n_clicks: int,
    scenario: str,
    scenario_button_n_clicks: int,
):

    changed_item = [p["prop_id"] for p in callback_context.triggered][0]

    if alpha and "submit-alpha-button" in changed_item:
        return alpha, no_update, no_update

    elif max_lags and "submit-maxlags-button" in changed_item:
        return no_update, max_lags, no_update

    elif scenario and "submit-scenario-button" in changed_item:
        future_values = scenario.replace(" ", "").split(",")

        future_values_int = [int(x) for x in future_values]

        return no_update, no_update, future_values_int

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("multi-fit-plot-div", "children"),
    Output("var-slider-div", "style"),
    Output("scenario-div", "style"),
    Output("var-forecast-slider", "marks"),
    Output("multi-forecast-div", "style"),
    Output("var-lags-div", "style"),
    Output("alpha-div", "style"),
    Output("forecast-data-selector", "options"),
    Output("forecast-data-table", "data"),
    Input("dataset", "data"),
    Input("dataset-2", "data"),
    Input("feature-dropdown-1", "value"),
    Input("feature-dropdown-2", "value"),
    Input("geo-dropdown-1", "value"),
    Input("geo-dropdown-2", "value"),
    Input("time-dropdown-1", "value"),
    Input("time-dropdown-2", "value"),
    State("multi-fit-plot-div", "children"),
    Input("multi-frequency-dropdown-forecast", "value"),
    Input("scenario-store", "data"),
    Input("country-dropdown-multi-forecast", "value"),
    Input("model-dropdown-multi-forecast", "value"),
    Input("var-forecast-slider", "value"),
    # Input("var-maxlags-slider", "value"),
    Input("alpha-store", "data"),
    Input("maxlags-store", "data"),
    Input("table-upload", "filename"),
    Input("table-upload-2", "filename"),
    Input("forecast-data-selector", "options"),
    Input("forecast-data-selector", "value"),
    Input("visibility-checklist", "value"),
)
def update_multivariate_forecast(
    dataset_1: str,
    dataset_2: str,
    feature_dropdown_1: str,
    feature_dropdown_2: str,
    geo_dropdown_1: str,
    geo_dropdown_2: str,
    time_dropdown_1: str,
    time_dropdown_2: str,
    multi_forecast_children: list,
    multi_frequency_dropdown: str,
    scenario_data: list,
    selected_country: str,
    selected_model: str,
    var_slider_value: int,
    # var_maxlags_value: str,
    alpha_parameter: int,
    max_lags_parameter: int,
    filename_1: str,
    filename_2: str,
    forecast_data_selector_options: str,
    selected_dataset: str,
    visibility_checklist: list,
) -> tuple:
    """Performs multivariate forecast with an additional dataset and plots the result

    Args:
        dataset_1 (str): Dataset which is forecasted for
        dataset_2 (str): Dataset which is used as additional timeseries for the forecast
        feature_dropdown_1 (str): selected feature column of first dataset
        feature_dropdown_2 (str): selected feature column of second dataset
        geo_dropdown_1 (str): selected geo column of first dataset
        geo_dropdown_2 (str): selected geo column of second dataset
        time_dropdown_1 (str): selected time column of first dataset
        time_dropdown_2 (str): selected time column of second dataset
        multi_forecast_children (list): container for the forecast figure
        multi_frequency_dropdown (str): selected frequency value
        scenario_data (list): artifical future data for the second dataset (needed for multivariate forecast with Prophet)
        selected_country (str): selected country of country dropdown

    Raises:
        exceptions.PreventUpdate: Update prevented until both datasets loaded, feature columns selected and artifical data is available

    Returns:
        tuple:
    """

    if (
        dataset_1
        and dataset_2
        and feature_dropdown_1
        and feature_dropdown_2
        and selected_model
        and selected_country
        and geo_dropdown_1
        and geo_dropdown_2
    ) and "Multivariate Forecast" in visibility_checklist:

        columns = {
            "Dataset 1": (
                dataset_1,
                geo_dropdown_1,
                time_dropdown_1,
                feature_dropdown_1,
            ),
            "Dataset 2": (
                dataset_2,
                geo_dropdown_2,
                time_dropdown_2,
                feature_dropdown_2,
            ),
        }

        if selected_dataset and selected_model == "Prophet":
            file_1 = [key for key in columns if key in selected_dataset][0]
            file_2 = [key for key in columns if key not in selected_dataset][0]
        else:
            file_1 = "Dataset 1"
            file_2 = "Dataset 2"

        df_1 = pd.read_json(columns[file_1][0])
        df_2 = pd.read_json(columns[file_2][0])

        filtered_df_1 = df_1[df_1[columns[file_1][1]] == selected_country][
            [columns[file_1][2], columns[file_1][3]]
        ]

        filtered_df_2 = df_2[df_2[columns[file_2][1]] == selected_country][
            [columns[file_2][2], columns[file_2][3]]
        ]

        last_five_datapoints = no_update

        if selected_model == "Vector AR":

            if not var_slider_value:
                var_slider_value = 1

            if not max_lags_parameter:
                max_lags_parameter = 1

            forecast, marks = var_fit_and_predict(
                filtered_df_1,
                filtered_df_2,
                time_dropdown_1,
                time_dropdown_2,
                feature_dropdown_1,
                feature_dropdown_2,
                max_lags_parameter,
                var_slider_value,
                multi_frequency_dropdown,
            )

            fig = create_var_forecast_plot(
                forecast,
                feature_dropdown_1,
                feature_dropdown_2,
                time_dropdown_1,
                var_slider_value,
            )

            var_slider_style = {"display": "block"}
            var_lags_style = {
                "padding-left": "15px",
                "margin-top": "10px",
                "display": "block",
            }
            alpha_div_style = {
                "padding-left": "15px",
                "margin-top": "10px",
                "display": "none",
            }
            scenario_div_style = {
                "padding-left": "15px",
                "margin-top": "10px",
                "display": "none",
            }
        elif selected_model == "HW Smoothing":
            if not var_slider_value:
                var_slider_value = 1

            if not max_lags_parameter:
                max_lags_parameter = 1

            if not alpha_parameter:
                alpha_parameter = 0.5

            forecast, marks = hw_es_fit_and_predict(
                filtered_df_1,
                filtered_df_2,
                time_dropdown_1,
                time_dropdown_2,
                feature_dropdown_1,
                feature_dropdown_2,
                multi_frequency_dropdown,
                var_slider_value,
                alpha_parameter,
            )

            fig = create_var_forecast_plot(
                forecast,
                feature_dropdown_1,
                feature_dropdown_2,
                time_dropdown_1,
                var_slider_value,
            )

            var_slider_style = {"display": "block"}
            var_lags_style = {"display": "none"}
            alpha_div_style = {
                "padding-left": "15px",
                "margin-top": "10px",
                "display": "block",
            }
            scenario_div_style = {
                "padding-left": "15px",
                "margin-top": "10px",
                "display": "none",
            }

        elif selected_model == "Prophet":
            forecast_data_selector_options = {
                "Dataset 1": f"{filename_1} ({feature_dropdown_1})",
                "Dataset 2": f"{filename_2} ({feature_dropdown_2})",
            }

            marks = no_update
            if scenario_data:
                forecast, merged_df, future_df = prophet_fit_and_predict_multi(
                    filtered_df_1,
                    filtered_df_2,
                    columns[file_1][2],
                    columns[file_2][2],
                    columns[file_1][3],
                    columns[file_2][3],
                    scenario_data,
                    multi_frequency_dropdown,
                )

                fig = create_multivariate_forecast(
                    forecast,
                    merged_df,
                    future_df,
                    columns[file_1][3],
                    columns[file_2][3],
                )
            else:
                merged_df, _ = merge_dataframes(
                    filtered_df_1, filtered_df_2, columns[file_1][2], columns[file_2][2]
                )

                last_five_datapoints = merged_df.iloc[::-1].round(2).to_dict("records")
            var_slider_style = {"display": "none"}
            var_lags_style = {"display": "none"}
            alpha_div_style = {
                "padding-left": "15px",
                "margin-top": "10px",
                "display": "none",
            }
            scenario_div_style = {
                "padding-left": "15px",
                "margin-top": "15px",
                "display": "flex",
            }

        if multi_forecast_children:
            multi_forecast_children.clear()

        if (
            (selected_model == "Prophet" and scenario_data)
            or selected_model == "Vector AR"
            or selected_model == "HW Smoothing"
        ):
            multi_forecast_children.append(dcc.Graph(figure=fig))

        multi_forecast_div_style = {"display": "block"}

        return (
            multi_forecast_children,
            var_slider_style,
            scenario_div_style,
            marks,
            multi_forecast_div_style,
            var_lags_style,
            alpha_div_style,
            forecast_data_selector_options,
            last_five_datapoints,
        )
    elif (
        dataset_1
        and dataset_2
        and feature_dropdown_1
        and feature_dropdown_2
        and "Multivariate Forecast" in visibility_checklist
    ):

        multi_forecast_div_style = {"display": "block"}

        return (
            multi_forecast_children,
            no_update,
            no_update,
            no_update,
            multi_forecast_div_style,
            no_update,
            no_update,
            no_update,
            no_update,
        )

    else:

        multi_forecast_div_style = {"display": "none"}

        return (
            multi_forecast_children,
            no_update,
            no_update,
            no_update,
            multi_forecast_div_style,
            no_update,
            no_update,
            no_update,
            no_update,
        )


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
