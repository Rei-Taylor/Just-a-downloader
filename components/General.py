from dash import html , dcc

def General():
    card = html.Div(
        className="card",
        children=[
            html.Div(
                className="card-header",
                children=[
                    html.H2(
                        className="card-title",
                        children=["File Downloader"]
                    )
                ]
            ),
            html.Div(
                className="card-body",
                children=[
                    html.Div(
                        className="input-group",
                        children=[
                            html.Label(
                                className="input-label",
                                htmlFor="fileUrl",
                                children=[
                                    "File URL"
                                ],
                            ),
                            dcc.Input(
                                className="url-input",
                                type="url",
                                placeholder="https://example.com/file.zip"
                            )
                        ]
                    ),
                    html.Div(
                        className="input-group",
                        children=[
                            html.Label(
                                className="input-label",
                                children="Download Settings",
                            ),
                            html.Div(
                                className="settings-grid",
                                children=[
                                    html.Div(
                                        className="settings-item",
                                        children=[
                                            html.Label(
                                                className="setting-label",
                                                htmlFor="maxWorkers",
                                                children="Threads",
                                            ),
                                            dcc.Input(
                                                type="number",
                                                id="maxWorkers",
                                                min="1",
                                                max="16",
                                                className="setting-input"
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        className="settings-item",
                                        children=[
                                            html.Label(
                                                className="setting-label",
                                                htmlFor="chunkSize",
                                                children="ChunkSize",
                                            ),
                                            dcc.Input(
                                                type="number",
                                                id="chunkSize",
                                                min="1",
                                                max="16",
                                                className="setting-input"
                                            )
                                        ]
                                    ),
                                    
                                ]
                            )
                        ]
                    ),
                    html.Button(
                        className="btn btn-primary w-full mb-4",
                        children="Analyzing File"
                    )
                ]
            )
        ]
    )
    return card