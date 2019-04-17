# -*- coding: utf-8 -*-

import sys
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from components import Article, GraphCasType, Header

version_beta_sans_graph_pop = True

API_mode = (
    False
)  # If true, the app will attempt to retrieve data through an API call rather than through Openfisca.

if not API_mode:
    try:
        sys.path.insert(0, "./Simulation_engine")
        import simulate_pop_from_reform
    except (Exception):
        sys.path.insert(0, "./../Simulation_engine")
        import simulate_pop_from_reform
else:
    import requests

    endpoint = "http://127.0.0.1:5000/"

    def api_revenus_ct():
        r = requests.post("http://127.0.0.1:5000/calculate/revenus", json={})
        return {int(k): int(v) for k, v in r.json().items()}

    def api_resultat_simulation(seuils, taux, compute_deciles):
        d = {"bareme_ir": {"taux": taux, "seuils": seuils}, "deciles": compute_deciles}
        r = requests.post("http://127.0.0.1:5000/calculate/compare", json=d)
        return r.json()[0]


external_scripts = [
    "https://cdn.jsdelivr.net/npm/jquery@3.3.1/dist/jquery.min.js",
    "https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.js",
]

external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.css"
]

app = dash.Dash(
    __name__,
    external_scripts=external_scripts,
    external_stylesheets=external_stylesheets,
)

basevalue = 9964

# app.config['suppress_callback_exceptions']=True

article_values = {
    "sizev": 1,
    "sizeperc": 1,
    "seuil0": 9964,
    "taux0": 14,
    "seuil1": 27519,
    "taux1": 30,
    "seuil2": 73779,
    "taux2": 41,
    "seuil3": 156244,
    "taux3": 45,
}

url_css_to_add = [
    "https://fonts.googleapis.com/css?family=Lora:400,400i,700,700i|PT+Serif",
    "https://fonts.googleapis.com/css?family=Lato",
]

links_css_stylesheets = [
    html.Link(href=url, rel="stylesheet") for url in url_css_to_add
]

names = ["Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard"]

if not API_mode:
    revenusCT = simulate_pop_from_reform.revenus_cas_types()
else:
    revenusCT = api_revenus_ct()

try:
    imgstarts = [
        "/assets/ImagesCasTypes/" + namefile
        for namefile in sorted(os.listdir("./assets/ImagesCasTypes"))
    ]
except (Exception):
    print(
        "images not found in ./assets/ImagesCasTypes, trying in ./interface_reform/assets/ImagesCasTypes"
    )
    imgstarts = [
        "/assets/ImagesCasTypes/" + namefile
        for namefile in sorted(os.listdir("./interface_reform/assets/ImagesCasTypes"))
    ]

halfwidthgraphs = True
if False:
    graphsCT = [
        GraphCasType.render(
            index,
            imgstarts[index],
            halfwidth=halfwidthgraphs,
            name=names[index],
            revenu=revenusCT[index],
        )
        for index, _name in enumerate(names)
    ]
else:
    graphsCT = [
        html.Div(id="graphtot-ct{}".format(index), className="ui card")
        for index, _name in enumerate(names)
    ]

nbsplit = 1
graphsCTsplit = [graphsCT[x : x + nbsplit] for x in range(0, len(graphsCT), nbsplit)]


# texte_cas_types=simulate_pop_from_reform.texte_cas_types()

# desc_cas_types=[html.P([k," : ",v]) for k,v in texte_cas_types.items()]

app.layout = html.Div(
    [
        Header.render(),
        html.P(
            [html.Button(id="submit-button", n_clicks=0, children="calculer impact")]
        )
        if not version_beta_sans_graph_pop
        else html.B(""),
        html.Div(
            [
                html.Div(Article.render(**article_values), className="six wide column"),
                html.Div(
                    html.Div(
                        graphsCT
                        + (
                            [
                                html.P(
                                    [
                                        dcc.Graph(id="graphtotal"),
                                        dcc.Graph(id="graphdecile"),
                                    ]
                                )
                            ]
                            if not version_beta_sans_graph_pop
                            else []
                        ),
                        className="ui two stackable cards",
                    ),
                    className="ten wide column",
                ),
            ],
            className="ui grid",
            style={"margin": "2em"},
        ),
    ]
)

