# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import drawing
from . import bom
from . import production


def register():
    Pool.register(
        drawing.Drawing,
        drawing.DrawingPosition,
        bom.BOM,
        bom.BOMDrawingLine,
        production.Production,
        production.ProductionDrawingLine,
        module='production_drawing', type_='model')
