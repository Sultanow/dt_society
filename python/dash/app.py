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
)
import pandas as pd

from helpers.plots import (
    create_multi_line_plot,
    create_choropleth_plot,
    create_two_line_plot,
    create_correlation_heatmap,
    create_forecast_plot,
)
from helpers.models import prophet_fit_and_predict
from helpers.layout import (
    preprocess_dataset,
    get_year_and_country_options_stats,
    compute_stats,
    compute_growth_rate,
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
                                        dcc.Store(id="dataset"),
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
                                        dcc.Store(id="dataset-2"),
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
                                                        "margin": "10px",
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
                                                "padding": "20px",
                                                "margin-bottom": "50px",
                                            },
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
                                    style={"display": "flex"},
                                ),
                            ],
                            style={
                                # "margin-top": "20px",
                            },
                        ),
                    ],
                    style={
                        "backgroundColor": "#111111",
                    },
                ),
            ],
            style={
                "backgroundColor": "#232323",
                "height": "300px",
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
                        "max-height": "250px",
                    },
                ),
            ],
            style={
                "backroundColor": "#ffffff",
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
                            "Time unit window for growth rate",
                            style={"padding": "15px"},
                        ),
                        dcc.RangeSlider(
                            0, 20, step=1, id="year-range-slider", allowCross=False
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
                                                        "width": "140px",
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
                                                "height": "100px",
                                                "width": "100%",
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
                                                "font-size": "14px",
                                                "border-top": "0px",
                                                "border-left": "0px",
                                                "border-right": "0px",
                                                "border-bottom": "0px",
                                                "backgroundColor": "#111111",
                                                "border-color": "#5c6cfa",
                                                "border-radius": "0px",
                                                "padding-top": "1.5px",
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
                    html.Div(
                        [],
                        id="max_country-comparison-div",
                        style={"display": "inline-block", "width": "100%"},
                    ),
                ),
            ],
            id="compare-div",
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
                html.Div(
                    html.Div(
                        [],
                        id="heatmap-plot-div",
                        style={"display": "inline-block", "width": "100%"},
                    ),
                ),
            ],
            id="heatmap-div",
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
                                    "Trend forecast",
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
                html.Div("Set amount of future time units", style={"padding": "15px"}),
                dcc.Slider(1, 25, 1, id="forecast-slider"),
                html.Div(
                    html.Div(
                        [],
                        id="fit-plot-div",
                        style={"display": "inline-block", "width": "100%"},
                    ),
                ),
                html.Div(
                    html.Div(
                        [],
                        id="forecast-plot-div",
                        style={"display": "inline-block", "width": "100%"},
                    ),
                ),
            ],
            id="trend-div",
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
    Input("delimiter-dropdown-1", "value"),
    Input("geo-dropdown-1", "value"),
    Input("table-upload", "contents"),
    Input("table-upload", "filename"),
    Input("reshape-dropdown-1", "value"),
    Input("reshape-switch-1", "on"),
    State("table-upload", "children"),
    Input("demo-button", "n_clicks"),
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
):

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
    Output("data-selector", "style"),
    Output("data-selector-div", "style"),
    Output("compare-div", "style"),
    Input("delimiter-dropdown-2", "value"),
    Input("geo-dropdown-2", "value"),
    Input("table-upload-2", "contents"),
    Input("table-upload-2", "filename"),
    Input("reshape-dropdown-2", "value"),
    Input("reshape-switch-2", "on"),
    State("table-upload-2", "children"),
    Input("demo-button", "n_clicks"),
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
):
    radio_div_visibility = {
        "display": "block",
        "padding-bottom": "10px",
        "padding-left": "5px",
    }

    selector_visibility = {"display": "block", "padding-left": "5px"}

    show_compare_dropdown = {"display": "block"}

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
        ),
        radio_div_visibility,
        selector_visibility,
        show_compare_dropdown,
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

        filtered_df_by_country = df[(df[geo_column] == country_dropdown_stats)]

        mean, max, min, max_country, min_country = compute_stats(
            filtered_df, feature_column, geo_column
        )

        growth_rate = compute_growth_rate(
            filtered_df_by_country, feature_column, year_range
        )

        avg_stat_children.clear()
        avg_stat_children.append("Mean \n" + str(mean))

        max_stat_children.clear()
        max_stat_children.append("max:\n" + str(max) + " - " + max_country)

        min_stat_children.clear()
        min_stat_children.append("min: \n" + str(min) + " - " + min_country)

        growth_stat_children.clear()
        growth_stat_children.append("Growth rate:\n" + str(growth_rate) + "%")

        visiblity = {"display": "block"}

        return (
            avg_stat_children,
            max_stat_children,
            min_stat_children,
            growth_stat_children,
            visiblity,
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


@app.callback(
    Output("fit-plot-div", "children"),
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
) -> list:
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
        list: container with forecast plot
    """

    if (
        dataset
        and feature_dropdown_1
        and geo_dropdown_1
        and selected_dataset == "Dataset 1"
        and country_dropdown
    ) or (
        dataset_2
        and feature_dropdown_2
        and geo_dropdown_2
        and selected_dataset == "Dataset 2"
        and country_dropdown
    ):

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

        # model = LinearRegression()
        # model = neighbors.KNeighborsRegressor()
        # model = tree.DecisionTreeRegressor()

        df = df[df[geo_column] == country_dropdown]

        forecast, df = prophet_fit_and_predict(
            df,
            time_column=time_column,
            feature_column=feature_column,
            periods=forecast_slider_value,
        )

        fig = create_forecast_plot(
            forecast=forecast,
            df=df,
            time_column=time_column,
            feature_column=feature_column,
        )

        # x = np.expand_dims(df[time_column], axis=1)

        # y_max = df[feature_column].max()

        # model.fit(x, df[feature_column])

        # x_range = np.linspace(x.min(), x.max(), 100)
        # y_range = model.predict(x_range.reshape(-1, 1))

        # rmse = np.sqrt(mean_squared_error(df[feature_column], model.predict(x)))

        # if forecast_slider_value not in range(time_min, time_max):
        #    forecast_slider_value = time_min

        # future_years = [
        #    year for year in range(time_min, time_max) if year <= forecast_slider_value
        # ]

        # future_years = np.expand_dims(np.array(future_years), axis=1)

        # future_preds = model.predict(future_years)

        # rmse = np.repeat(rmse, future_years.squeeze().size)

        if fit_plot_children:
            fit_plot_children.clear()

        fit_plot_children.append(dcc.Graph(figure=fig))

        return fit_plot_children
    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("heatmap-plot-div", "children"),
    Input("dataset", "data"),
    Input("dataset-2", "data"),
    Input("time-dropdown-1", "value"),
    Input("time-dropdown-2", "value"),
    Input("geo-dropdown-1", "value"),
    Input("geo-dropdown-2", "value"),
    Input("data-selector", "value"),
    State("heatmap-plot-div", "children"),
    Input("country-dropdown-corr", "value"),
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
        dataset
        and time_dropdown_1
        and geo_dropdown_1
        and selected_dataset == "Dataset 1"
    ) or (
        dataset_2
        and time_dropdown_2
        and geo_dropdown_2
        and selected_dataset == "Dataset 2"
    ):

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

        return heatmap_children
    else:
        raise exceptions.PreventUpdate


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
