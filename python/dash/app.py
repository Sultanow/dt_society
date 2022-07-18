from dash import Dash, dcc, html, Input, Output, exceptions, State
import pandas as pd

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
                                    "color": "#f2f2f2",
                                }
                            ),
                        ]
                    )
                ),
                html.Div(
                    [
                        dcc.Upload(
                            id="table-upload",
                            children=html.Div(
                                ["Drag and Drop or ", html.A("Select Files")]
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
                            },
                        ),
                        dcc.Store(id="dataset"),
                    ],
                    style={
                        "display": "inline-block",
                    },
                ),
                html.Div(
                    [
                        dcc.Upload(
                            id="table-upload-2",
                            children=html.Div(
                                ["Drag and Drop or ", html.A("Select second file")]
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
                            },
                        ),
                        dcc.Store(id="dataset-2"),
                    ],
                    id="second-file-upload",
                    style={
                        "display": "inline-block",
                        "margin-left": "20px",
                    },
                ),
                html.Div(
                    [
                        dcc.RadioItems(
                            ["Dataset 1", "Dataset 2"],
                            "Dataset 1",
                            id="data-selector",
                            inline=False,
                            style={"display": "inline-block"},
                        )
                    ],
                    style={
                        "margin-top": "20px",
                        "margin-bottom": "10px",
                        "margin-left": "10px",
                    },
                ),
            ],
            # style={"box-shadow": "2px 2px 2px lightgrey"},
            # style={"margin-bottom": "100px"},
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
                                                "color": "#f2f2f2",
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
                    style={"display": "inline-block", "width": "40%"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    "Countries",
                                    style={
                                        "padding-top": "10px",
                                        "padding-left": "10px",
                                        "padding-bottom": "10px",
                                        "backgroundColor": "#111111",
                                        "font-weight": "bold",
                                        "textAlign": "center",
                                    },
                                ),
                                html.Hr(style={"padding": "0px", "margin": "0px"}),
                            ]
                        ),
                        html.Div(
                            [],
                            id="map-div",
                        ),
                    ],
                    style={
                        "display": "inline-block",
                        "width": "59%",
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
                            "Country comparison",
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
                                "color": "#f2f2f2",
                            }
                        ),
                    ]
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            ["none"],
                            placeholder="No values found",
                            clearable=False,
                            id="country-dropdown",
                            style={
                                "width": "150px",
                                "margin-top": "10px",
                                "margin-left": "5px",
                                "border-color": "#5c6cfa",
                                "background-color": "#111111",
                            },
                        ),
                    ]
                ),
                html.Div(
                    html.Div(
                        [],
                        id="country-comparison-div",
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
    },
)


@app.callback(
    Output("columns-dropdown", "options"),
    Output("dataset", "data"),
    Output("table-upload", "children"),
    Output("columns-dropdown", "value"),
    Output("second-file-upload", "style"),
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

        return filtered_cols, df, children, filtered_cols[0], show_second_file_upload

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
    Output("line-div", "children"),
    Input("category-dropdown", "value"),
    Input("columns-dropdown", "value"),
    Input("dataset", "data"),
    Input("category-dropdown-2", "value"),
    Input("columns-dropdown-2", "value"),
    Input("dataset-2", "data"),
    State("line-div", "children"),
    Input("data-selector", "value"),
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
):

    if dataframe and selected_unit and category_column != "none":

        datasets = {
            "Dataset 1": [dataframe, selected_unit, category_column],
            "Dataset 2": [dataframe_2, selected_unit_2, category_column_2],
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
)
def update_choropleth(
    selected_unit,
    category_column,
    dataframe,
    children,
    selected_unit_2,
    category_column_2,
    dataframe_2,
):

    if dataframe and selected_unit and category_column != "none":

        df = pd.read_json(dataframe)

        filtered_df = DigitalTwinTimeSeries(df=df)
        filtered_df = filtered_df.melt_data(category_column=category_column)

        filtered_df = filtered_df[selected_unit]

        if dataframe_2:

            df_2 = pd.read_json(dataframe_2)

            filtered_df_2 = DigitalTwinTimeSeries(df=df_2)
            filtered_df_2 = filtered_df_2.melt_data(category_column=category_column_2)
            filtered_df_2 = filtered_df_2[selected_unit_2]

            filtered_df["category"] = selected_unit
            filtered_df_2["category"] = selected_unit_2

            years_df, years_df_2 = tuple(
                df["year"].unique() for df in [filtered_df, filtered_df_2]
            )

            column_intersection = list(set(years_df).intersection(years_df_2))

            filtered_df = pd.concat([filtered_df, filtered_df_2])

            filtered_df = filtered_df[filtered_df["year"].isin(column_intersection)]

            fig = create_choropleth_plot(filtered_df, facet="category")
        else:

            fig = create_choropleth_plot(filtered_df)

        if children:
            children.clear()

        children.append(dcc.Graph(figure=fig))

        return children

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("country-comparison-div", "children"),
    Input("category-dropdown", "value"),
    Input("columns-dropdown", "value"),
    Input("dataset", "data"),
    Input("category-dropdown-2", "value"),
    Input("columns-dropdown-2", "value"),
    Input("country-dropdown", "value"),
    Input("dataset-2", "data"),
    State("country-comparison-div", "children"),
)
def update_country_compare(
    selected_unit,
    category_column,
    dataframe,
    selected_unit_2,
    category_column_2,
    selected_country,
    dataframe_2,
    children,
):

    if (
        selected_country
        and selected_unit_2
        and selected_unit
        and dataframe
        and dataframe_2
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
            lambda x: x[x["geo"] == selected_country].index[0],
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
