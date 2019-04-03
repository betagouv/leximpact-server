# -*- coding: utf-8 -*-

import dash_core_components as dcc


class GraphCasType(object):
    def render(index: int) -> dcc:
        return dcc.Graph(id=f"graph-ct{index}", className="outputstat six columns")
