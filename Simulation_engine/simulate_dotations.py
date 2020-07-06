from dotations.impact import impacts_reforme_dotation, format_reforme_openfisca  # type: ignore


def simulate(request_body):
    simulation_result = impacts_reforme_dotation(format_reforme_openfisca(request_body["reforme"]))
    return simulation_result
