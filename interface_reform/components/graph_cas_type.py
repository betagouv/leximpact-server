# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html


class GraphCasType(object):
    def render(index: int,addressimage  : str ,halfwidth=True,name=None,revenu=10000) -> html:
        return html.Table([html.Tr([html.Td(html.Img(src=addressimage)),html.Td(dcc.Graph(id='graph-ct{}'.format(index),className='outputstat six columns' if halfwidth else "outputstat"),rowSpan=2)]),html.Tr([html.Td("Famille {} : revenu de {}".format(name,revenu))])])