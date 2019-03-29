# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import sys
try:
    sys.path.insert(0, './Simulation_engine')
    import simulate_pop_from_reform
except(Exception):
    sys.path.insert(0, './../Simulation_engine')
    import simulate_pop_from_reform

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

basevalue=9964

#app.config['suppress_callback_exceptions']=True

sizeperc=1
sizev=3


url_css_to_add = ["https://fonts.googleapis.com/css?family=Lora:400,400i,700,700i|PT+Serif",
                 "https://fonts.googleapis.com/css?family=Lato"]
links_css_stylesheets =[html.Link(href=url,rel="stylesheet") for url in url_css_to_add]

list_cas_types = [0, 1, 2, 3, 4, 5]

graphsCT = [dcc.Graph(id='graph-ct{}'.format(ct),className='outputstat six columns') for ct in list_cas_types]
graphsCTsplit = [html.P(graphsCT[x:x+2]) for x in range(0,len(graphsCT),2)]

app.layout = html.Div(links_css_stylesheets + [html.Div([html.H2("Article 197"),
    html.H3("code général des impôts"),
    html.Button(id='submit-button', n_clicks=0, children='Submit'),
    html.P("""I. – En ce qui concerne les contribuables visés à l'article 4 B, il est fait application des règles suivantes pour le calcul de l'impôt sur le revenu :"""),
    html.P(html.Div(["""1. L'impôt est calculé en appliquant à la fraction de chaque part de revenu qui excède """,
                     dcc.Input(id='input-seuil0', type='text', value=9964,size=sizev),"""€ le taux de :"""])),
    html.P(html.Div(["""– """, dcc.Input(id='input-taux0', type='text', value=14,size=sizeperc),"""% pour la fraction supérieure à """,
                     html.Nobr(id='output-seuil0'),
                     """ et inférieure ou égale à """, dcc.Input(id='input-seuil1', type='text', value=27519,size=sizev),"""€ ;"""])),
    html.P(html.Div(["""– """, dcc.Input(id='input-taux1', type='text', value=30,size=sizeperc),"""% pour la fraction supérieure à """,
                     html.Nobr(id='output-seuil1'),
                     """ € et inférieure ou égale à """, dcc.Input(id='input-seuil2', type='text', value=73779,size=sizev),"""€ ;"""])),
    html.P(html.Div(["""– """, dcc.Input(id='input-taux2', type='text', value=41,size=sizeperc),"""% pour la fraction supérieure à """,
                     html.Nobr(id='output-seuil2'),
                     """ € et inférieure ou égale à """, dcc.Input(id='input-seuil3', type='text', value=156244,size=sizev),"""€ ;"""])),
    html.P(html.Div(["""– """, dcc.Input(id='input-taux3', type='text', value=45,size=sizeperc),"""% pour la fraction supérieure à """,
                     html.Nobr(id='output-seuil3'),
                     """€"""])),
    html.Div(["""2. La réduction d'impôt résultant de l'application du quotient familial ne peut excéder""",
              """ 1 527 € par demi-part ou la moitié de cette somme par quart de part s'ajoutant à une part pour les contribuables célibataires, divorcés, veufs ou soumis à l'imposition distincte prévue au 4 de l'article 6 et à deux parts pour les contribuables mariés soumis à une imposition commune."""]),
    html.P("""Toutefois, pour les contribuables célibataires, divorcés, ou soumis à l'imposition distincte prévue au 4 de l'article 6 qui répondent aux conditions fixées au II de l'article 194, la réduction d'impôt correspondant à la part accordée au titre du premier enfant à charge est limitée à 3 660 € Lorsque les contribuables entretiennent uniquement des enfants dont la charge est réputée également partagée entre l'un et l'autre des parents, la réduction d'impôt correspondant à la demi-part accordée au titre de chacun des deux premiers enfants est limitée à la moitié de cette somme."""),
    html.P("""Par dérogation aux dispositions du premier alinéa, la réduction d'impôt résultant de l'application du quotient familial, accordée aux contribuables qui bénéficient des dispositions des a, b et e du 1 de l'article 195, ne peut excéder 927 € ;"""),
    html.P("""Les contribuables qui bénéficient d'une demi-part au titre des a, b, c, d, d bis, e et f du 1 ainsi que des 2 à 6 de l'article 195 ont droit à une réduction d'impôt égale à 1 547 € pour chacune de ces demi-parts lorsque la réduction de leur cotisation d'impôt est plafonnée en application du premier alinéa. La réduction d'impôt est égale à la moitié de cette somme lorsque la majoration visée au 2 de l'article 195 est de un quart de part. Cette réduction d'impôt ne peut toutefois excéder l'augmentation de la cotisation d'impôt résultant du plafonnement."""),
    html.P("""Les contribuables veufs ayant des enfants à charge qui bénéficient d'une part supplémentaire de quotient familial en application du I de l'article 194 ont droit à une réduction d'impôt égale à 1 728 € pour cette part supplémentaire lorsque la réduction de leur cotisation d'impôt est plafonnée en application du premier alinéa du présent 2. Cette réduction d'impôt ne peut toutefois excéder l'augmentation de la cotisation d'impôt résultant du plafonnement."""),
    html.P("""3. Le montant de l'impôt résultant de l'application des dispositions précédentes est réduit de 30 %, dans la limite de 2 450 €, pour les contribuables domiciliés dans les départements de la Guadeloupe, de la Martinique et de la Réunion ; cette réduction est égale à 40 %, dans la limite de 4 050 €, pour les contribuables domiciliés dans les départements de la Guyane et de Mayotte ;"""),
    html.P("""4. a. Le montant de l'impôt résultant de l'application des dispositions précédentes est diminué, dans la limite de son montant, de la différence entre 1 196 € et les trois quarts de son montant pour les contribuables célibataires, divorcés ou veufs et de la différence entre 1 970 € et les trois quarts de son montant pour les contribuables soumis à imposition commune."""),
    html.P("""b. Le montant de l'impôt résultant du a est réduit dans les conditions prévues au sixième alinéa du présent b pour les contribuables dont le montant des revenus du foyer fiscal, au sens du 1° du IV de l'article 1417, est inférieur à 20 500 €, pour la première part de quotient familial des personnes célibataires, veuves ou divorcées, et à 41 000 €, pour les deux premières parts de quotient familial des personnes soumises à une imposition commune. Ces seuils sont majorés de 3 700 € pour chacune des demi-parts suivantes et de la moitié de ce montant pour chacun des quarts de part suivants."""),
    html.P("""Pour l'application des seuils mentionnés au premier alinéa du présent b, le montant des revenus du foyer fiscal est majoré :"""),
    html.P("""1° Du montant des plus-values, déterminées le cas échéant avant application des abattements pour durée de détention mentionnés au 1 de 150-0 D bis, dans leur rédaction en vigueur jusqu'au 31 décembre 2013 ;"""),
    html.P("""2° Du montant des plus-values, déterminées le cas échéant avant application des abattements pour durée de détention mentionnés aux 1 ter ou 1 quater de l'article 150-0 D ou à l'article 150-0 D ter, et des créances mentionnées aux I et II de l'article 167 bis, pour la seule détermination du premier terme de la différence mentionnée au deuxième alinéa du 1 du II bis du même article 167 bis ;"""),
    html.P("""3° Du montant des plus-values mentionnées au I de 200 A pour l'application de la seconde phrase du 3° du même a."""),
    html.P("""Le taux de la réduction prévue au premier alinéa du présent b est de 20 %. Toutefois, pour les contribuables dont les revenus du foyer fiscal, au sens du 1° du IV de l'article 1417, excèdent 18 500 €, pour la première part de quotient familial des personnes célibataires, veuves ou divorcées, ou 37 000 €, pour les deux premières parts de quotient familial des personnes soumises à une imposition commune, ces seuils étant majorés le cas échéant dans les conditions prévues au même premier alinéa, le taux de la réduction d'impôt est égal à 20 % multiplié par le rapport entre :"""),
    html.P("""– au numérateur, la différence entre 20 500 €, pour les personnes célibataires, veuves ou divorcées, ou 41 000 €, pour les personnes soumises à une imposition commune, ces seuils étant majorés le cas échéant dans les conditions prévues audit premier alinéa, et le montant des revenus mentionnés au troisième alinéa du présent b, et ;"""),
    html.P("""– au dénominateur, 2 000 €, pour les personnes célibataires, veuves ou divorcées, ou 4 000 €, pour les personnes soumises à une imposition commune."""),
    html.P("""Les montants de revenus mentionnés au présent b sont révisés chaque année dans la même proportion que la limite supérieure de la première tranche du barème de l'impôt sur le revenu. Les montants obtenus sont arrondis, s'il y a lieu, à l'euro supérieur."""),
    html.P("""5. Les réductions d'impôt mentionnées aux articles 199 quater B à 200 s'imputent sur l'impôt résultant de l'application des dispositions précédentes avant imputation des crédits d'impôt et des prélèvements ou retenues non libératoires ; elles ne peuvent pas donner lieu à remboursement."""),
   # dcc.Input(id='input-seuil0', type='text', value='1527'),
    html.B(id='result-reform')
],className="inputarticle six columns"),
    html.Div(
    [html.Div(graphsCTsplit+
    # [html.P(dcc.Graph(
        #      id='graph-ct0'
    #  )),
    #      html.P(dcc.Graph(
        #      id='graph-ct1'
    #  )),]+
        [html.P([dcc.Graph(id='graphtotal',className="six columns"),
            dcc.Graph(id='graphdecile',className="six columns")])]
    )],className="five columns")],className="row")


