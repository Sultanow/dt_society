import dash_daq as daq
from dash import (
    ALL,
    MATCH,
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

from aio_components.filepreprocessing import FilePreProcessingAIO
from aio_components.stats import StatAIO
from aio_components.parameters import ParameterStoreAIO
from aio_components.figure import FigureAIO

from helpers.plots import (
    create_multi_line_plot,
    create_choropleth_plot,
    create_choropleth_slider_plot,
    create_two_line_plot,
    create_correlation_heatmap,
    create_forecast_plot,
    create_var_forecast_plot_multi,
    create_multivariate_forecast_prophet,
)
from helpers.models import (
    prophet_fit_and_predict,
    fit_and_predict,
    var_fit_and_predict_multi,
    hw_es_fit_and_predict_multi,
    prophet_fit_and_predict_n,
)
from helpers.layout import (
    preprocess_dataset,
    get_year_and_country_options_stats,
    get_time_marks,
    compute_stats,
    compute_growth_rate,
    export_settings,
)

from preprocessing.parse import merge_dataframes_multi

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
                        FilePreProcessingAIO(0),
                        FilePreProcessingAIO(1),
                    ],
                    id="files-container",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            "Visible dataset",
                                            style={
                                                "margin-left": "10px",
                                                "margin-bottom": "10px",
                                                "font-weight": "bold",
                                            },
                                        ),
                                        dcc.RadioItems(
                                            options=[
                                                {
                                                    "label": "Dataset 1",
                                                    "value": 0,
                                                },
                                                {
                                                    "label": "Dataset 2",
                                                    "value": 1,
                                                },
                                            ],
                                            value=0,
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
                                            "Add File",
                                            id="add-file-button",
                                            n_clicks=1,
                                            style={
                                                "border-color": "#5c6cfa",
                                                "width": "120px",
                                                "margin-right": "40px",
                                                "float": "none",
                                            },
                                        ),
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
                html.Div(
                    [
                        html.Div(
                            "Hide/show sections",
                            style={"font-weight": "bold", "margin-left": "10px"},
                        ),
                        dcc.Checklist(
                            [
                                "Table",
                                "Stats",
                                "Timeline",
                                "Map",
                                "Correlation",
                                "Forecast",
                            ],
                            value=[
                                "Table",
                                "Stats",
                                "Timeline",
                                "Map",
                                "Correlation",
                                "Forecast",
                            ],
                            labelStyle={
                                "margin-left": "10px",
                                "font-weight": "lighter",
                                "font-size": "14px",
                                "padding-bottom": "5px",
                            },
                            inline=True,
                            id="visibility-checklist",
                            style={"padding-top": "5px", "padding-bottom": "5px"},
                        ),
                    ],
                    style={"margin-bottom": "5px"},
                ),
            ],
            style={
                "backgroundColor": "#111111",
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
                                    style_cell={"padding": "5px", "textAlign": "left"},
                                    style_header={
                                        "backgroundColor": "#454545",
                                        "border": "solid 1px #5c6cfa",
                                    },
                                    fixed_rows={"headers": True},
                                    style_table={
                                        "overflowY": "auto",
                                        "height": "250px",
                                    },
                                )
                            ],
                        ),
                    ],
                    style={
                        "backgroundColor": "#5c6cfa",
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
                                StatAIO("Mean"),
                                StatAIO("Max"),
                                StatAIO("Min"),
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
                dcc.Tabs(
                    [
                        dcc.Tab(
                            style={
                                "background-color": "#111111",
                                "border-left": "0px",
                                "border-right": "0px",
                                "border-bottom": "0px",
                                "border-radius": "0px",
                                "border-top": "0px",
                            },
                            selected_style={
                                "background-color": "#111111",
                                "color": "white",
                                "border-left": "0px",
                                "border-right": "0px",
                                "border-bottom": "0px",
                                "border-radius": "0px",
                            },
                            label="Feature correlation",
                            children=[
                                html.Div(
                                    [
                                        html.Hr(
                                            style={
                                                "padding": "0px",
                                                "margin": "0px",
                                                "border-color": "#2f2f2f",
                                                "backgroundColor": "#2f2f2f",
                                            }
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Country",
                                                    style={
                                                        "padding-top": "15px",
                                                        "padding-bottom": "15px",
                                                        "padding-right": "15px",
                                                    },
                                                ),
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
                                                    },
                                                ),
                                            ],
                                            style={"margin-left": "10px"},
                                        ),
                                    ],
                                    style={"margin-left": "10px"},
                                ),
                                dcc.Loading(
                                    type="circle",
                                    children=[
                                        html.Div(
                                            html.Div(
                                                [],
                                                id="heatmap-plot-div",
                                                style={
                                                    "display": "inline-block",
                                                    "width": "100%",
                                                },
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        dcc.Tab(
                            id="compare-div",
                            style={
                                "background-color": "#111111",
                                "border-left": "0px",
                                "border-right": "0px",
                                "border-bottom": "0px",
                                "border-radius": "0px",
                                "border-top": "0px",
                            },
                            selected_style={
                                "background-color": "#111111",
                                "color": "white",
                                "border-left": "0px",
                                "border-right": "0px",
                                "border-bottom": "0px",
                                "border-radius": "0px",
                            },
                            label="Dataset correlation",
                            children=[
                                html.Div(
                                    [
                                        html.Hr(
                                            style={
                                                "padding": "0px",
                                                "margin": "0px",
                                                "border-color": "#2f2f2f",
                                                "backgroundColor": "#2f2f2f",
                                            }
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Country",
                                                    style={
                                                        "padding-top": "15px",
                                                        "padding-bottom": "15px",
                                                        "padding-right": "15px",
                                                    },
                                                ),
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
                                                    },
                                                ),
                                            ],
                                            style={"margin-left": "10px"},
                                        ),
                                    ],
                                    style={"margin-left": "10px"},
                                ),
                                html.Div(
                                    dcc.Loading(
                                        type="circle",
                                        children=[
                                            html.Div(
                                                [],
                                                id="max_country-comparison-div",
                                                style={
                                                    "display": "inline-block",
                                                    "width": "100%",
                                                },
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ]
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
                dcc.Tabs(
                    [
                        dcc.Tab(
                            style={
                                "background-color": "#111111",
                                "border-left": "0px",
                                "border-right": "0px",
                                "border-bottom": "0px",
                                "border-radius": "0px",
                                "border-top": "0px",
                            },
                            selected_style={
                                "background-color": "#111111",
                                "color": "white",
                                "border-left": "0px",
                                "border-right": "0px",
                                "border-bottom": "0px",
                                "border-radius": "0px",
                            },
                            label="Univariate Forecast",
                            children=[
                                html.Div(
                                    [
                                        html.Hr(
                                            style={
                                                "padding": "0px",
                                                "margin": "0px",
                                                "border-color": "#2f2f2f",
                                                "backgroundColor": "#2f2f2f",
                                            }
                                        ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Time frequency",
                                                    style={
                                                        "padding-top": "15px",
                                                        "padding-bottom": "15px",
                                                        "padding-right": "15px",
                                                    },
                                                ),
                                                dcc.Dropdown(
                                                    [
                                                        "Yearly",
                                                        "Monthly",
                                                        "Weekly",
                                                        "Daily",
                                                    ],
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
                                            ],
                                            style={"margin-left": "10px"},
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Model",
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
                                            ],
                                            style={"margin-left": "10px"},
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Country",
                                                    style={
                                                        "padding-top": "15px",
                                                        "padding-bottom": "15px",
                                                        "padding-right": "15px",
                                                    },
                                                ),
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
                                                    },
                                                ),
                                            ],
                                            style={"margin-left": "10px"},
                                        ),
                                    ],
                                    style={"display": "flex", "margin-left": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Set future prediction",
                                            style={"padding": "15px"},
                                        ),
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
                                                style={
                                                    "display": "inline-block",
                                                    "width": "100%",
                                                },
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        dcc.Tab(
                            id="multi-forecast-div",
                            style={
                                "background-color": "#111111",
                                "border-left": "0px",
                                "border-right": "0px",
                                "border-bottom": "0px",
                                "border-radius": "0px",
                                "border-top": "0px",
                            },
                            selected_style={
                                "background-color": "#111111",
                                "color": "white",
                                "border-left": "0px",
                                "border-right": "0px",
                                "border-bottom": "0px",
                                "border-radius": "0px",
                            },
                            label="Multivariate Forecast",
                            children=[
                                html.Div(
                                    [
                                        html.Hr(
                                            style={
                                                "padding": "0px",
                                                "margin": "0px",
                                                "border-color": "#2f2f2f",
                                                "backgroundColor": "#2f2f2f",
                                            }
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            "Time frequency",
                                                            style={
                                                                "padding-top": "15px",
                                                                "padding-bottom": "15px",
                                                                "padding-right": "15px",
                                                            },
                                                        ),
                                                        dcc.Dropdown(
                                                            [
                                                                "Yearly",
                                                                "Monthly",
                                                                "Weekly",
                                                                "Daily",
                                                            ],
                                                            placeholder="Select frequency",
                                                            clearable=False,
                                                            id="multi-frequency-dropdown-forecast",
                                                            style={
                                                                "width": "140px",
                                                                "font-size": "14px",
                                                                "border-color": "#5c6cfa",
                                                                "background-color": "#111111",
                                                            },
                                                        ),
                                                    ],
                                                    style={"margin-left": "10px"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            "Model",
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
                                                    ],
                                                    style={"margin-left": "10px"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            "Country",
                                                            style={
                                                                "padding-top": "15px",
                                                                "padding-bottom": "15px",
                                                                "padding-right": "15px",
                                                            },
                                                        ),
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
                                                            },
                                                        ),
                                                    ],
                                                    style={"margin-left": "10px"},
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "margin-left": "10px",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Set future prediction",
                                                    style={"padding": "15px"},
                                                ),
                                                dcc.Slider(
                                                    1, 30, 1, id="var-forecast-slider"
                                                ),
                                            ],
                                            id="var-slider-div",
                                            style={"display": "none"},
                                        ),
                                        ParameterStoreAIO(
                                            parameter="max_lags",
                                            value=1,
                                            min=1,
                                            max=7,
                                            step=1,
                                            type="number",
                                        ),
                                        ParameterStoreAIO(
                                            parameter="\u03B1",
                                            value=0.5,
                                            min=1e-4,
                                            max=1 - 1e-4,
                                            step=1e-4,
                                            type="number",
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            "Select dependent dataset"
                                                        ),
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
                                                        ParameterStoreAIO(
                                                            parameter="scenario",
                                                            type="text",
                                                            display="block",
                                                        ),
                                                    ],
                                                    id="scenario-container",
                                                ),
                                                html.Div(
                                                    [
                                                        dash_table.DataTable(
                                                            id="forecast-data-table",
                                                            style_data={
                                                                "backgroundColor": "#232323",
                                                                "border": "solid 1px #5c6cfa",
                                                            },
                                                            style_cell={
                                                                "padding": "5px",
                                                                "textAlign": "left",
                                                            },
                                                            style_header={
                                                                "backgroundColor": "#454545",
                                                                "border": "solid 1px #5c6cfa",
                                                            },
                                                            fixed_rows={
                                                                "headers": True
                                                            },
                                                            style_table={
                                                                "overflowY": "auto",
                                                                "height": "175px",
                                                            },
                                                        ),
                                                    ],
                                                    style={
                                                        "margin-left": "auto",
                                                        "float": "right",
                                                        "margin-right": "20px",
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
                        ),
                    ],
                ),
            ],
            # id="multi-forecast-div",
            id="trend-div",
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
    Output("files-container", "children"),
    Output("data-selector", "options"),
    Output("scenario-container", "children"),
    Input("add-file-button", "n_clicks"),
    State("files-container", "children"),
    State("data-selector", "options"),
    State("scenario-container", "children"),
    State(
        {
            "component": "ParameterStoreAIO",
            "subcomponent": "container",
            "aio_id": "scenario",
        },
        "children",
    ),
)
def add_file(
    add_file_button_clicks,
    files_container,
    data_selector,
    scenario_container: list,
    comp,
):

    changed_item = [p["prop_id"] for p in callback_context.triggered][0]

    if "add-file-button" in changed_item:
        files_container.append(FilePreProcessingAIO(add_file_button_clicks))
        data_selector.append(
            {
                "label": f"Dataset {add_file_button_clicks+1}",
                "value": add_file_button_clicks,
            }
        )

        store = {
            "component": "ParameterStoreAIO",
            "subcomponent": "store",
            "store_no": add_file_button_clicks,
            "aio_id": "scenario",
        }

        input = {
            "component": "ParameterStoreAIO",
            "subcomponent": f"input",
            "input_no": add_file_button_clicks,
            "aio_id": "scenario",
        }

        comp.insert(
            -1,
            dcc.Input(
                id=input,
                type="text",
                style={
                    "backgroundColor": "#111111",
                    "color": "#f2f2f2",
                    "padding": "10px",
                    "border-top": "0px",
                    "border-left": "0px",
                    "border-right": "0px",
                    "border-color": "#5c6cfa",
                    "width": "300px",
                    "display": "block",
                },
            ),
        )
        comp.insert(-1, dcc.Store(id=store))

        scenario_container.pop()
        scenario_container.extend(comp)

        return files_container, data_selector, scenario_container

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("data-selector", "style"),
    Output("data-selector-div", "style"),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "store",
            "aio_id": ALL,
        },
        "data",
    ),
)
def update_selector_visibility(dataframes: list):
    """Updates the dataset visibility toggle

    Args:
        dataframes (list): All available datasets

    Returns:
        tuple: style properties for visibility selector
    """

    loaded_datasets = [True for df in dataframes if df is not None]

    if len(loaded_datasets) > 1:
        radio_div_visibility = {
            "display": "block",
            "padding-bottom": "10px",
            "padding-left": "5px",
        }

        selector_visibility = {"display": "block", "padding-left": "5px"}
    else:
        radio_div_visibility = {"display": "none"}
        selector_visibility = {"display": "none"}

    return radio_div_visibility, selector_visibility


