from typing import Callable, NamedTuple, TypeVar

from toolz.functoolz import compose  # type: ignore

from Simulation_engine.lexception import LexCeption
from openfisca_core.parameters import ParameterNode  # type: ignore
from openfisca_core import periods  # type: ignore
from openfisca_france import FranceTaxBenefitSystem  # type: ignore
from openfisca_france.model.base import (  # type: ignore
    Reform,
    Variable,
    FoyerFiscal,
    YEAR,
    not_,
    min_,
    max_,
    TypesStatutMarital,
)
from numpy import take  # type: ignore

T = TypeVar("T", bound="ParametricReform")


def generate_nbptr_class(
    calcul_nb_parts
):  # redéfinit le calcul des nbptr si spécifié par l'utilisateur
    situations_familiales = ["veuf", "mariesOuPacses", "celibataire", "divorce"]
    for nom_rubrique in [
        "partsSelonNombrePAC",
        "partsParPACAuDela",
        "partsParPACChargePartagee",
    ]:
        if nom_rubrique not in calcul_nb_parts:
            raise LexCeption(
                "the field '{}' is missing from 'calculNombreParts'. You can refer to the README to check valid format.".format(
                    nom_rubrique
                )
            )
    parts_pac_array_of_objects = calcul_nb_parts["partsSelonNombrePAC"]
    nb_cases_tableau = len(parts_pac_array_of_objects)
    for nb_pac in range(nb_cases_tableau):
        for nom_situation in situations_familiales:
            if nom_situation not in parts_pac_array_of_objects[nb_pac]:
                raise LexCeption(
                    "the field '{}' is missing from {}-th element of 'partsSelonNombrePAC'. You can refer to the README to check valid format.".format(
                        nom_situation, nb_pac + 1
                    )
                )

    parts_pac_tableau = {
        nom_situation: [
            parts_pac_array_of_objects[nb_enfant][nom_situation]
            for nb_enfant in range(nb_cases_tableau)
        ]
        for nom_situation in situations_familiales
    }

    nb_enfants_tableau = nb_cases_tableau - 1  # car le zéro est décrit dans le tableau
    parts_supp_cp = calcul_nb_parts["partsParPACChargePartagee"]
    for nb_cp in [
        "zeroChargePrincipale",
        "unChargePrincipale",
        "deuxOuPlusChargePrincipale",
    ]:
        if nb_cp not in parts_supp_cp:
            raise LexCeption(
                "the field '{}' is missing from 'partsParPACChargePartagee'. You can refer to the README to check valid format.".format(
                    nb_cp
                )
            )

    bonus_isole = calcul_nb_parts["bonusParentIsole"]

    class nbptr(Variable):
        value_type = float
        entity = FoyerFiscal
        label = "Nombre de parts"
        reference = "http://vosdroits.service-public.fr/particuliers/F2705.xhtml"
        definition_period = YEAR

        def formula(foyer_fiscal, period, parameters):
            """
            Nombre de parts du foyer fiscal

            note 1 enfants et résidence alternée (formulaire 2041 GV page 10)

            quotient_familial.conj : nb part associées au conjoint d'un couple marié ou pacsé
            quotient_familial.enf1 : nb part 2 premiers enfants
            quotient_familial.enf2 : nb part enfants de rang 3 ou plus
            quotient_familial.inv1 : nb part supp enfants invalides (I, G)
            quotient_familial.inv2 : nb part supp adultes invalides (R)
            quotient_familial.not31 : nb part supp note 3 : cases W ou G pour veuf, celib ou div
            quotient_familial.not32 : nb part supp note 3 : personne seule ayant élevé des enfants
            quotient_familial.not41 : nb part supp adultes invalides (vous et/ou conjoint) note 4
            quotient_familial.not42 : nb part supp adultes anciens combattants (vous et/ou conjoint) note 4
            quotient_familial.not6 : nb part supp note 6
            quotient_familial.isol : demi-part parent isolé (T)
            quotient_familial.edcd : enfant issu du mariage avec conjoint décédé;
            """
            nb_pac = foyer_fiscal("nb_pac", period)
            mariesOuPacses = foyer_fiscal("mariesOuPacses", period)
            celibataire_ou_divorce = foyer_fiscal("celibataire_ou_divorce", period)
            veuf = foyer_fiscal("veuf", period)
            jeune_veuf = foyer_fiscal("jeune_veuf", period)
            # nbF = foyer_fiscal("nbF", period)
            nbG = foyer_fiscal("nbG", period)
            nbH = foyer_fiscal("nbH", period)
            nbI = foyer_fiscal("nbI", period)
            nbR = foyer_fiscal("nbR", period)
            # nbJ = foyer_fiscal("nbJ", period)
            # nbN = foyer_fiscal("nbN", period)  # noqa F841
            caseP = foyer_fiscal("caseP", period)
            caseW = foyer_fiscal("caseW", period)
            caseG = foyer_fiscal("caseG", period)
            caseE = foyer_fiscal("caseE", period)
            caseK = foyer_fiscal("caseK", period)
            caseN = foyer_fiscal("caseN", period)
            caseF = foyer_fiscal("caseF", period)
            caseS = foyer_fiscal("caseS", period)
            caseL = foyer_fiscal("caseL", period)
            caseT = foyer_fiscal("caseT", period.first_month)
            quotient_familial = parameters(period).impot_revenu.quotient_familial

            no_pac = nb_pac == 0  # Aucune personne à charge en garde exclusive
            has_pac = not_(no_pac)
            no_alt = nbH == 0  # Aucun enfant à charge en garde alternée
            has_alt = not_(no_alt)
            # Ici on calcule plutôt d'abord le nombre de parts liées au nb d'enfants en charge principale

            def nb_enfants_principal(situation="celibataire"):
                def fonction_parts_gagnees(nb_charge_principale=1):
                    return (
                        parts_pac_tableau[situation][nb_enfants_tableau]
                        + (nb_charge_principale - nb_enfants_tableau)
                        * calcul_nb_parts["partsParPACAuDela"]
                    ) * (nb_charge_principale > nb_enfants_tableau) + (
                        nb_charge_principale <= nb_enfants_tableau
                    ) * take(
                        parts_pac_tableau[situation],
                        min_(nb_enfants_tableau, nb_charge_principale),
                    )

                return fonction_parts_gagnees

            statut_marital = foyer_fiscal.declarant_principal(
                "statut_marital", period.first_month
            )
            celib = statut_marital == TypesStatutMarital.celibataire
            divorce = statut_marital == TypesStatutMarital.divorce
            nb_pac = nb_pac.astype(int)
            enf3 = (
                celib * nb_enfants_principal("celibataire")(nb_pac)
                + divorce * nb_enfants_principal("divorce")(nb_pac)
                + mariesOuPacses * nb_enfants_principal("mariesOuPacses")(nb_pac)
                + veuf * nb_enfants_principal("veuf")(nb_pac)
            )

            # # nombre de parts liées aux enfants à charge
            # que des enfants en résidence alternée
            enf1 = (no_pac & has_alt) * (
                parts_supp_cp["zeroChargePrincipale"]["deuxPremiers"] * min_(nbH, 2)
                + parts_supp_cp["zeroChargePrincipale"]["suivants"] * max_(nbH - 2, 0)
            )
            # pas que des enfants en résidence alternée
            enf2 = (has_pac & has_alt) * (
                (nb_pac == 1)
                * (
                    parts_supp_cp["unChargePrincipale"]["premier"] * min_(nbH, 1)
                    + parts_supp_cp["unChargePrincipale"]["suivants"] * max_(nbH - 1, 0)
                )
                + (nb_pac > 1)
                * (parts_supp_cp["deuxOuPlusChargePrincipale"]["suivants"] * nbH)
            )
            # pas d'enfant en résidence alternée
            # enf3 = quotient_familial.enf1 * min_(nb_pac, 2) + quotient_familial.enf2 * max_((nb_pac - 2), 0)

            enf = enf1 + enf2 + enf3
            # # note 2 : nombre de parts liées aux invalides (enfant + adulte)
            n2 = quotient_familial.inv1 * (nbG + nbI / 2) + quotient_familial.inv2 * nbR

            # # note 3 : Pas de personne à charge
            # - invalide

            n31a = quotient_familial.not31a * (no_pac & no_alt & caseP)
            # - ancien combatant
            n31b = quotient_familial.not31b * (no_pac & no_alt & (caseW | caseG))
            n31 = max_(n31a, n31b)
            # - personne seule ayant élevé des enfants
            n32 = quotient_familial.not32 * (
                no_pac & no_alt & ((caseE | caseK | caseL) & not_(caseN))
            )
            n3 = max_(n31, n32)
            # # note 4 Invalidité de la personne ou du conjoint pour les mariés ou
            # # jeunes veuf(ve)s
            n4 = max_(
                quotient_familial.not41 * (1 * caseP + 1 * caseF),
                quotient_familial.not42 * (caseW | caseS),
            )

            # # note 5
            #  - enfant du conjoint décédé
            # n51 = quotient_familial.cdcd * (caseL & ((nbF + nbJ) > 0))
            #  - enfant autre et parent isolé
            # n52 = quotient_familial.isol * caseT * (((no_pac & has_alt) * ((nbH == 1) * 0.5 + (nbH >= 2))) + 1 * has_pac)
            # n5 = max_(n51, n52)

            # # note 6 invalide avec personne à charge
            n6 = quotient_familial.not6 * (caseP & (has_pac | has_alt))

            # # note 7 Parent isolé["auMoinsUnChargePrincipale"]
            n7 = caseT * (
                (no_pac & has_alt)
                * (
                    (nbH == 1) * bonus_isole["zeroChargePrincipaleUnPartage"]
                    + (nbH >= 2) * bonus_isole["zeroChargeprincipaleDeuxOuPlusPartage"]
                )
                + bonus_isole["auMoinsUnChargePrincipale"] * has_pac
            )
            # # Régime des mariés ou pacsés
            nb_parts_famille = enf + n2 + n4

            # # veufs  hors jeune_veuf
            nb_parts_veuf = enf + n2 + n3 + n6

            # # celib div
            nb_parts_celib = enf + n2 + n3 + n6 + n7
            return (
                (mariesOuPacses | jeune_veuf) * nb_parts_famille
                + (veuf & not_(jeune_veuf)) * nb_parts_veuf
                + celibataire_ou_divorce * nb_parts_celib
            )

    return nbptr