# Generates reform text from input. Actually should run the simulations...

@app.callback(Output(component_id='output-seuil0', component_property= 'children'),
              [Input(component_id='input-seuil0',component_property=  'value')])
def output_seuil0(input1):
    return str(input1)
    # return u"""
    # def reform_from_bareme(seuilsthreshold=None):
    #     def TheReform(parameters):
    #         reform_period = periods.period("year:1900:200")
    #         parameters.impot_revenu.plafond_qf.maries_ou_pacses.update(period=reform_period, value={})
    #         return parameters
    # return TheReform""".format(input1)#.replace("\n","\r\n\r\n"))

@app.callback(Output(component_id='output-seuil1', component_property= 'children'),
              [Input(component_id='input-seuil1',component_property=  'value')])
def output_seuil1(input1):
    return str(input1)

@app.callback(Output(component_id='output-seuil2', component_property= 'children'),
              [Input(component_id='input-seuil2',component_property=  'value')])
def output_seuil2(input1):
    return str(input1)

@app.callback(Output(component_id='output-seuil3', component_property= 'children'),
              [Input(component_id='input-seuil3',component_property=  'value')])
def output_seuil3(input1):
    return str(input1)

# Generates results for the graphs depending on the simulation on the full population
nbseuil=4
@app.callback([Output(component_id='graphtotal',component_property= 'figure'),
               Output(component_id='graphdecile',component_property= 'figure')],
            [Input(component_id='submit-button', component_property='n_clicks')],
            [State(component_id='input-seuil{}'.format(numseuil), component_property='value') for numseuil in range(nbseuil)] +
              [State(component_id='input-taux{}'.format(numseuil), component_property='value') for numseuil in range(nbseuil)])
