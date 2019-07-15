from typing import Callable, List


def cas_types(reform: dict, cas_types: List[dict]) -> List[dict]:
    """Calcule l'impact d'une réforme par cas types"""
    return [{"name": impact(reform)(cas_type)} for cas_type in cas_types]


def impact(reform: dict) -> Callable:
    return lambda cas_type: cas_type[reform["variable"]] * int(reform["times"])
