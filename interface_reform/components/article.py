# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html


class Article(object):
    def render(
        sizev: int,
        sizeperc: int,
        seuil0: int,
        taux0: int,
        seuil1: int,
        taux1: int,
        seuil2: int,
        taux2: int,
        seuil3: int,
        taux3: int,
    ) -> html:
        return html.Div(
            [
                html.H1(
                    [
                        "Article 197",
                        html.Div("Code Général des Impôts", className="sub header"),
                    ],
                    className="ui header dividing",
                ),
                html.P(
                    """I. – En ce qui concerne les contribuables visés à l'article 4 B, il est fait application des règles suivantes pour le calcul de l'impôt sur le revenu :"""
                ),
                html.P(
                    [
                        """1. L'impôt est calculé en appliquant à la fraction de chaque part de revenu qui excède """,
                        html.S(f"{seuil0} €"),
                        html.Div(
                            dcc.Input(
                                id="input-seuil0",
                                type="number",
                                value=seuil0,
                                style={"border-radius": 0, "height": "2em"},
                            ),
                            className="ui mini input",
                        ),
                        """ € """,
                        """le taux de : """,
                    ]
                ),
                html.Ol(
                    [
                        html.Li(
                            [
                                html.S(f"{taux0} %"),
                                """ """,
                                html.Div(
                                    dcc.Input(
                                        id="input-taux0",
                                        type="number",
                                        value=taux0,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ % """,
                                """pour la fraction supérieure à """,
                                html.Nobr(id="output-seuil0"),
                                """ € et inférieure ou égale à """,
                                html.S(f"{seuil1} €"),
                                html.Div(
                                    dcc.Input(
                                        id="input-seuil1",
                                        type="number",
                                        value=seuil1,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ € ; """,
                            ],
                            value="—",
                        ),
                        html.Li(
                            [
                                html.S(f"{taux1} %"),
                                """ """,
                                html.Div(
                                    dcc.Input(
                                        id="input-taux1",
                                        type="number",
                                        value=taux1,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ % """,
                                """pour la fraction supérieure à """,
                                html.Nobr(id="output-seuil1"),
                                """ € et inférieure ou égale à """,
                                html.S(f"{seuil2} €"),
                                html.Div(
                                    dcc.Input(
                                        id="input-seuil2",
                                        type="number",
                                        value=seuil2,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ € ; """,
                            ],
                            value="—",
                        ),
                        html.Li(
                            [
                                html.S(f"{taux2} %"),
                                """ """,
                                html.Div(
                                    dcc.Input(
                                        id="input-taux2",
                                        type="number",
                                        value=taux2,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ % """,
                                """pour la fraction supérieure à """,
                                html.Nobr(id="output-seuil2"),
                                """ € et inférieure ou égale à """,
                                html.S(f"{seuil3} €"),
                                html.Div(
                                    dcc.Input(
                                        id="input-seuil3",
                                        type="number",
                                        value=seuil3,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ € ; """,
                            ],
                            value="—",
                        ),
                        html.Li(
                            [
                                html.S(f"{taux3} %"),
                                """ """,
                                html.Div(
                                    dcc.Input(
                                        id="input-taux3",
                                        type="number",
                                        value=taux3,
                                        style={"border-radius": 0, "height": "2em"},
                                    ),
                                    className="ui mini input",
                                ),
                                """ % """,
                                """pour la fraction supérieure à """,
                                html.Nobr(id="output-seuil3"),
                                """ € """,
                            ],
                            value="—",
                        ),
                    ],
                    className="ui list",
                ),
                html.Div(
                    [
                        """2. La réduction d'impôt résultant de l'application du quotient familial ne peut excéder""",
                        """ 1 527 € par demi-part ou la moitié de cette somme par quart de part s'ajoutant à une part pour les contribuables célibataires, divorcés, veufs ou soumis à l'imposition distincte prévue au 4 de l'article 6 et à deux parts pour les contribuables mariés soumis à une imposition commune.""",
                    ]
                ),
                html.P(
                    """Toutefois, pour les contribuables célibataires, divorcés, ou soumis à l'imposition distincte prévue au 4 de l'article 6 qui répondent aux conditions fixées au II de l'article 194, la réduction d'impôt correspondant à la part accordée au titre du premier enfant à charge est limitée à 3 660 € Lorsque les contribuables entretiennent uniquement des enfants dont la charge est réputée également partagée entre l'un et l'autre des parents, la réduction d'impôt correspondant à la demi-part accordée au titre de chacun des deux premiers enfants est limitée à la moitié de cette somme."""
                ),
                html.P(
                    """Par dérogation aux dispositions du premier alinéa, la réduction d'impôt résultant de l'application du quotient familial, accordée aux contribuables qui bénéficient des dispositions des a, b et e du 1 de l'article 195, ne peut excéder 927 € ;"""
                ),
                html.P(
                    """Les contribuables qui bénéficient d'une demi-part au titre des a, b, c, d, d bis, e et f du 1 ainsi que des 2 à 6 de l'article 195 ont droit à une réduction d'impôt égale à 1 547 € pour chacune de ces demi-parts lorsque la réduction de leur cotisation d'impôt est plafonnée en application du premier alinéa. La réduction d'impôt est égale à la moitié de cette somme lorsque la majoration visée au 2 de l'article 195 est de un quart de part. Cette réduction d'impôt ne peut toutefois excéder l'augmentation de la cotisation d'impôt résultant du plafonnement."""
                ),
                html.P(
                    """Les contribuables veufs ayant des enfants à charge qui bénéficient d'une part supplémentaire de quotient familial en application du I de l'article 194 ont droit à une réduction d'impôt égale à 1 728 € pour cette part supplémentaire lorsque la réduction de leur cotisation d'impôt est plafonnée en application du premier alinéa du présent 2. Cette réduction d'impôt ne peut toutefois excéder l'augmentation de la cotisation d'impôt résultant du plafonnement."""
                ),
                html.P(
                    """3. Le montant de l'impôt résultant de l'application des dispositions précédentes est réduit de 30 %, dans la limite de 2 450 €, pour les contribuables domiciliés dans les départements de la Guadeloupe, de la Martinique et de la Réunion ; cette réduction est égale à 40 %, dans la limite de 4 050 €, pour les contribuables domiciliés dans les départements de la Guyane et de Mayotte ;"""
                ),
                html.P(
                    """4. a. Le montant de l'impôt résultant de l'application des dispositions précédentes est diminué, dans la limite de son montant, de la différence entre 1 196 € et les trois quarts de son montant pour les contribuables célibataires, divorcés ou veufs et de la différence entre 1 970 € et les trois quarts de son montant pour les contribuables soumis à imposition commune."""
                ),
                html.P(
                    """b. Le montant de l'impôt résultant du a est réduit dans les conditions prévues au sixième alinéa du présent b pour les contribuables dont le montant des revenus du foyer fiscal, au sens du 1° du IV de l'article 1417, est inférieur à 20 500 €, pour la première part de quotient familial des personnes célibataires, veuves ou divorcées, et à 41 000 €, pour les deux premières parts de quotient familial des personnes soumises à une imposition commune. Ces seuils sont majorés de 3 700 € pour chacune des demi-parts suivantes et de la moitié de ce montant pour chacun des quarts de part suivants."""
                ),
                html.P(
                    """Pour l'application des seuils mentionnés au premier alinéa du présent b, le montant des revenus du foyer fiscal est majoré :"""
                ),
                html.P(
                    """1° Du montant des plus-values, déterminées le cas échéant avant application des abattements pour durée de détention mentionnés au 1 de 150-0 D bis, dans leur rédaction en vigueur jusqu'au 31 décembre 2013 ;"""
                ),
                html.P(
                    """2° Du montant des plus-values, déterminées le cas échéant avant application des abattements pour durée de détention mentionnés aux 1 ter ou 1 quater de l'article 150-0 D ou à l'article 150-0 D ter, et des créances mentionnées aux I et II de l'article 167 bis, pour la seule détermination du premier terme de la différence mentionnée au deuxième alinéa du 1 du II bis du même article 167 bis ;"""
                ),
                html.P(
                    """3° Du montant des plus-values mentionnées au I de 200 A pour l'application de la seconde phrase du 3° du même a."""
                ),
                html.P(
                    """Le taux de la réduction prévue au premier alinéa du présent b est de 20 %. Toutefois, pour les contribuables dont les revenus du foyer fiscal, au sens du 1° du IV de l'article 1417, excèdent 18 500 €, pour la première part de quotient familial des personnes célibataires, veuves ou divorcées, ou 37 000 €, pour les deux premières parts de quotient familial des personnes soumises à une imposition commune, ces seuils étant majorés le cas échéant dans les conditions prévues au même premier alinéa, le taux de la réduction d'impôt est égal à 20 % multiplié par le rapport entre :"""
                ),
                html.P(
                    """– au numérateur, la différence entre 20 500 €, pour les personnes célibataires, veuves ou divorcées, ou 41 000 €, pour les personnes soumises à une imposition commune, ces seuils étant majorés le cas échéant dans les conditions prévues audit premier alinéa, et le montant des revenus mentionnés au troisième alinéa du présent b, et ;"""
                ),
                html.P(
                    """– au dénominateur, 2 000 €, pour les personnes célibataires, veuves ou divorcées, ou 4 000 €, pour les personnes soumises à une imposition commune."""
                ),
                html.P(
                    """Les montants de revenus mentionnés au présent b sont révisés chaque année dans la même proportion que la limite supérieure de la première tranche du barème de l'impôt sur le revenu. Les montants obtenus sont arrondis, s'il y a lieu, à l'euro supérieur."""
                ),
                html.P(
                    """5. Les réductions d'impôt mentionnées aux articles 199 quater B à 200 s'imputent sur l'impôt résultant de l'application des dispositions précédentes avant imputation des crédits d'impôt et des prélèvements ou retenues non libératoires ; elles ne peuvent pas donner lieu à remboursement."""
                ),
                html.B(id="result-reform"),
            ],
            className="eight wide column",
        )
