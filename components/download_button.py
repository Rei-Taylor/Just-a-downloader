from dash import html, dcc
import typing as t 
from .Icon import Icon

def download_button(label : str, type_ : t.Literal["video", "audio"] , ID : int, Icon_ : str):
    btn = html.Div(
                className="download-btn-group",
                children=[
                    html.Button(
                        className=f"btn btn-{type_} w-full",
                        children=[
                            Icon(Icon_),
                            label
                        ],
                        id={"index" : ID, "type":"dl-btn"}
                    ),
                    dcc.Store(id="Status")
                ]
                    )
    return btn