@app.callback(
    Output("country-dropdown", "options"),
    Output("country-dropdown", "value"),
    Output("country-dropdown-multi-forecast", "options"),
    Output("country-dropdown-multi-forecast", "value"),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "store",
            "aio_id": ALL,
        },
        "data",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "geo_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
)
def update_country_dropdown_comparison(
    dataframes: list,
    geo_dropdowns: list,
):
    """Fills the dropdown in correlation section with countries that occur in both datasets

    Args:
        dataframes (list): All available dataframes
        geo_dropdowns (list): Selected geo-column values

    Raises:
        exceptions.PreventUpdate: Update prevented unless both datasets and geo-columns are available

    Returns:
        tuple: country intersection
    """

    if not any(x is None for x in dataframes + geo_dropdowns):
        countries_per_df = []

        for i, df in enumerate(dataframes):
            countries = pd.read_json(df)[geo_dropdowns[i]].unique()
            countries_per_df.append(set(countries))

        country_intersection = list(set.intersection(*countries_per_df))

        country_intersection.sort()

        return (
            country_intersection,
            country_intersection[0],
            country_intersection,
            country_intersection[0],
        )

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
    Input("data-selector", "value"),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "store",
            "aio_id": ALL,
        },
        "data",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "time_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "geo_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
)
def update_year_and_country_dropdown_stats(
    selected_dataset: str,
    dataframes: list,
    time_dropdowns: list,
    geo_dropdowns: list,
) -> tuple:
    """Fills dropdown in stats section with available years in the selected dataset

    Args:
        selected_dataset (str): value of the selected dataset
        dataframes (list): available dataframes
        time_dropdowns (list): Selected time-column values
        geo_dropdowns (list): Selected geo-column values

    Raises:
        exceptions.PreventUpdate: prevents update if no dataset is available and no dataset is selected

    Returns:
        tuple: available years, first year value, available countries, first country value, available years, first year value
    """

    time_column = time_dropdowns[selected_dataset]
    geo_column = geo_dropdowns[selected_dataset]
    data = dataframes[selected_dataset]

    if time_column and geo_column and data:

        df = pd.read_json(data)

        return get_year_and_country_options_stats(
            df, geo_column=geo_column, time_column=time_column
        )
    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("data-table", "data"),
    Output("table-div", "style"),
    Input("data-selector", "value"),
    Input("visibility-checklist", "value"),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "store",
            "aio_id": ALL,
        },
        "data",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "separator_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
)
def update_table_content(
    selected_dataset: str,
    visibility_checklist: list,
    dataframes: list,
    separators: list,
) -> pd.DataFrame:
    """Fills table section with data from the selected dataset

    Args:
        selected_dataset (str): value of selected dataset
        visibility_checklist (list): list of displayed sections
        dataframes (list): available dataframes
        separators (list): selected seperators for each dataset

    Raises:
        exceptions.PreventUpdate: update prevented if no dataset is available

    Returns:
        pd.DataFrame: Dataframe of selected dataset
    """

    data = dataframes[selected_dataset]
    sep = separators[selected_dataset]

    if (data and sep) and "Table" in visibility_checklist:

        df = pd.read_json(data).round(2).to_dict("records")

        table_div_style = {"backroundColor": "#ffffff", "display": "block"}

        return df, table_div_style

    else:
        table_div_style = {"display": "none"}
        return no_update, table_div_style


