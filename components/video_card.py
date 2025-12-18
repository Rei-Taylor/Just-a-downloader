from dash import html, dcc 
from .download_section import download_section



def video_card():
    video = html.Div(
        className="card fade-in",
        children=[
            html.Div(
                className="card-header",
                children=[
                    html.H2(
                        className="card-title",
                        children=[
                            "Video Details"
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
                                        alt="Hello"
                                    )
                                ]
                            ),
                            html.Div(
                                className="video-info",
                                children=[
                                    html.H3(
                                        className="video-title",
                                        children="Video"
                                    ),
                                    html.Div(
                                        className="stats",
                                        children=[
                                            html.Div(
                                                className="stat-item",
                                                children=[
                                                    html.Span(
                                                        children="81 views"
                                                    )
                                                ]
                                            ),
                                            html.Div(
                                                className="stat-item",
                                                children=[
                                                    html.Span(
                                                        children="81 likes"
                                                    )
                                                ]
                                            ),
                                            download_section()
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
    return video