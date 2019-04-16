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
            ],
            className="eight wide column",
        )

    def _header() -> html:
        return html.H1(
            [
                "Article 197",
                html.Div("Code Général des Impôts", className="sub header"),
            ],
            className="ui header dividing",
        )

    def _section() -> html:
        return html.P(
            "I. – En ce qui concerne les contribuables visés à l'article 4 B, il est fait application des règles suivantes pour le calcul de l'impôt sur le revenu :"
        )

    def _subsection(index: int, seuil: int) -> html:
        return html.P(
            [
                "1. L'impôt est calculé en appliquant à la fraction de chaque part de revenu qui excède ",
                html.S(f"{seuil} €"),
                html.Div(
                    dcc.Input(
                        id=f"input-seuil{index}",
                        type="number",
                        value=seuil,
                        style={"border-radius": 0, "height": "2em"},
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
                html.S(f"{taux} %"),
                """ """,
                html.Div(
                    dcc.Input(
                        id=f"input-taux{index}",
                        type="number",
                        value=taux,
                        style={"border-radius": 0, "height": "2em"},
                    ),
                    className="ui mini input",
                ),
                """ % """,
                """pour la fraction supérieure à """,
                html.Nobr(id=f"output-seuil{index}"),
                """ € et inférieure ou égale à """,
                html.S(f"{seuil} €"),
                html.Div(
                    dcc.Input(
                        id=f"input-seuil{index + 1}",
                        type="number",
                        value=seuil,
                        style={"border-radius": 0, "height": "2em"},
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
                html.S(f"{taux} %"),
                """ """,
                html.Div(
                    dcc.Input(
                        id=f"input-taux{index}",
                        type="number",
                        value=taux,
                        style={"border-radius": 0, "height": "2em"},
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