@app.callback(
    Output(StatAIO.ids.stat("Mean"), "children"),
    Output(StatAIO.ids.stat("Max"), "children"),
    Output(StatAIO.ids.stat("Min"), "children"),
    Output("growth-stat", "children"),
    Output("stats-div", "style"),
    Input("data-selector", "value"),
    State(StatAIO.ids.stat("Mean"), "children"),
    State(StatAIO.ids.stat("Max"), "children"),
    State(StatAIO.ids.stat("Min"), "children"),
    State("growth-stat", "children"),
    Input("year-dropdown-stats", "value"),
    Input("country-dropdown-stats", "value"),
    [Input("year-range-slider", "value")],
    Input("visibility-checklist", "value"),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "store",
            "aio_id": ALL,
        },
        "data",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "feature_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "time_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "geo_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
)
def update_stats(
    selected_dataset: str,
    avg_stat_children: list,
    max_stat_children: list,
    min_stat_children: list,
    growth_stat_children: list,
    year_dropdown_stats: str,
    country_dropdown_stats: str,
    year_range: list,
    visibility_checklist: list,
    dataframes,
    feature_dropdowns,
    time_dropdowns,
    geo_dropdowns,
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

    time_column = time_dropdowns[selected_dataset]
    feature_column = feature_dropdowns[selected_dataset]
    geo_column = geo_dropdowns[selected_dataset]
    data = dataframes[selected_dataset]

    if (
        time_column and feature_column and geo_column and data
    ) and "Stats" in visibility_checklist:

        df = pd.read_json(data)

        year = year_dropdown_stats

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
    State("line-div", "children"),
    Input("data-selector", "value"),
    Input("visibility-checklist", "value"),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "store",
            "aio_id": ALL,
        },
        "data",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "feature_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "time_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "geo_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
)
def update_line_plot(
    timeline_children: list,
    selected_dataset: str,
    visibility_checklist: list,
    dataframes,
    feature_dropdowns,
    time_dropdowns,
    geo_dropdowns,
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

    time_column = time_dropdowns[selected_dataset]
    feature_column = feature_dropdowns[selected_dataset]
    geo_column = geo_dropdowns[selected_dataset]
    data = dataframes[selected_dataset]

    if (
        time_column and feature_column and geo_column and data
    ) and "Timeline" in visibility_checklist:

        df = pd.read_json(data)

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

    elif data and time_column == "none":

        df = pd.read_json(data)
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
    State("map-div", "children"),
    Input("data-selector", "value"),
    Input("visibility-checklist", "value"),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "store",
            "aio_id": ALL,
        },
        "data",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "feature_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "time_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "geo_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
)
def update_choropleth(
    map_children: list,
    selected_dataset: str,
    visiblity_checklist: list,
    dataframes,
    feature_dropdowns,
    time_dropdowns,
    geo_dropdowns,
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

    time_column = time_dropdowns[selected_dataset]
    feature_column = feature_dropdowns[selected_dataset]
    geo_column = geo_dropdowns[selected_dataset]
    data = dataframes[selected_dataset]

    if (
        time_column and feature_column and geo_column and data
    ) and "Map" in visiblity_checklist:

        df = pd.read_json(data)

        # mapbox choropleth disabled for now
        #
        # filtered_df = df[df[time_column] == selected_year_map]
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
    Input("country-dropdown", "value"),
    State("max_country-comparison-div", "children"),
    Input("visibility-checklist", "value"),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "store",
            "aio_id": ALL,
        },
        "data",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "feature_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "time_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "geo_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
)
def update_max_country_compare(
    selected_country: str,
    comparison_children: str,
    visibility_checklist: list,
    dataframes,
    feature_dropdowns,
    time_dropdowns,
    geo_dropdowns,
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
        not any(
            x is None
            for x in dataframes + feature_dropdowns + time_dropdowns + geo_dropdowns
        )
    ) and "Correlation" in visibility_checklist:

        dfs = []

        for i, data in enumerate(dataframes):
            df = pd.read_json(data)
            df_by_country = df[df[geo_dropdowns[i]] == selected_country]

            dfs.append(df_by_country)

        fig = create_two_line_plot(
            dfs,
            feature_dropdowns,
            time_dropdowns,
        )

        comparison_children.clear()

        comparison_children.append(dcc.Graph(figure=fig))

        compare_div_style = {
            "display": "block",
            "background-color": "#111111",
            "border-left": "0px",
            "border-right": "0px",
            "border-bottom": "0px",
            "border-radius": "0px",
            "border-top": "0px",
        }

        return comparison_children, compare_div_style
    else:
        compare_div_style = {"display": "none"}

        return comparison_children, compare_div_style


