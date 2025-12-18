from dash import html 
from .Icon import Icon
def Tabs():
    tabs_ = html.Div(
        className="tabs-container",
        children=[
            html.Div(
                className="tabs",
                children=[
                    html.Button(
                        className="tab-btn active-tab",
                        id="Youtube-tab",
                        children=[
                            Icon("mingcute:youtube-line"),
                            "YouTube Downloader"
                        ]
                        
                    ),
                    html.Button(
                        className="tab-btn",
                        id="General-tab",
                        children=[
                            "General File Downloader"
                        ]
                        
                    )
                ]
            )
        ]
    )

    return tabs_