def get_reform_result(n_clicks,*args):
    if n_clicks:
        myres=simulate_pop_from_reform.CompareOldNew([int(k) for k in args],isdecile=True)#[input1,input1]#
        return {
                'data': [
                    {'x': ["avant"], 'y': [myres["total"]["avant"]], 'type': 'bar', 'name': u'avant'},
                    {'x': ["après"], 'y': [myres["total"]["apres"]], 'type': 'bar', 'name': u'après'},
                    {'x': ["impact"], 'y': [myres["total"]["apres"]-myres["total"]["avant"]], 'type': 'bar', 'name': 'impact'}
                ]
            ,
                'layout': {
                    'title': 'Impact du changement'
                }
            },{
                'data':
                [{'x' : ["decile {}".format(i)], 'y':[myres["deciles"][i][2]-myres["deciles"][i][1]] , 'type':'bar', 'name' :"decile {}".format(i)} for i in range(len(myres["deciles"]))]
            ,
                'layout': {
                    'title': 'changement par décile'
                }
            }
    else: #Does not run before the first click
        return None,None

# Generates results for the graphs depending on the simulation on the full population
nbseuil=4
@app.callback([Output(component_id='graph-ct0',component_property= 'figure') ,
                Output(component_id='graph-ct1',component_property= 'figure') ,
                Output(component_id='graph-ct2',component_property= 'figure') ,
                Output(component_id='graph-ct3',component_property= 'figure') ,
                Output(component_id='graph-ct4',component_property= 'figure') ,
                Output(component_id='graph-ct5',component_property= 'figure')],
            [Input(component_id='submit-button', component_property='n_clicks')],
            [State(component_id='input-seuil{}'.format(numseuil), component_property='value') for numseuil in range(nbseuil)] +
              [State(component_id='input-taux{}'.format(numseuil), component_property='value') for numseuil in range(nbseuil)])
def get_reform_result_castypes(n_clicks,*args):
    if n_clicks:
        print("computing castypes")
        myres=simulate_pop_from_reform.CompareOldNew([int(k) for k in args],isdecile=False)#[input1,input1]#
        print(myres)
        df=myres["res_brut"]
        for ct in list_cas_types:
            print("alors :")
            print(ct)
            print(df[df.index==ct],df["avant"][ct],df["apres"][ct])
        resforcastypes = [
            {
                'data': [
                    {'x': ["avant"], 'y': [-df["avant"][ct]], 'type': 'bar', 'name': u'avant'},
                    {'x': ["après"], 'y': [-df["apres"][ct]], 'type': 'bar', 'name': u'après'},
                    {'x': ["impact"], 'y': [-df["apres"][ct] + df["avant"][ct]], 'type': 'bar',
                     'name': 'impact'}
                ]
                ,
                'layout': {
                    'title': simulate_pop_from_reform.foyertotexte(ct)
                }
            } for ct in list_cas_types]
        print(*resforcastypes)
        return (*resforcastypes,)
    else: #Does not run before the first click
        return tuple([None]*len(list_cas_types))#


#Generates graph

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



if __name__ == '__main__':
    app.run_server(debug=True)