@app.callback(
    Output("forecast-slider", "marks"),
    Output("forecast-slider-div", "style"),
    Input("data-selector", "value"),
    Input("frequency-dropdown-forecast", "value"),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "store",
            "aio_id": ALL,
        },
        "data",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "time_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
)
def update_forecast_slider(
    selected_dataset: str,
    frequency_dropdown: str,
    dataframes: str,
    time_dropdowns: str,
):

    time_column = time_dropdowns[selected_dataset]
    data = dataframes[selected_dataset]

    if time_column and data and frequency_dropdown:

        df = pd.read_json(data)

        marks = get_time_marks(df, time_column, frequency_dropdown)

        slider_visibility = {"display": "block"}

        return marks, slider_visibility

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("fit-plot-div", "children"),
    Output("trend-div", "style"),
    Input("data-selector", "value"),
    State("fit-plot-div", "children"),
    Input("country-dropdown-forecast", "value"),
    Input("forecast-slider", "value"),
    Input("frequency-dropdown-forecast", "value"),
    Input("model-dropdown-forecast", "value"),
    Input("visibility-checklist", "value"),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "store",
            "aio_id": ALL,
        },
        "data",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "feature_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "time_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "geo_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
)
def update_forecast(
    selected_dataset: str,
    fit_plot_children: list,
    country_dropdown: str,
    forecast_slider_value: str,
    frequency_dropdown: str,
    model_dropdown: str,
    visibility_checklist: list,
    dataframes,
    feature_dropdowns,
    time_dropdowns,
    geo_dropdowns,
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

    time_column = time_dropdowns[selected_dataset]
    feature_column = feature_dropdowns[selected_dataset]
    geo_column = geo_dropdowns[selected_dataset]
    data = dataframes[selected_dataset]

    if (
        time_column
        and feature_column
        and geo_column
        and data
        and frequency_dropdown
        and model_dropdown
    ) and "Forecast" in visibility_checklist:

        df = pd.read_json(data)

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
        feature_column and geo_column and data
    ) and "Forecast" in visibility_checklist:

        forecast_div_style = {"display": "block"}

        return fit_plot_children, forecast_div_style

    else:
        forecast_div_style = {"display": "none"}

        return fit_plot_children, forecast_div_style


