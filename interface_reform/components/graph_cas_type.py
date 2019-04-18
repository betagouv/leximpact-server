# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html


cas_types_textes = [
    ["Seul·e", "sans enfant"],
    ["En couple", "deux enfants"],
    ["En couple", "deux enfants", "Guadeloupe"],
    ["En couple", "deux enfants", "Retraité·e·s"],
    ["Seul·e", "un enfant"],
    ["En couple", "un enfant"],
]  # Decrit les cas types


class GraphCasType(object):
    def rendermieux(index: int, avant: float, apres: float, revenu=10000):
        relevanttext = ["{:.0f}€/mois".format(revenu / 12.0)]
        tags = [html.A(rt, className="ui tag label") for rt in relevanttext]
        diff = avant - apres
        return [
            html.Div(
                dcc.Graph(
                    id="graph-ct{}".format(index),
                    figure={
                        "data": [
                            {
                                "x": ["avant"],
                                "y": [-avant],
                                "type": "bar",
                                "name": u"avant",
                            },
                            {
                                "x": ["après"],
                                "y": [-apres],
                                "type": "bar",
                                "name": u"après",
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
            html.A(
                [
                    "Impôt payé :",
                    html.Div(
                        [
                            html.Nobr(
                                ("+" if avant >= apres else "") + str(avant - apres)
                            ),
                            "€",
                        ],
                        className="detail",
                    ),
                ],
                className="ui {} huge ribbon label".format(
                    "green" if diff < -1 else "red" if diff > 1 else "grey"
                ),
            ),
            html.Div(
                [html.Div(" | ".join(cas_types_textes[index]), className=" header")]
                + tags,
                className="content",
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
