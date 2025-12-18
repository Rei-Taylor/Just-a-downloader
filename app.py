from dash import Dash, html, dcc, callback, ctx , Output, Input, no_update, State, MATCH, ALL
import typing as t
from components.header import header

from components.tabs import Tabs
from components.YouTube import YouTube
from components.video_card import video_card

from components.General import General
from pathlib import Path
from src.YouTubeDownloader import Downloader
from src.DL import IDMDownloader

import time,os
from waitress import serve
app = Dash(__name__,use_async=True,suppress_callback_exceptions=True,external_stylesheets=["static/style.css"])

app.title = "TubeSaver"

app.layout = html.Div(
    className="container",
    children=[
        html.Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"),
        html.Link(rel="preconnect", href="https://fonts.googleapis.com"),
        html.Link(rel="preconnect", href="https://fonts.gstatic.com"),
        header(),
        html.Main(
            children=[
                Tabs(),
                html.Div(
                    id="Tab-children",
                    children=[
                        YouTube()
                        , dcc.Store(id="resolution-data")
                    ]
                )
            ]
        ),
        html.Footer(
            className="footer",
            children=[
                html.P("TubeSaver · Download YouTube videos and any file with lightning speed"),
                html.P("Made with ❤️ by Rei Taylor")
            ])
        
    ]
)

async def cool():
    import asyncio 
    await asyncio.sleep(3)
    print("Done")

@callback(
    Output("result", "children"),
    Input("show-info", "n_clicks"),
    State("url", "value"),
    running=[Output("show-info-children", "children"), "Fetching Data", "Done"],
    prevent_initial_call = True
)
def fetch_info(n_clicks, url):
    ytd = Downloader(url)
    get_info = ytd.meta_data()
    if get_info["title"] is not None:

        return [video_card(title=get_info["title"], thumbnail=get_info["thumbnail"], like=get_info["likes"], view=get_info["views"], resolutions = get_info["available_resolutions"])]
    else:
        return "Your URL is not working. How stupid can you be"
    

@callback(
     [Output("Status", "data"), Output("download-video", "data")],
     Input({"type" : "dl-btn" , "index" : ALL}, "n_clicks"),
     [State("url", "value"),
      State("resolution-data", "data")],
)
def download_now(n_clicks, url, resolution):
    
    id_ = ctx.triggered_id
    
    if id_["index"] == 1:
        ytd = Downloader(url, output_path="assets")
        
        file, name = ytd.download_video(resolution)
        with open(file, "rb") as f:
            data = f.read()
            
        print(file)
        print(resolution)
        os.remove(file)
        return ["done", dcc.send_bytes(data, filename=name)]
    
@callback(
    Output("resolution-data", "data", allow_duplicate=True),
    Input({"type" : "resolutions" , "index" : ALL}, "n_clicks"),
    State({"type" : "resolutions" , "index" : ALL}, "value"),
    prevent_initial_call = True
)    
def get_resolution(n_clicks, value):
    id_ = ctx.triggered_id
    print(value)
    print(id_["index"])
    return [value[id_["index"]]]


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
    elif text == "Fetching Data":
        return no_update
    else:
        pass

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000,  threads=8)