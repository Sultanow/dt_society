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


class ParameterStoreAIO(html.Div):
    class ids:
        store = lambda parameter: {
            "component": "ParameterStoreAIO",
            "subcomponent": "store",
            "aio_id": parameter,
        }

        input = lambda parameter: {
            "component": "ParameterStoreAIO",
            "subcomponent": "input",
            "aio_id": parameter,
        }

        submit_button = lambda parameter: {
            "component": "ParameterStoreAIO",
            "subcomponent": "submit_button",
            "aio_id": parameter,
        }

        container = lambda parameter: {
            "component": "ParameterStoreAIO",
            "subcomponent": "container",
            "aio_id": parameter,
        }

    ids = ids

    def __init__(self, parameter, value=None, min=None, max=None, step=None, type=None):
        super().__init__(
            children=[
                dcc.Store(id=self.ids.store(parameter)),
                html.Div(f"Set {parameter}"),
                dcc.Input(
                    value=value,
                    min=min,
                    max=max,
                    step=step,
                    id=self.ids.input(parameter),
                    type=type,
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
                            id=self.ids.submit_button(parameter),
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
            id=self.ids.container(parameter),
            style={
                "display": "none",
                "padding-left": "10px",
                "margin-top": "10px",
            },
        )

    @callback(
        Output(ids.store(MATCH), "data"),
        Input(ids.input(MATCH), "value"),
        Input(ids.submit_button(MATCH), "n_clicks"),
    )
    def update_parameter_store(parameter_input: str, n_clicks: int):

        changed_item = [p["prop_id"] for p in callback_context.triggered][0]

        if parameter_input and "submit_button" in changed_item:
            if "scenario" in changed_item:
                scenario = parameter_input.replace(" ", "").split(",")

                scenario = [float(x) for x in scenario]

                return scenario

            else:
                return parameter_input

        else:
            raise exceptions.PreventUpdate
