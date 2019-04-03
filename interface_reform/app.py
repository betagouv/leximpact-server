# -*- coding: utf-8 -*-

import sys,os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from components import (
    Article,
    GraphCasType,
    Header,
)

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

url_css_to_add = ["https://fonts.googleapis.com/css?family=Lora:400,400i,700,700i|PT+Serif",
                 "https://fonts.googleapis.com/css?family=Lato"]
links_css_stylesheets =[html.Link(href=url,rel="stylesheet") for url in url_css_to_add]

names=["Martin","Bernard","Thomas","Petit","Robert","Richard"]
revenusCT= simulate_pop_from_reform.revenus_cas_types()

try:
    imgstarts=["./assets/ImagesCasTypes/"+namefile for namefile in sorted(os.listdir("./assets/ImagesCasTypes"))]
except:
    print("images not found in ./assets/ImagesCasTypes, trying in ./interface_reform/assets/ImagesCasTypes")
    imgstarts=["./interface_reform/assets/ImagesCasTypes/"+namefile for namefile in sorted(os.listdir("./interface_reform/assets/ImagesCasTypes"))]

halfwidthgraphs=False
graphsCT = [GraphCasType.render(index,imgstarts[index],halfwidth=halfwidthgraphs,name=names[index],revenu=revenusCT[index]) for index, _name in enumerate(names)]
nbsplit=2 if halfwidthgraphs else 1
graphsCTsplit = [html.P(graphsCT[x:x+nbsplit]) for x in range(0,len(graphsCT),nbsplit)]

texte_cas_types=simulate_pop_from_reform.texte_cas_types()

desc_cas_types=[html.P([k," : ",v]) for k,v in texte_cas_types.items()]

app.layout = html.Div([
    Header.render(),
    Article.render(**article_values),

    html.Div(
    graphsCTsplit+
    # [html.P(dcc.Graph(
        #      id='graph-ct0'
    #  )),
    #      html.P(dcc.Graph(
        #      id='graph-ct1'
    #  )),]+
        [html.P([html.Button(id='submit-button', n_clicks=0, children='population française'),dcc.Graph(id='graphtotal'),
            dcc.Graph(id='graphdecile')]
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
        for index, _name in enumerate(names):
            print("alors :")
            print(index)
            print(df[df.index==index],df["avant"][index],df["apres"][index])
        resforcastypes = [
            {
                'data': [
                    {'x': ["avant"], 'y': [-df["avant"][index]], 'type': 'bar', 'name': u'avant'},
                    {'x': ["après"], 'y': [-df["apres"][index]], 'type': 'bar', 'name': u'après'},
                    {'x': ["impact"], 'y': [-df["apres"][index] + df["avant"][index]], 'type': 'bar',
                     'name': 'impact'}
                ]
                #,
                #'layout': {
                #    'title': simulate_pop_from_reform.foyertotexte(index)
                #}
            } for index, _name in enumerate(names)]
        print(*resforcastypes)
        return (*resforcastypes,)
    else: #Does not run before the first click
        return tuple([None]*len(names))#


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
