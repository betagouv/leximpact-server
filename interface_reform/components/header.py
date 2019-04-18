# -*- coding: utf-8 -*-

import dash_html_components as html


class Header(object):
    def render() -> html:
        return html.Header(
            html.Div(Header._navbar(), className="ui container"),
            className="ui segment inverted",
        )

    def _navbar() -> html:
        return html.Div(
            [
                Header._item("LEXIMPACT", className="header item"),
                Header._item("Simulateur de l'impôt sur le revenu", className="active"),
                Header._item(
                    "Vos retours !",
                    href="mailto:leximpact@openfisca.org",
                    className="ui inverted right button",
                ),
            ],
            className="ui secondary menu inverted",
            style={"font-size":"120%", "margin-bottom":"-0.5em", "margin-top":"-0.5em","padding-right":"20px"}
        )

    def _item(content: str, href: str = "#", className: str = "") -> html:
        return html.A(content, href=href, className=f"ui item {className}")
