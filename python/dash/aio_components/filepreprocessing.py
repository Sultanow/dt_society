import dash_daq as daq
from dash import (
    Dash,
    dcc,
    html,
    Input,
    Output,
    exceptions,
    State,
    callback_context,
    callback,
    MATCH,
)
from helpers.layout import preprocess_dataset, export_settings


class FilePreProcessingAIO(html.Div):
    class ids:
        store = lambda dataset_id: {
            "component": "FilePreProcessingAIO",
            "subcomponent": "store",
            "aio_id": dataset_id,
        }
        geo_dropdown = lambda dataset_id: {
            "component": "FilePreProcessingAIO",
            "subcomponent": "geo_dropdown",
            "aio_id": dataset_id,
        }
        reshape_dropdown = lambda dataset_id: {
            "component": "FilePreProcessingAIO",
            "subcomponent": "reshape_dropdown",
            "aio_id": dataset_id,
        }
        file_upload = lambda dataset_id: {
            "component": "FilePreProcessingAIO",
            "subcomponent": "file_upload",
            "aio_id": dataset_id,
        }
        feature_dropdown = lambda dataset_id: {
            "component": "FilePreProcessingAIO",
            "subcomponent": "feature_dropdown",
            "aio_id": dataset_id,
        }
        time_dropdown = lambda dataset_id: {
            "component": "FilePreProcessingAIO",
            "subcomponent": "time_dropdown",
            "aio_id": dataset_id,
        }
        separator_dropdown = lambda dataset_id: {
            "component": "FilePreProcessingAIO",
            "subcomponent": "separator_dropdown",
            "aio_id": dataset_id,
        }
        reshape_switch = lambda dataset_id: {
            "component": "FilePreProcessingAIO",
            "subcomponent": "reshape_switch",
            "aio_id": dataset_id,
        }
        error_dialog = lambda dataset_id: {
            "component": "FilePreProcessingAIO",
            "subcomponent": "error_dialog",
            "aio_id": dataset_id,
        }
        preset_upload = lambda dataset_id: {
            "component": "FilePreProcessingAIO",
            "subcomponent": "preset_upload",
            "aio_id": dataset_id,
        }
        preset_upload_button = lambda dataset_id: {
            "component": "FilePreProcessingAIO",
            "subcomponent": "preset_upload_button",
            "aio_id": dataset_id,
        }
        preset_download = lambda dataset_id: {
            "component": "FilePreProcessingAIO",
            "subcomponent": "preset_download",
            "aio_id": dataset_id,
        }
        preset_download_button = lambda dataset_id: {
            "component": "FilePreProcessingAIO",
            "subcomponent": "preset_download_button",
            "aio_id": dataset_id,
        }
        demo_id = lambda dataset_id: {
            "component": "FilePreprocessingAIO",
            "subcomponent": "demo_id",
            "aio_id": dataset_id,
        }

    ids = ids

    def __init__(self, dataset_id: str):

        self.demo_id = dataset_id

        super().__init__(
            children=[
                html.Div(
                    f"{dataset_id}",
                    id=self.ids.demo_id(dataset_id),
                    style={"display": "none"},
                ),
                dcc.ConfirmDialog(
                    id=self.ids.error_dialog(dataset_id),
                    message="An error occured while processing your data. Please make sure that the data is in the correct format and select the appropriate separator.",
                ),
                html.Div(
                    [
                        dcc.Upload(
                            id=self.ids.file_upload(dataset_id),
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
                            id=self.ids.separator_dropdown(dataset_id),
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
                            id=self.ids.geo_dropdown(dataset_id),
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
                                    id=self.ids.reshape_switch(dataset_id),
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
                            id=self.ids.reshape_dropdown(dataset_id),
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
                            id=self.ids.time_dropdown(dataset_id),
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
                            id=self.ids.feature_dropdown(dataset_id),
                            style={
                                "border-color": "#5c6cfa",
                                "background-color": "#111111",
                            },
                        ),
                        dcc.Loading(
                            children=[
                                dcc.Store(id=self.ids.store(dataset_id)),
                            ],
                            fullscreen=True,
                            style={"backgroundColor": "rgba(8,8,8,0.8)"},
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
                                    id=self.ids.preset_upload(dataset_id),
                                    children=html.Button(
                                        "Import",
                                        id=self.ids.preset_upload_button(dataset_id),
                                        n_clicks=0,
                                        style={
                                            "border-color": "#5c6cfa",
                                            "width": "120px",
                                            "margin-right": "4px",
                                        },
                                    ),
                                ),
                                dcc.Download(id=self.ids.preset_download(dataset_id)),
                                html.Button(
                                    "Export",
                                    id=self.ids.preset_download_button(dataset_id),
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
            style={"display": "flex"},
        )

    def get_demo_id(self):
        return self.demo_id

    @callback(
        Output(ids.store(MATCH), "data"),
        Output(ids.geo_dropdown(MATCH), "options"),
        Output(ids.reshape_dropdown(MATCH), "options"),
        Output(ids.file_upload(MATCH), "children"),
        Output(ids.feature_dropdown(MATCH), "options"),
        Output(ids.time_dropdown(MATCH), "options"),
        Output(ids.file_upload(MATCH), "contents"),
        Output(ids.separator_dropdown(MATCH), "value"),
        Output(ids.file_upload(MATCH), "filename"),
        Output(ids.reshape_switch(MATCH), "on"),
        Output(ids.geo_dropdown(MATCH), "value"),
        Output(ids.error_dialog(MATCH), "displayed"),
        Output(ids.feature_dropdown(MATCH), "value"),
        Output(ids.time_dropdown(MATCH), "value"),
        Output(ids.preset_upload(MATCH), "contents"),
        Output(ids.reshape_dropdown(MATCH), "value"),
        Output(ids.error_dialog(MATCH), "message"),
        Input(ids.separator_dropdown(MATCH), "value"),
        Input(ids.geo_dropdown(MATCH), "value"),
        Input(ids.file_upload(MATCH), "contents"),
        Input(ids.file_upload(MATCH), "filename"),
        Input(ids.reshape_dropdown(MATCH), "value"),
        Input(ids.reshape_switch(MATCH), "on"),
        State(ids.file_upload(MATCH), "children"),
        Input("demo-button", "n_clicks"),
        Input(ids.preset_upload(MATCH), "contents"),
        Input("reset-button", "n_clicks"),
        Input(ids.demo_id(MATCH), "children"),
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
        demo_id: str,
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
            f"Demo {str(demo_id)}",
            preset_file,
        )

    @callback(
        Output(ids.preset_download(MATCH), "data"),
        Input(ids.separator_dropdown(MATCH), "value"),
        Input(ids.geo_dropdown(MATCH), "value"),
        Input(ids.reshape_dropdown(MATCH), "value"),
        Input(ids.reshape_switch(MATCH), "on"),
        Input(ids.time_dropdown(MATCH), "value"),
        Input(ids.feature_dropdown(MATCH), "value"),
        Input(ids.preset_download_button(MATCH), "n_clicks"),
        Input(ids.file_upload(MATCH), "filename"),
        Input(ids.demo_id(MATCH), "children"),
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
        demo_id: int,
    ):
        changed_item = [p["prop_id"] for p in callback_context.triggered][0]

        if "preset_download_button" in changed_item:

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
