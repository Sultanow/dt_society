from dash import (
    Dash,
    dcc,
    html,
)


class StatAIO(html.Div):
    class ids:
        stat = lambda aio_id: {
            "component": "StatAIO",
            "subcomponent": "stat",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(self, aio_id: str):
        """AIO component to display a specific statistic

        Args:
            aio_id (str): name/id of component
        """
        super().__init__(
            children=[
                html.Div(
                    [
                        html.Div(
                            f"{aio_id}",
                            style={
                                "backgroundColor": "#111111",
                                "font-weight": "bolder",
                                "textAlign": "center",
                                "margin-left": "auto",
                                "margin-right": "auto",
                                "padding": "15px",
                                "font-size": "12px",
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
                                        "font-size": "28px",
                                    },
                                    id=self.ids.stat(aio_id),
                                ),
                            ],
                        ),
                    ],
                    style={
                        "backgroundColor": "#111111",
                        "height": "90px",
                        "width": "90%",
                        # "font-size": "20px",
                    },
                ),
            ],
            style={"display": "inline-block", "width": "25%"},
        )
