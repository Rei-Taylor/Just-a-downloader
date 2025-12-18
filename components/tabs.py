from dash import html 

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