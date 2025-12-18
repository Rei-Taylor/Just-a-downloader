from dash import html 
from .download_button import download_button


def download_section():
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
                            html.Option(
                                children="hello"
                            ),
                            html.Option(
                                children="hi"
                            ),
                        ]

                    )
                ]
            ),
            html.Div(
                className="download-options",
                children=[
                    download_button("Download Video", "video"),
                    download_button("Download Video", "audio"),
                ]
            )
        ]
    )

    return download