class IncomeTaxReform(Reform):
    """Une réforme de l'impôt sur le revenu"""

    def __init__(self, tbs: FranceTaxBenefitSystem, payload: dict, period: str) -> None:
        self.payload = payload.get("impot_revenu", {})
        self.instant = periods.instant(period)
        self.period = periods.period("year:1900:200")
        super().__init__(tbs)

    def modifier(self, parameters: ParameterNode) -> ParameterNode:
        reform = ParametricReform(parameters, self.payload, self.instant, self.period)
        parameters, *_ = compose(*reforms(mapping(), self.payload))(reform)
        return parameters

    def apply(self) -> None:
        if "calculNombreParts" in self.payload:
            function_nbptr = generate_nbptr_class(self.payload["calculNombreParts"])
            self.update_variable(function_nbptr)
        self.modify_parameters(modifier_function=self.modifier)


class ParametricReform(NamedTuple):
    """Une réforme paramétrique"""

    parameters: ParameterNode
    payload: dict
    instant: periods.Instant
    period: periods.Period

    def __call__(self: T, function: Callable[[T], T]) -> T:
        return function(self)


def reforms(mapping: dict, payload: dict) -> tuple:
    return tuple(mapping[reform] for reform in tuple(payload) if reform in mapping)


def mapping() -> dict:
    return {
        "decote": decote,
        "bareme": bareme,
        "abattements_rni": abattements_rni,
        "plafond_qf": compose(plafond_qf, abat_dom, reduction_ss_condition_revenus),
    }


