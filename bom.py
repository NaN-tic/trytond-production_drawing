from trytond.model import ModelSQL, ModelView, fields, Unique
from trytond.pyson import Eval, Bool
from trytond.pool import PoolMeta, Pool


class BOM(metaclass=PoolMeta):
    __name__ = 'production.bom'
    drawing = fields.Many2One('production.drawing', 'Drawing',
        ondelete='RESTRICT')
    drawing_lines = fields.One2Many('production.bom.drawing.line',
        'bom', 'Drawing Positions', states={
            'invisible': ~Bool(Eval('drawing')),
            })
    drawing_image = fields.Function(fields.Binary('Drawing Image'),
        'on_change_with_drawing_image')

    @fields.depends('drawing', 'drawing_lines')
    def on_change_with_drawing_lines(self):
        DrawingLine = Pool().get('production.bom.drawing.line')
        if not self.drawing:
            return []
        res = []
        for position in self.drawing.positions:
            res.append(DrawingLine(position=position))
        return res

    @fields.depends('drawing')
    def on_change_with_drawing_image(self, name=None):
        return self.drawing.image if self.drawing else None


class BOMDrawingLine(ModelSQL, ModelView):
    'Production BOM Drawing Line'
    __name__ = 'production.bom.drawing.line'
    bom = fields.Many2One('production.bom', 'BOM', required=True,
        ondelete='CASCADE')
    position = fields.Many2One('production.drawing.position',
        'Drawing Position', required=True, ondelete='RESTRICT', domain=[
            ('drawing', '=', Eval('drawing', -1)),
            ], states={
            'readonly': True,
            })
    drawing = fields.Function(fields.Many2One('production.drawing', 'Drawing'),
        'get_drawing')
    product = fields.Many2One('product.product', 'Product',
        ondelete='RESTRICT')

    @classmethod
    def __setup__(cls):
        super(BOMDrawingLine, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('check_bom_drawing_line_uniq', Unique(t, t.bom, t.position),
                'Drawing Position must be unique per BOM.'),
            ]

    def get_drawing(self, name):
        return self.bom.drawing.id if self.bom.drawing else None
