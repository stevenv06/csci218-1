"""Render the reachable-layout comparison figure from benchmark results."""

import argparse
import json
from math import ceil, floor, log2
from pathlib import Path

import pypdfium2 as pdfium
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing, Line, String
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib.colors import HexColor


SIZES = ("20 × 30", "40 × 60", "80 × 120")
DENSITIES = (
    (0, "#27476D", "FilledCircle", None),
    (15, "#0B725E", "FilledSquare", (4, 2)),
    (30, "#A05022", "FilledDiamond", (1.5, 2)),
)
INK = HexColor("#1E2936")
SECONDARY = HexColor("#465769")
GRID = HexColor("#DDE5ED")


def marker(shape, color):
    point = makeMarker(shape)
    point.size = 5.3
    point.fillColor = color
    point.strokeColor = color
    return point


def chart(figure, x, title, data, low, high):
    plot = LinePlot()
    plot.x, plot.y, plot.width, plot.height = x, 42, 174, 104
    plot.data = [tuple((index, log2(ratio)) for index, ratio in enumerate(series)) for series in data]
    plot.xValueAxis.valueMin = -0.18
    plot.xValueAxis.valueMax = 2.18
    plot.xValueAxis.valueStep = 1
    plot.xValueAxis.strokeColor = GRID
    plot.xValueAxis.labelTextFormat = lambda value: SIZES[round(value)]
    plot.xValueAxis.labels.fillColor = SECONDARY
    plot.xValueAxis.labels.fontName = "Helvetica"
    plot.xValueAxis.labels.fontSize = 8.7
    plot.xValueAxis.tickDown = 3
    plot.yValueAxis.valueMin = low
    plot.yValueAxis.valueMax = high
    plot.yValueAxis.valueStep = 1
    plot.yValueAxis.labelTextFormat = lambda value: f"{2 ** value:g}×"
    plot.yValueAxis.strokeColor = GRID
    plot.yValueAxis.labels.fillColor = SECONDARY
    plot.yValueAxis.labels.fontName = "Helvetica"
    plot.yValueAxis.labels.fontSize = 8.7
    plot.yValueAxis.visibleGrid = True
    plot.yValueAxis.gridStrokeColor = GRID
    for index, (_, code, shape, dash) in enumerate(DENSITIES):
        color = HexColor(code)
        plot.lines[index].strokeColor = color
        plot.lines[index].strokeWidth = 1.5
        plot.lines[index].strokeDashArray = dash
        plot.lines[index].symbol = marker(shape, color)
    figure.add(plot)
    figure.add(String(x + 87, 157, title, textAnchor="middle", fontName="Helvetica-Bold",
                      fontSize=11, fillColor=INK))


def draw(summary):
    reachable = {(row["rows"], row["nominal_density_percent"]): row for row in summary if row["found"]}
    metrics = ("mean_ms", "mean_nodes_expanded")
    ratios = [
        [
            [reachable[rows, density]["dijkstra"][metric] / reachable[rows, density]["astar"][metric]
             for rows in (20, 40, 80)]
            for density, *_ in DENSITIES
        ]
        for metric in metrics
    ]
    values = [item for panel in ratios for series in panel for item in series]
    low = min(0, floor(log2(min(values))))
    high = max(6, ceil(log2(max(values))))
    figure = Drawing(473, 193)
    chart(figure, 39, "Search time ratio", ratios[0], low, high)
    chart(figure, 276, "Nodes expanded ratio", ratios[1], low, high)

    figure.add(String(57, 177, "Obstacle density", fontName="Helvetica-Bold", fontSize=9, fillColor=INK))
    for x, (density, code, shape, dash) in zip((159, 247, 338), DENSITIES):
        color = HexColor(code)
        figure.add(Line(x, 180.5, x + 22, 180.5, strokeColor=color, strokeWidth=1.5, strokeDashArray=dash))
        symbol = marker(shape, color)
        symbol.x, symbol.y = x + 11, 180.5
        figure.add(symbol)
        figure.add(String(x + 28, 177, f"{density}%", fontName="Helvetica", fontSize=9, fillColor=INK))
    figure.add(String(236.5, 10, "Grid size (rows × columns)", textAnchor="middle",
                      fontName="Helvetica", fontSize=9, fillColor=SECONDARY))
    return figure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("benchmark_results.json"))
    parser.add_argument("--output", type=Path, default=Path("reachable_comparison.png"))
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    with pdfium.PdfDocument(renderPDF.drawToString(draw(data["summary"]))) as pdf:
        pdf[0].render(scale=4).to_pil().save(args.output)


if __name__ == "__main__":
    main()