def update(items, keys, node, period):
    for (key, value) in items:
        if key in keys:
            parameter = getattr(node, key)
            parameter.update(period=period, value=float(value))


def bareme(reform: T) -> T:
    seuils = reform.payload.get("bareme", {}).get("seuils")
    taux = reform.payload.get("bareme", {}).get("taux")
    node = reform.parameters.impot_revenu.bareme.brackets

    if seuils:
        for i in range(len(seuils)):
            node[i].threshold.update(period=reform.period, value=seuils[i])

        for i in range(len(seuils), len(node) - 1):
            node[i].threshold.update(period=reform.period, value=seuils[-1] + i)

    if taux:
        for i in range(len(taux)):
            node[i].rate.update(period=reform.period, value=taux[i])

        for i in range(len(taux), len(node) - 1):
            node[i].rate.update(period=reform.period, value=taux[-1])

    return type(reform)(*reform)


def decote(reform: T) -> T:
    seuil_couple = reform.payload.get("decote", {}).get("seuil_couple")
    seuil_celib = reform.payload.get("decote", {}).get("seuil_celib")
    taux = reform.payload.get("decote", {}).get("taux")
    node = reform.parameters.impot_revenu.decote

    if seuil_couple is not None:
        node.seuil_couple.update(period=reform.period, value=float(seuil_couple))

    if seuil_celib is not None:
        node.seuil_celib.update(period=reform.period, value=float(seuil_celib))

    if taux is not None:
        node.taux.update(period=reform.period, value=float(taux))
    return type(reform)(*reform)


def abattements_rni(reform: T) -> T:
    abattements_rni = reform.payload.get("abattements_rni", {})
    payload = abattements_rni.get("personne_agee_ou_invalide", {})
    node = reform.parameters.impot_revenu.abattements_rni.personne_agee_ou_invalide
    keys = ["montant_1", "montant_2", "plafond_1", "plafond_2"]
    update(payload.items(), keys, node, reform.period)
    return type(reform)(*reform)


def plafond_qf(reform: T) -> T:
    payload = reform.payload.get("plafond_qf", {})
    node = reform.parameters.impot_revenu.plafond_qf
    keys = [
        "maries_ou_pacses",
        "celib_enf",
        "celib",
        "reduc_postplafond",
        "reduc_postplafond_veuf",
    ]
    update(payload.items(), keys, node, reform.period)
    return type(reform)(*reform)


def abat_dom(reform: T) -> T:
    plafond_qf = reform.payload.get("plafond_qf", {})
    payload = plafond_qf.get("abat_dom", {})
    node = reform.parameters.impot_revenu.plafond_qf.abat_dom
    keys = ["taux_GuadMarReu", "plaf_GuadMarReu", "taux_GuyMay", "plaf_GuyMay"]
    update(payload.items(), keys, node, reform.period)
    return type(reform)(*reform)


def reduction_ss_condition_revenus(reform: T) -> T:
    plafond_qf = reform.payload.get("plafond_qf", {})
    payload = plafond_qf.get("reduction_ss_condition_revenus", {})
    node = reform.parameters.impot_revenu.plafond_qf.reduction_ss_condition_revenus
    keys = ["seuil_maj_enf", "seuil1", "seuil2", "taux"]
    update(payload.items(), keys, node, reform.period)
    return type(reform)(*reform)
