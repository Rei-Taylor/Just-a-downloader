from dash import html

def header():
    header = html.Div(
            children=[
                html.Header(
                    className="header",
                    children=[
                        html.H1(
                            className="logo-text",
                            children="Tube Saver"
                        ),
                        html.P(
                            className="tagline",
                            children=["YouTube videos & General File downloader"]
                        )
                    ]
                )
            ]
        )
    
    return header