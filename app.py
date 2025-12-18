from dash import Dash, html, dcc, callback, ctx , Output, Input, no_update
import typing as t
from components.header import header

from components.tabs import Tabs
from components.YouTube import YouTube
from components.video_card import video_card

from components.General import General




app = Dash(__name__,use_async=True,suppress_callback_exceptions=True,external_stylesheets=["static/style.css"])



app.layout = html.Div(
    className="container",
    children=[
        header(),
        html.Main(
            children=[
                Tabs(),
                html.Div(
                    id="Tab-children",
                    children=[
                        YouTube(),
                    ]
                )
            ]
        ),
        
    ]
)

async def cool():
    import asyncio 
    await asyncio.sleep(3)
    print("Done")

@callback(
    Output("result", "children"),
    Input("show-info", "n_clicks"),
    running=[Output("show-info-children", "children"), "Downloadloaing", "Done"],
    prevent_initial_call = True
)
async def download(n_clicks):
    await cool()
    return [video_card()]

@callback(
        [Output("Tab-children", "children", allow_duplicate=True),
         Output("Youtube-tab", "className", allow_duplicate=True), 
         Output("General-tab", "className", allow_duplicate=True)],
        Input("Youtube-tab", "n_clicks"),
        prevent_initial_call = True
)
def change_tab(n_clicks):
    return [YouTube(), "tab-btn active-tab", "tab-btn"]

@callback(
        [Output("Tab-children", "children", allow_duplicate=True),
         Output("Youtube-tab", "className", allow_duplicate=True), 
         Output("General-tab", "className", allow_duplicate=True)],
        Input("General-tab", "n_clicks"),
        prevent_initial_call = True
)
def change_tab(n_clicks):
    return [General(), "tab-btn", "tab-btn active-tab"]

@callback(
    Output("show-info-children", "children", allow_duplicate=True),
    Input("show-info-children", "children"),
    prevent_initial_call = True
)
async def change_back(text):

    if text == "Done":
        await cool()  
        return "Fetch Video Info"
    elif text == "Downloadloaing":
        return no_update
    else:
        pass

app.run(debug=True)