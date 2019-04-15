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
                html.H1(
                    [
                        "Article 197",
                        html.Div("Code Général des Impôts", className="sub header"),
                    ],
                    className="ui header dividing",
                ),
                html.P(
                    """I. – En ce qui concerne les contribuables visés à l'article 4 B, il est fait application des règles suivantes pour le calcul de l'impôt sur le revenu :"""
                ),
                html.P(
                    [
                        """1. L'impôt est calculé en appliquant à la fraction de chaque part de revenu qui excède """,
                        html.S(f"{seuil0} €"),
                        html.Div(
                            dcc.Input(
                                id="input-seuil0",
                                type="number",
                                value=seuil0,
                                style={"border-radius": 0, "height": "2em"},
                            ),
                            className="ui mini input",
                        ),
                        """ € """,
                        """le taux de : """,
                    ]
                ),
                html.Ol(
                    [
                        html.Li(
                            [
                                html.S(f"{taux0} %"),
                                """ """,
                                html.Div(
                                    dcc.Input(
                                        id="input-taux0",
                                        type="number",
                                        value=taux0,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ % """,
                                """pour la fraction supérieure à """,
                                html.Nobr(id="output-seuil0"),
                                """ € et inférieure ou égale à """,
                                html.S(f"{seuil1} €"),
                                html.Div(
                                    dcc.Input(
                                        id="input-seuil1",
                                        type="number",
                                        value=seuil1,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ € ; """,
                            ],
                            value="—",
                        ),
                        html.Li(
                            [
                                html.S(f"{taux1} %"),
                                """ """,
                                html.Div(
                                    dcc.Input(
                                        id="input-taux1",
                                        type="number",
                                        value=taux1,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ % """,
                                """pour la fraction supérieure à """,
                                html.Nobr(id="output-seuil1"),
                                """ € et inférieure ou égale à """,
                                html.S(f"{seuil2} €"),
                                html.Div(
                                    dcc.Input(
                                        id="input-seuil2",
                                        type="number",
                                        value=seuil2,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ € ; """,
                            ],
                            value="—",
                        ),
                        html.Li(
                            [
                                html.S(f"{taux2} %"),
                                """ """,
                                html.Div(
                                    dcc.Input(
                                        id="input-taux2",
                                        type="number",
                                        value=taux2,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ % """,
                                """pour la fraction supérieure à """,
                                html.Nobr(id="output-seuil2"),
                                """ € et inférieure ou égale à """,
                                html.S(f"{seuil3} €"),
                                html.Div(
                                    dcc.Input(
                                        id="input-seuil3",
                                        type="number",
                                        value=seuil3,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ € ; """,
                            ],
                            value="—",
                        ),
                        html.Li(
                            [
                                html.S(f"{taux3} %"),
                                """ """,
                                html.Div(
                                    dcc.Input(
                                        id="input-taux3",
                                        type="number",
                                        value=taux3,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ % """,
                                """pour la fraction supérieure à """,
                                html.Nobr(id="output-seuil3"),
                                """ € """,
                            ],
                            value="—",
                        ),
                    ],
                    className="ui list",
                ),
            ],
            className="eight wide column",
        )
