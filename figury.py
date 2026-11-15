"""Tworzenie figur 3D i eksport do formatu STL w FreeCAD."""

from __future__ import annotations

from os import PathLike, fspath
from typing import Any


def create_hollow_cuboid_stl(
    length: float,
    width: float,
    height: float,
    wall_thickness: float = 0.2,
    output_path: str | PathLike[str] = "pusty_prostopadloscian.stl",
    name: str = "HollowCuboid",
    document: Any | None = None,
) -> str:
    """Utwórz pusty prostopadłościan i zapisz go jako plik STL.

    Wszystkie wymiary są podawane w tych samych jednostkach co w FreeCAD
    (zwykle w milimetrach). Prostopadłościan jest zamknięty i ma sześć ścian.

    Args:
        length: Wymiar w osi X.
        width: Wymiar w osi Y.
        height: Wymiar w osi Z.
        wall_thickness: Grubość każdej ściany; domyślnie 0.2.
        output_path: Ścieżka docelowego pliku STL.
        name: Nazwa obiektu w dokumencie FreeCAD.
        document: Opcjonalny dokument FreeCAD. Gdy go nie podasz, użyty
            zostanie aktywny dokument albo zostanie utworzony nowy.

    Returns:
        Ścieżkę do zapisanego pliku STL.

    Raises:
        ValueError: Gdy wymiary są niedodatnie albo ściana jest zbyt gruba.
        ImportError: Gdy funkcja zostanie uruchomiona poza FreeCAD.
    """
    if length <= 0 or width <= 0 or height <= 0:
        raise ValueError("length, width i height muszą być większe od zera")
    if wall_thickness <= 0:
        raise ValueError("wall_thickness musi być większe od zera")
    if 2 * wall_thickness >= min(length, width, height):
        raise ValueError(
            "wall_thickness musi być mniejsze niż połowa najmniejszego wymiaru"
        )

    try:
        import FreeCAD as App
        import Mesh
        import Part
    except ImportError as error:
        raise ImportError(
            "Tę funkcję należy uruchomić w środowisku FreeCAD"
        ) from error

    doc = document or App.ActiveDocument
    if doc is None:
        doc = App.newDocument()

    outer = Part.makeBox(length, width, height)
    inner = Part.makeBox(
        length - 2 * wall_thickness,
        width - 2 * wall_thickness,
        height - 2 * wall_thickness,
        App.Vector(wall_thickness, wall_thickness, wall_thickness),
    )
    hollow_cuboid = outer.cut(inner)

    obj = doc.addObject("Part::Feature", name)
    obj.Label = name
    obj.Shape = hollow_cuboid
    doc.recompute()

    path = fspath(output_path)
    Mesh.export([obj], path)
    return path