@app.callback(
    Output("heatmap-plot-div", "children"),
    Output("heatmap-div", "style"),
    Input("data-selector", "value"),
    State("heatmap-plot-div", "children"),
    Input("country-dropdown-corr", "value"),
    Input("visibility-checklist", "value"),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "store",
            "aio_id": ALL,
        },
        "data",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "feature_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "time_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "geo_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
)
def update_heatmap(
    selected_dataset: str,
    heatmap_children: list,
    country_dropdown: str,
    visibility_checklist: list,
    dataframes,
    feature_dropdowns,
    time_dropdowns,
    geo_dropdowns,
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

    time_column = time_dropdowns[selected_dataset]
    feature_column = feature_dropdowns[selected_dataset]
    geo_column = geo_dropdowns[selected_dataset]
    data = dataframes[selected_dataset]

    if (
        time_column and feature_column and geo_column and data
    ) and "Correlation" in visibility_checklist:

        df = pd.read_json(data)

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
    Output("multi-fit-plot-div", "children"),
    Output("var-slider-div", "style"),
    Output("scenario-div", "style"),
    Output("var-forecast-slider", "marks"),
    Output("multi-forecast-div", "style"),
    Output(ParameterStoreAIO.ids.container("max_lags"), "style"),
    Output(ParameterStoreAIO.ids.container("\u03B1"), "style"),
    Output("forecast-data-selector", "options"),
    Output("forecast-data-table", "data"),
    Output(
        {
            "component": "ParameterStoreAIO",
            "subcomponent": "input",
            "input_no": ALL,
            "aio_id": "scenario",
        },
        "placeholder",
    ),
    State("multi-fit-plot-div", "children"),
    Input("multi-frequency-dropdown-forecast", "value"),
    Input(ParameterStoreAIO.ids.store("scenario"), "data"),
    Input("country-dropdown-multi-forecast", "value"),
    Input("model-dropdown-multi-forecast", "value"),
    Input("var-forecast-slider", "value"),
    Input(ParameterStoreAIO.ids.store("\u03B1"), "data"),
    Input(ParameterStoreAIO.ids.store("max_lags"), "data"),
    Input("forecast-data-selector", "options"),
    Input("forecast-data-selector", "value"),
    Input("visibility-checklist", "value"),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "store",
            "aio_id": ALL,
        },
        "data",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "feature_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "time_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "geo_dropdown",
            "aio_id": ALL,
        },
        "value",
    ),
    Input(
        {
            "component": "FilePreProcessingAIO",
            "subcomponent": "file_upload",
            "aio_id": ALL,
        },
        "filename",
    ),
    Input(
        {
            "component": "ParameterStoreAIO",
            "subcomponent": "store",
            "store_no": ALL,
            "aio_id": "scenario",
        },
        "data",
    ),
)
def update_multivariate_forecast(
    multi_forecast_children: list,
    multi_frequency_dropdown: str,
    scenario_data: list,
    selected_country: str,
    selected_model: str,
    var_slider_value: int,
    alpha_parameter: int,
    max_lags_parameter: int,
    forecast_data_selector_options: str,
    selected_dataset: str,
    visibility_checklist: list,
    dataframes,
    feature_dropdowns,
    time_dropdowns,
    geo_dropdowns,
    filenames,
    scenarios_data,
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

    placeholders = [no_update for _ in range(len(feature_dropdowns) - 1)]

    if (
        not any(
            x is None
            for x in dataframes + feature_dropdowns + time_dropdowns + geo_dropdowns
        )
        and selected_model
        and selected_country
    ) and "Forecast" in visibility_checklist:

        filtered_dfs = []
        for i, df in enumerate(dataframes):
            df = pd.read_json(df)
            filtered_df = df[df[geo_dropdowns[i]] == selected_country][
                [time_dropdowns[i], feature_dropdowns[i]]
            ]

            filtered_dfs.append(filtered_df)

        last_five_datapoints = no_update

        if selected_model == "Vector AR":

            if not var_slider_value:
                var_slider_value = 1

            if not max_lags_parameter:
                max_lags_parameter = 1

            forecast, marks = var_fit_and_predict_multi(
                filtered_dfs,
                time_dropdowns,
                feature_dropdowns,
                max_lags=max_lags_parameter,
                periods=var_slider_value,
                frequency=multi_frequency_dropdown,
            )

            fig = create_var_forecast_plot_multi(
                forecast, feature_dropdowns, time_dropdowns[-1], var_slider_value
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

            forecast, marks = hw_es_fit_and_predict_multi(
                filtered_dfs,
                time_dropdowns,
                feature_dropdowns,
                multi_frequency_dropdown,
                var_slider_value,
                alpha_parameter,
            )

            fig = create_var_forecast_plot_multi(
                forecast, feature_dropdowns, time_dropdowns[-1], var_slider_value
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
            forecast_data_selector_options = [
                {"label": f"{file} ({feature})", "value": n}
                for n, (file, feature) in enumerate(zip(filenames, feature_dropdowns))
            ]

            if selected_dataset is not None:

                placeholders = [
                    feature
                    for i, feature in enumerate(feature_dropdowns)
                    if i != selected_dataset
                ]

            marks = no_update
            if not any(scenario is None for scenario in scenarios_data):

                forecast, merged_df, future_df, y_feature = prophet_fit_and_predict_n(
                    filtered_dfs,
                    time_dropdowns,
                    feature_dropdowns,
                    scenarios=scenarios_data,
                    frequency=multi_frequency_dropdown,
                    y_feature_index=selected_dataset,
                )

                fig = create_multivariate_forecast_prophet(
                    forecast, merged_df, future_df, y_feature, feature_dropdowns
                )

            else:
                merged_df, _ = merge_dataframes_multi(
                    filtered_dfs,
                    time_dropdowns,
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
            (
                selected_model == "Prophet"
                and not any(scenario is None for scenario in scenarios_data)
            )
            or selected_model == "Vector AR"
            or selected_model == "HW Smoothing"
        ):
            multi_forecast_children.append(dcc.Graph(figure=fig))

        multi_forecast_div_style = {
            "display": "block",
            "background-color": "#111111",
            "border-left": "0px",
            "border-right": "0px",
            "border-bottom": "0px",
            "border-radius": "0px",
            "border-top": "0px",
        }

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
            placeholders,
        )
    elif (
        not any(x is None for x in dataframes + feature_dropdowns)
        and "Forecast" in visibility_checklist
    ):

        multi_forecast_div_style = {
            "display": "block",
            "background-color": "#111111",
            "border-left": "0px",
            "border-right": "0px",
            "border-bottom": "0px",
            "border-radius": "0px",
            "border-top": "0px",
        }

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
            placeholders,
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
            placeholders,
        )


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
