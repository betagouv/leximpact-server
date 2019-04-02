# -*- coding: utf-8 -*-

import dash_html_components as html


class Header(object):
    def render() -> html:
        return html.Header(
            [
                html.H1("LEXIMPACT"),
                html.Ul(
                    [html.Li("About me"), html.Li("Stuff"), html.Li("Mes amendements")]
                ),
            ]
        )
