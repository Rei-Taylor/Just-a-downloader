from dash import html, dcc

def Options(children : str, index : int):
    
    option = html.Option(
        id={"type" : "resolutions", "index" : index},
        children=[children],
        value=children
    )
    return option