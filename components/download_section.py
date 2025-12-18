from dash import html , dcc
from .download_button import download_button
from .options import Options

from .Icon import Icon

def download_section(resolutions : list):
    download = html.Div(
        className="download-section",
        children=[
            html.Div(
                className="input-group",
                children=[
                    html.Label(
                        className="input-lable",
                        htmlFor="resolution",
                        children=[
                            "Select Quality"
                        ]
                    ),
                    html.Select( 
                        className="resolution-select",
                        children=[
                            Options(value, index )
                             for index,value in enumerate(resolutions)
                        ]

                    )
                ]
            ),
            html.Div(
                className="download-options",
                children=[
                    download_button("Download Video", "video", 1, "line-md:download-loop"),
                    download_button("Download Audio", "audio", 2, "formkit:fileaudio"),
                    dcc.Download(id="download-video")
                ]
            ),
            html.Div(
                id="Final-Result"
            )
        ]
    )

    return download
