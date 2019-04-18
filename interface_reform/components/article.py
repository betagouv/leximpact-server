# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html


class Article(object):
    def render(
        sizev: int,
        sizeperc: int,
        seuil0: int,
        taux0: int,
        seuil1: int,
        taux1: int,
        seuil2: int,
        taux2: int,
        seuil3: int,
        taux3: int,
    ) -> html:
        return html.Div(
            [
                Article._header(),
                Article._section(),
                Article._subsection(*(0, seuil0)),
                html.Ol(
                    [
                        Article._list_item(*(0, taux0, seuil1)),
                        Article._list_item(*(1, taux1, seuil2)),
                        Article._list_item(*(2, taux2, seuil3)),
                        Article._list_item_last(*(3, taux3)),
                    ],
                    className="ui list",
                ),
                html.Div(
                    [
                        html.Button("Ajouter", className="ui button", style={
                            "color": "#00A3FF"}),
                        html.Div(className="or"),
                        html.Button("Enlever une tranche", className="ui button",style={
                            "color": "#FFFFFF"}),
                    ],
                    className="ui large buttons",
                ),
            ],
            className="ui segment",
            style={
                "padding": "2em",
                "family": "serif",
                "font-size": "20px",
                "font-family": "serif",
            },
        )

    def _header() -> html:
        return html.H1(
            [
                "Article 197",
                html.Div(
                    "Code général des impôts",
                    className="sub header",
                    style={"font-family": "sans serif"},
                ),
            ],
            className="ui header",
            style={"font-size": "40px", "font-family": "serif"},
        )

    def _section() -> html:
        return html.P(
            "I. – En ce qui concerne les contribuables visés à l'article 4 B, il est fait application des règles suivantes pour le calcul de l'impôt sur le revenu :"
        )

    def _subsection(index: int, seuil: int) -> html:
        return html.P(
            [
                "1. L'impôt est calculé en appliquant à la fraction de chaque part de revenu qui excède ",
                html.Span(f"{seuil} ", style={"color": "#A6A00C", "font-size": "100%"}),
                html.Div(
                    dcc.Input(
                        id=f"input-seuil{index}",
                        type="number",
                        value=seuil,
                        style={
                            "color": "#00A3FF",
                            "padding": "0 0 0 .25em",
                            "height": "1.5em",
                            "width": "5em",
                            "font-size": "130%",
                            "font-family": "serif",
                        },
                    ),
                    className="ui mini input",
                ),
                " € ",
                "le taux de : ",
            ]
        )

    def _list_item(index: int, taux: int, seuil: int) -> html:
        return html.Li(
            [
                html.Span(f"{taux} ", style={"color": "#A6A00C", "font-size": "100%"}),
                """ """,
                html.Div(
                    dcc.Input(
                        id=f"input-taux{index}",
                        type="number",
                        value=taux,
                        style={
                            "color": "#00A3FF",
                            "padding": "0 0 0 .25em",
                            "height": "1.5em",
                            "width": "3em",
                            "font-size": "130%",
                            "font-family": "serif",
                        },
                    ),
                    className="ui mini input",
                ),
                """ % """,
                """pour la fraction supérieure à """,
                html.Nobr(id=f"output-seuil{index}"),
                """ € et inférieure ou égale à """,
                html.Span(f"{seuil} ", style={"color": "#A6A00C", "font-size": "100%"}),
                html.Div(
                    dcc.Input(
                        id=f"input-seuil{index + 1}",
                        type="number",
                        value=seuil,
                        style={
                            "color": "#00A3FF",
                            "padding": "0 0 0 .25em",
                            "height": "1.5em",
                            "width": "5em",
                            "font-size": "130%",
                            "font-family": "serif",
                        },
                    ),
                    className="ui mini input",
                ),
                """ € ; """,
            ],
            value="—",
        )

    def _list_item_last(index: int, taux: int) -> html:
        return html.Li(
            [
                html.Span(f"{taux} ", style={"color": "#A6A00C", "font-size": "100%"}),
                """ """,
                html.Div(
                    dcc.Input(
                        id=f"input-taux{index}",
                        type="number",
                        value=taux,
                        style={
                            "color": "#00A3FF",
                            "padding": "0 0 0 .25em",
                            "height": "1.5em",
                            "width": "3em",
                            "font-size": "130%",
                            "font-family": "serif",
                        },
                    ),
                    className="ui mini input",
                ),
                """ % """,
                """pour la fraction supérieure à """,
                html.Nobr(id=f"output-seuil{index}"),
                """ € """,
            ],
            value="—",
        )
