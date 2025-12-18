from dash import html, dcc 
from .download_section import download_section
from .Icon import Icon


def video_card(title : str, thumbnail : str ,view : int , like : int, resolutions : list):
    video = html.Div(
        className="card fade-in",
        children=[
            html.Div(
                className="card-header",
                children=[
                    html.H2(
                        className="card-title",
                        children=[
                            Icon("line-md:play"),"Video Details"
                        ]
                    )
                ]
            ),
            html.Div(
                className="card-body",
                children=[
                    html.Div(
                        className="video-preview",
                        children=[
                            html.Div(
                                className="thumbnail-container",
                                children=[
                                    html.Img(
                                        alt="Hello",
                                        src=f"{thumbnail}",

                                        className="thumbnail-img",
                                    )
                                ]
                            ),
                            html.Div(
                                className="video-info",
                                children=[
                                    html.H3(
                                        className="video-title",
                                        children=f"{title}"
                                    ),
                                    html.Div(
                                        className="stats",
                                        children=[
                                            html.Div(
                                                className="stat-item",
                                                children=[
                                                    Icon("icon-park-outline:trend"),
                                                    html.Span(
                                                        children=f"{view} views"
                                                    )
                                                ]
                                            ),
                                            html.Div(
                                                className="stat-item",
                                                children=[
                                                    Icon("iconamoon:like-duotone"),
                                                    html.Span(
                                                        children=f"{like}likes"
                                                    )
                                                ]
                                            ),
                                            
                                        ]
                                    ),
                                    download_section(resolutions=resolutions)
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
    return video