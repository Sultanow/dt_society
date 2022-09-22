from dash import (
    dcc,
    html,
    Input,
    Output,
    exceptions,
    callback_context,
    callback,
    MATCH,
    ALL,
)
from typing import List


class ParameterStoreAIO(html.Div):
    class ids:
        store = lambda parameter: {
            "component": "ParameterStoreAIO",
            "subcomponent": "store",
            "store_no": 1,
            "aio_id": parameter,
        }

        input = lambda parameter: {
            "component": "ParameterStoreAIO",
            "subcomponent": "input",
            "input_no": 1,
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

    def __init__(
        self,
        parameter: str,
        value: float | str = None,
        min: float = None,
        max: float = None,
        step: float = None,
        type: str = None,
        display: str = "none",
    ):
        """AIO component to store a parameter required for a multivariate forecasting model

        Args:
            parameter (str): name of the parameter
            value (float | str, optional): Initial value. Defaults to None.
            min (float, optional): Minimum value. Defaults to None.
            max (float, optional): Maximum value. Defaults to None.
            step (float, optional): Size of increment when using increase/decrease buttons. Defaults to None.
            type (str, optional): specify type of input (text, numeric,..). Defaults to None.
            display (str, optional): Initial visibility. Defaults to "none".
        """

        super().__init__(
            children=[
                html.Div(f"Set {parameter}"),
                dcc.Store(id=self.ids.store(parameter)),
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
                "display": display,
                "padding-left": "10px",
                "margin-top": "10px",
            },
        )

    @callback(
        Output(
            {
                "component": "ParameterStoreAIO",
                "subcomponent": "store",
                "store_no": ALL,
                "aio_id": MATCH,
            },
            "data",
        ),
        Input(ids.input(MATCH), "value"),
        Input(
            {
                "component": "ParameterStoreAIO",
                "subcomponent": "input",
                "input_no": ALL,
                "aio_id": MATCH,
            },
            "value",
        ),
        Input(ids.submit_button(MATCH), "n_clicks"),
    )
    def update_parameter_store(
        parameter_input: str | List[str], inputs: List[str], n_clicks: int
    ):
        """Save input in storage component

        Args:
            inputs (List[str]): List of inputs from each input component
            n_clicks (int): number of clicks of submit button

        Raises:
            exceptions.PreventUpdate: No update unless submit button is clicked and inputs are modified

        Returns:
            List[float]: formatted input
        """

        changed_item = [p["prop_id"] for p in callback_context.triggered][0]

        if parameter_input and "submit_button" in changed_item:
            if "scenario" in changed_item:

                scenarios = [
                    [float(x) for x in scenario.replace(" ", "").split(",")]
                    for scenario in inputs
                ]

                return scenarios

            else:
                return inputs

        else:
            raise exceptions.PreventUpdate
