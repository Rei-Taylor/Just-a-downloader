from dash import html, dcc

def YouTube():
    card_ = html.Div(
        className="card",
        children=[
            html.Div(
                className="card-header",
                children=[
                    html.H2(
                        className="card-title",
                        children=[
                            "Enter YouTube URL"
                        ]
                    )
                ]
            ),
            html.Div(
                className="card-body",
                children=[
                    html.Div(
                        className="input-group",
                        children=[
                            html.Label(
                                className="input-lable",
                                children=["Vidoe URL"],
                                htmlFor="url"
                            ),
                            dcc.Input(
                                type="url",
                                id="url",
                                className="url-input",
                                placeholder="https://www.youtube.com/watch?v=...",
                                style={"margin-bottom" : "5px"}
                            ),
                            html.Button(
                                className="btn btn-primary w-full",
                                id="show-info",
                                children=[
                                    html.Span(
                                        children="Fetch Video Info",
                                        id="show-info-children"
                                    )
                                ]
                            ),
                            html.Div(
                                id="result",
                                children=[
                                    
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )


    return card_