# Generates reform text from input. Actually should run the simulations...


@app.callback(
    Output(component_id="output-seuil0", component_property="children"),
    [Input(component_id="input-seuil0", component_property="value")],
)
def output_seuil0(input1):
    return str(input1)
    # return u"""
    # def reform_from_bareme(seuilsthreshold=None):
    #     def TheReform(parameters):
    #         reform_period = periods.period("year:1900:200")
    #         parameters.impot_revenu.plafond_qf.maries_ou_pacses.update(period=reform_period, value={})
    #         return parameters
    # return TheReform""".format(input1)#.replace("\n","\r\n\r\n"))


@app.callback(
    Output(component_id="output-seuil1", component_property="children"),
    [Input(component_id="input-seuil1", component_property="value")],
)
def output_seuil1(input1):
    return str(input1)


@app.callback(
    Output(component_id="output-seuil2", component_property="children"),
    [Input(component_id="input-seuil2", component_property="value")],
)
def output_seuil2(input1):
    return str(input1)


@app.callback(
    Output(component_id="output-seuil3", component_property="children"),
    [Input(component_id="input-seuil3", component_property="value")],
)
def output_seuil3(input1):
    return str(input1)


nbseuil = 4

# Maybe I can do that ? (i.e. the if is gonna work properly with the callback
if not version_beta_sans_graph_pop:
    # Generates results for the graphs depending on the simulation on the full population
    @app.callback(
        [
            Output(component_id="graphtotal", component_property="figure"),
            Output(component_id="graphdecile", component_property="figure"),
        ],
        [Input(component_id="submit-button", component_property="n_clicks")],
        [
            State(
                component_id="input-seuil{}".format(numseuil),
                component_property="value",
            )
            for numseuil in range(nbseuil)
        ]
        + [
            State(
                component_id="input-taux{}".format(numseuil), component_property="value"
            )
            for numseuil in range(nbseuil)
        ],
    )
    def get_reform_result(n_clicks, *args):
        if not API_mode:
            myres = simulate_pop_from_reform.CompareOldNew(
                [int(k) for k in args], isdecile=True
            )  # [input1,input1]#
        else:
            myres = api_resultat_simulation(
                args[: len(args) // 2], args[len(args) // 2 :], True
            )
        print(myres)
        return (
            {
                "data": [
                    {
                        "x": ["avant"],
                        "y": [myres["total"]["avant"]],
                        "type": "bar",
                        "name": u"avant",
                    },
                    {
                        "x": ["après"],
                        "y": [myres["total"]["apres"]],
                        "type": "bar",
                        "name": u"après",
                    },
                    {
                        "x": ["impact"],
                        "y": [myres["total"]["apres"] - myres["total"]["avant"]],
                        "type": "bar",
                        "name": "impact",
                    },
                ],
                "layout": {"title": "Impact du changement"},
            },
            {
                "data": [
                    {
                        "x": ["decile {}".format(i)],
                        "y": [myres["deciles"][i][2] - myres["deciles"][i][1]],
                        "type": "bar",
                        "name": "decile {}".format(i),
                    }
                    for i in range(len(myres["deciles"]))
                ],
                "layout": {"title": "changement par décile"},
            },
        )


# Generates results for the graphs depending on the simulation on the full population
nbseuil = 4

nbgraphs = 6

if False:

    @app.callback(
        [
            Output(component_id="graph-ct{}".format(k), component_property="figure")
            for k in range(nbgraphs)
        ]
        + [
            Output(component_id="impact-ct{}".format(k), component_property="children")
            for k in range(nbgraphs)
        ],
        # [Input(component_id="submit-button", component_property="n_clicks")],
        [
            Input(
                component_id="input-seuil{}".format(numseuil),
                component_property="value",
            )
            for numseuil in range(nbseuil)
        ]
        + [
            Input(
                component_id="input-taux{}".format(numseuil), component_property="value"
            )
            for numseuil in range(nbseuil)
        ],
    )
    def get_reform_result_castypes(*args):
        print("computing castypes")
        if not API_mode:
            myres = simulate_pop_from_reform.CompareOldNew(
                [int(k) for k in args], isdecile=False
            )  # [input1,input1]#
        else:
            myres = api_resultat_simulation(
                args[: len(args) // 2], args[len(args) // 2 :], False
            )
        print(myres)
        df = myres["res_brut"]
        indextotake = []
        for index, _name in enumerate(names):
            try:
                print("alors :", index, df["avant"][index], df["apres"][index])
            except KeyError:
                index = str(index)
                print(
                    "alors (les index sont foireux, j ai du les stringer):",
                    index,
                    df["avant"][index],
                    df["apres"][index],
                )
            indextotake += [index]
        resforcastypes = [
            {
                "data": [
                    {
                        "x": ["avant"],
                        "y": [-df["avant"][indextotake[index]]],
                        "type": "bar",
                        "name": u"avant",
                    },
                    {
                        "x": ["après"],
                        "y": [-df["apres"][indextotake[index]]],
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
            }
            for index, _name in enumerate(names)
        ]
        resforcastypes += [
            -df["apres"][indextotake[index]] + df["avant"][indextotake[index]]
            for index, _name in enumerate(names)
        ]
        print(*resforcastypes)
        return (*resforcastypes,)


else:

    @app.callback(
        [
            Output(
                component_id="graphtot-ct{}".format(k), component_property="children"
            )
            for k in range(nbgraphs)
        ],
        # [Input(component_id="submit-button", component_property="n_clicks")],
        [
            Input(
                component_id="input-seuil{}".format(numseuil),
                component_property="value",
            )
            for numseuil in range(nbseuil)
        ]
        + [
            Input(
                component_id="input-taux{}".format(numseuil), component_property="value"
            )
            for numseuil in range(nbseuil)
        ],
    )
    def get_reform_result_castypes_mieux(*args):
        print("computing castypes")
        if not API_mode:
            myres = simulate_pop_from_reform.CompareOldNew(
                [int(k) for k in args], isdecile=False
            )  # [input1,input1]#
        else:
            myres = api_resultat_simulation(
                args[: len(args) // 2], args[len(args) // 2 :], False
            )
        print(myres)
        df = myres["res_brut"]
        indextotake = []
        for index, _name in enumerate(names):
            try:
                print("alors :", index, df["avant"][index], df["apres"][index])
            except KeyError:
                index = str(index)
                print(
                    "alors (les index sont foireux, j ai du les stringer):",
                    index,
                    df["avant"][index],
                    df["apres"][index],
                )
            indextotake += [index]
        resforcastypes = [
            GraphCasType.rendermieux(
                index, df["avant"][index], df["apres"][index], revenu=revenusCT[index]
            )
            for index, _name in enumerate(names)
        ]
        print(*resforcastypes)
        return (*resforcastypes,)


# Generates graph

# @app.callback(Output(component_id='w-graph',component_property= 'figure'),
#               [Input(component_id='result-reform', component_property='children')])
# def update_graph(input1):
#     myres=input1
#     print("Moi je suis update_graph et j'ai fini : ",myres)
#     return {
#             'data': #[
# #                {'x': ["avant"], 'y': [myres[0]], 'type': 'bar', 'name': u'avant'},
# #                {'x': ["après"], 'y': [myres[1]], 'type': 'bar', 'name': 'après'},
# #                {'x': ["impact"], 'y': [myres[1]-myres[0]], 'type': 'bar', 'name': 'impact'}
# #            ]
#             [{'x' : ["decile {}".format(i)], 'y':[myres[2+i][2]-myres[2+i][1]] , 'type':'bar', 'name' :"decile {}".format(i)} for i in range(10)]
#         ,
#             'layout': {
#                 'title': 'Impact du changement'
#             }
#         }


if __name__ == "__main__":
    app.run_server(
        host=os.environ.get("HOST", "127.0.0.1"), port=os.environ.get("PORT", "8050")
    )
