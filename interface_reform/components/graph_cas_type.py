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
    def render(
        index: int,
        addressimage: str,
        halfwidth=True,
        name=None,
        revenu=10000,
        diff=-300,
    ) -> html:
        relevanttext = ["{:.0f}€/mois".format(revenu / 12.0)]
        tags = [html.A(rt, className="ui tag label") for rt in relevanttext]
        return html.Div(
            [
                html.Div(
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
                                    "{}{}€".format("+" if diff >= 0 else "", diff),
                                    className="detail",
                                ),
                            ],
                            className="ui {} ribbon label".format(
                                "green" if diff < 0 else "red"
                            ),
                        ),
                        html.Div(
                            [
                                html.Div(
                                    " | ".join(cas_types_textes[index]),
                                    className=" header",
                                )
                            ]
                            + tags,
                            className="content",
                        ),
                    ],
                    className="{} card".format("green" if diff < 0 else "red"),
                )
            ],
            className="ui link cards",
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
