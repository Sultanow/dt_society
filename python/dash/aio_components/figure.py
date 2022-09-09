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
    ALL,
)
from helpers.layout import preprocess_dataset, export_settings
from .filepreprocessing import FilePreProcessingAIO


class FigureAIO(html.Div):
    class ids:
        fig_container = lambda aio_id: {
            "component": "FigureAIO",
            "subcomponent": "fig_container",
            "aio_id": aio_id,
        }

        section_container = lambda aio_id: {
            "component": "FigureAIO",
            "subcomponent": "section_container",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(self, aio_id):
        super().__init__(
            children=[
                html.Div(
                    [
                        html.Div(
                            f"{aio_id}",
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
                    ],
                    style={"backgroundColor": "#111111"},
                ),
                dcc.Loading(
                    type="circle",
                    children=[
                        html.Div(
                            [],
                            id=self.ids.fig_container(aio_id),
                        ),
                    ],
                ),
            ],
            style={"display": "none"},
            id=self.ids.section_container(aio_id),
        )
