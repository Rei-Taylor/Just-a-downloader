from src.DL import IDMDownloader

app = IDMDownloader(
    url="https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
)

info = app.get_file_info()

app.download()
print(str(info))