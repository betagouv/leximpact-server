# -*- coding: utf-8 -*-

import dash_html_components as html


class Header(object):
    def render() -> html:
        return html.Header(
            html.Div(Header._navbar(), className="ui container"),
            className="ui vertical center aligned segment inverted",
        )

    def _navbar() -> html:
        return html.Div(
            [
                Header._item("LexImpact"),
                Header._item("Article 157 du CGI", className="active"),
                Header._item(
                    "Feedback", href="mailto:leximpact@openfisca.org", className="right"
                ),
            ],
            className="ui secondary pointing menu inverted",
        )

    def _item(content: str, href: str = "#", className: str = "") -> html:
        return html.A(content, href=href, className=f"ui item {className}")
