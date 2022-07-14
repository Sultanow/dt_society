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
            [
                html.Div(
                    [
                        dcc.Upload(
                            id="table-upload",
                            children=html.Div(
                                ["Drag and Drop or ", html.A("Select Files")]
                            ),
                            style={
                                "width": "50%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px",
                                "font-size": "12px",
                            },
                        ),
                        dcc.Dropdown(
                            ["none"],
                            "none",
                            id="columns-dropdown",
                            style={"width": "150px", "backgroundColor": "#506783"},
                        ),
                        dcc.Dropdown(
                            ["none"],
                            "none",
                            id="category-dropdown",
                            style={"width": "150px", "backgroundColor": "#506783"},
                        ),
                        dcc.Store(id="dataset"),
                    ],
                    style={
                        "width": "20%",
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
                                "width": "60%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px",
                                "font-size": "12px",
                            },
                        ),
                        dcc.Dropdown(
                            ["none"],
                            "none",
                            id="columns-dropdown-2",
                            style={"width": "150px", "backgroundColor": "#506783"},
                        ),
                        dcc.Dropdown(
                            ["none"],
                            "none",
                            id="category-dropdown-2",
                            style={"width": "150px", "backgroundColor": "#506783"},
                        ),
                        dcc.Store(id="dataset-2"),
                    ],
                    style={"width": "20%", "display": "inline-block"},
                ),
            ],
        ),
        html.Div(
            [
                html.Div(
                    [],
                    id="line-div",
                    style={
                        "width": "40%",
                        "display": "inline-block",
                    },
                ),
                html.Div(
                    [],
                    id="map-div",
                    style={
                        "height": "10%",
                        "width": "40%",
                        "display": "inline-block",
                    },
                ),
            ],
        ),
        html.Div(
            [
                "Compare indicators",
                dcc.Dropdown(
                    ["none"],
                    "none",
                    id="country-dropdown",
                    style={"width": "150px", "backgroundColor": "#506783"},
                ),
                html.Div(
                    [],
                    id="country-comparison-div",
                    style={"width": "43%", "display": "inline-block"},
                ),
            ],
            style={"backgroundColor": "white"},
        ),
    ],
    style={
        "fontFamily": "helvetica",
        "backgroundColor": "white",
        "color": "black",
    },
)
# pltoly black = #111111


@app.callback(
    Output("columns-dropdown", "options"),
    Output("dataset", "data"),
    Output("table-upload", "children"),
    Output("columns-dropdown", "value"),
    Input("table-upload", "contents"),
    Input("table-upload", "filename"),
    State("table-upload", "children"),
)
def preprocess_dataset(file, filename, children):
    if file is not None:
        df, filtered_cols = parse_dataset(file)

        children["props"]["children"] = html.Div([filename])

        print(filtered_cols)

        if not filtered_cols:

            filtered_cols = ["none"]

        return filtered_cols, df, children, filtered_cols[0]

    else:
        raise exceptions.PreventUpdate


@app.callback(
    Output("columns-dropdown-2", "options"),
    Output("dataset-2", "data"),
    Output("table-upload-2", "children"),
    Output("columns-dropdown-2", "value"),
    Output("country-dropdown", "options"),
    Output("country-dropdown", "value"),
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

        return (
            filtered_cols,
            df_2,
            children,
            filtered_cols[0],
            countries,
            countries[0],
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
)
def update_line_plot(
    selected_unit,
    category_column,
    dataframe,
    selected_unit_2,
    category_column_2,
    dataframe_2,
    children,
):
    if dataframe and selected_unit and category_column != "none":
        df = pd.read_json(dataframe)
        filtered_df = df[df[category_column] == selected_unit]

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
)
def update_choropleth(selected_unit, category_column, dataframe, children):

    if dataframe and selected_unit and category_column != "none":
        df = pd.read_json(dataframe)

        filtered_df = DigitalTwinTimeSeries(df=df)
        filtered_df = filtered_df.melt_data(category_column=category_column)

        filtered_df = filtered_df[selected_unit]

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
