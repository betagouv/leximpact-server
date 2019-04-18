# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

cas_types_textes = [
    ["Seul·e", "sans enfant"],
    ["En couple", "deux enfants"],
    ["En couple", "deux enfants", "Guadeloupe"],
    ["En couple", "deux enfants", "Retraité·e·s"],
    ["Seul·e", "un enfant"],
    ["En couple", "un enfant"],
]  # Decrit les cas types

from math import log10


class GraphCasType(object):
    def rendermieux(
        index: int, avant: float, apres: float, revenu=10000, maximpot=35000
    ):
        relevanttext = ["{:.0f}€/mois".format(revenu / 12.0)]
        tags = [html.A(rt, className="ui tag label") for rt in relevanttext]
        diff = avant - apres
        map = max(-avant, -apres)
        scale = (map) * max(0, (maximpot / map))  # Mise a l'échelle
        return [
            html.Div(
                [
                    html.Div(
                        " | ".join(cas_types_textes[index]),
                        className=" header",
                        style={
                            "font-size": "185%",
                            "margin-bottom": "0.4em",
                            "padding-right": "20px",
                        },
                    )
                ]
                + tags,
                className="content",
            ),
            html.A(
                [
                    "Effet sur l'impôt payé :",
                    html.Div(
                        [
                            html.Nobr(
                                ("+" if avant >= apres else "") + str(avant - apres)
                            ),
                            "€",
                        ],
                        className="header",
                        style={
                            "font-size": "300%",
                            "margin-top": "0.5em",
                        },
                    ),
                ],
                # className="ui {} large ribbon label".format(
                # "green" if diff < -1 else "red" if diff > 1 else "grey",
                className="ui {} huge extra".format(
                    "green" if diff < -1 else "red" if diff > 1 else "grey",
                   
                ),

            ),

            html.A(
                [html.Div("", className="heart icon", style={"font-size": "0%"})],
                className="ui {} large right corner label".format(
                    "green" if diff < -1 else "red" if diff > 1 else "grey"
                ),
            ),
            html.Div(
                dcc.Graph(
                    id="graph-ct{}".format(index),
                    figure={
                        "layout": go.Layout(
                            margin=go.layout.Margin(l=50, r=50, b=50, t=20, pad=4),
                            autosize=True,
                            height=250,
                            #width=200,
                            yaxis={
                                "range": [
                                    0,
                                    map if scale <= map else scale,
                                ],  # Si l'échelle par défaut est trop petite,
                                # on met en rouge mais on montre la vraie taille
                                "tickfont": {
                                    "color": "red" if scale <= map else "black"
                                },
                            },
                        ),
                        "data": [
                            {
                                "x": ["droit existant"],
                                "y": [-avant],
                                "type": "bar",
                                # "name": u"avant",
                                "marker": {"color": "E5DC07"},  # " "rgb(40,40,40)"},
                                "showlegend": False,
                            },
                            {
                                "x": ["droit proposé"],
                                "y": [-apres],
                                "type": "bar",
                                # "name": u"après",
                                "marker": {"color": "00A3FF"},
                                "showlegend": False,
                            },
                            #     {'x': ["impact"], 'y': [-df["apres"][indextotake[index]] + df["avant"][indextotake[index]]], 'type': 'bar',
                            #     'name': 'impact'}
                        ]
                        # ,
                        # 'layout': {
                        #    'title': simulate_pop_from_reform.foyertotexte(index)
                        # }
                    },
                ),
                className="image",
            ),
        ]

    def render(
        index: int, addressimage: str, halfwidth=True, name=None, diff=0, revenu=10000
    ) -> html:
        relevanttext = ["{:.0f}€/mois".format(revenu / 12.0)]
        tags = [html.A(rt, className="ui tag label") for rt in relevanttext]
        return html.Div(
            [
                html.Div(
                    dcc.Graph(id="graph-ct{}".format(index)),
                    className="image",
                    style={},
                ),
                html.A(
                    [
                        "Impôt payé :",
                        html.Div(
                            [html.Nobr(id="impact-ct{}".format(index)), "€"],
                            className="detail",
                        ),
                    ],
                    className="ui {} ribbon label".format(
                        "green" if diff < 0 else "red"
                    ),
                ),
                html.Div(
                    [html.Div(" | ".join(cas_types_textes[index]), className=" header")]
                    + tags,
                    className="content",
                ),
            ],
            className="ui {} card".format("green" if diff < 0 else "red"),
        )
        # return html.Table(
        #     [
        #         html.Tr(
        #             [
        #                 html.Td(html.Img(src=addressimage)),
        #                 html.Td(
        #                     dcc.Graph(
        #                         id="graph-ct{}".format(index),
        #                         className="four wide columns"
        #                         if halfwidth
        #                         else "outputstat",
        #                     ),
        #                     rowSpan=2,
        #                 ),
        #             ]
        #         ),
        #         html.Tr([html.Td("Famille {} : revenu de {}".format(name, revenu))]),
        #     ]
        # )
