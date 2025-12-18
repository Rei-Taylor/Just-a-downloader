from dash import html
import typing as t 


def download_button(label : str, type_ : t.Literal["video", "audio"]):
    btn = html.Div(
                className="download-btn-group",
                children=[
                    html.Button(
                        className=f"btn btn-{type_} w-full",
                        children=[
                            label
                        ]
                    ),
                    
                ]
                    )
    return btn