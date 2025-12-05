from pathlib import Path
from flask import Flask

NAME = "constellation_viz"

COLOR = [
    "CRIMSON",
    "DODGERBLUE",
    "PERU",
    "BLUEVIOLET",
    "DARKMAGENTA",
]  # color for orbit supported by CesiumJS

HTML_DIR = Path(__file__).parent.parent.parent / "static" / "html"


def gen_html(pos: tuple[float, float, float], pt: list) -> str:
    viz_html = ""
    lat, lon, height = pos
    viz_html += (
        "viewer.entities.add({name: "
        + f"'sat-{500}'"
        + ", position: Cesium.Cartesian3.fromDegrees("
        + str(lon)
        + ", "
        + str(lat)
        + ", "
        + str(height * 1000)
        + "), "
        + "ellipsoid : {radii : new Cesium.Cartesian3(30000.0, 30000.0, 30000.0), material : "
        "Cesium.Color.BLACK.withAlpha(1),}});\n"
    )

    for id, p in enumerate(pt):
        viz_html += (
            "viewer.entities.add({name: "
            + f"'pt-{id}'"
            + ", position: Cesium.Cartesian3.fromDegrees("
            + str(p[1])
            + ", "
            + str(p[0])
            + ", "
            + str(0)
            + "), "
            + "ellipsoid : {radii : new Cesium.Cartesian3(30000.0, 30000.0, 30000.0), material : "
            "Cesium.Color.BLACK.withAlpha(1),}});\n"
        )
    return viz_html


def viz(pos: tuple[float, float, float], pt: list):
    html_dir = HTML_DIR
    top_html = open(html_dir / "top.html", "r")
    bottom_html = open(html_dir / "bottom.html", "r")
    output_html = open(html_dir / f"{NAME}.html", "w")
    output_html.write(top_html.read())

    output_html.write(gen_html(pos, pt))

    output_html.write(bottom_html.read())

    top_html.close()
    bottom_html.close()
    output_html.close()

    app = Flask(__name__, static_folder=html_dir)

    @app.route("/")
    def index():
        # return app.send_static_file(f"test.html")
        return app.send_static_file(f"{NAME}.html")

    app.run(debug=False)
