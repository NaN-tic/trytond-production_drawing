from trytond.model import ModelSQL, ModelView, fields, Unique
from trytond.pyson import Eval, Bool
from trytond.pool import PoolMeta, Pool

__all__ = ['Production', 'ProductionDrawingLine']


class Production(metaclass=PoolMeta):
    __name__ = 'production'
    drawing = fields.Many2One('production.drawing', 'Drawing',
        ondelete='RESTRICT', states={
            'readonly': True,
            })
    drawing_lines = fields.One2Many('production.drawing.line',
        'production', 'Drawing Positions', states={
            'invisible': ~Bool(Eval('drawing')),
            })
    drawing_image = fields.Function(fields.Binary('Drawing Image'),
        'on_change_with_drawing_image')

    @fields.depends('bom', 'drawing_lines')
    def on_change_bom(self):
        super(Production, self).on_change_bom()
        self.drawing = (self.bom.drawing.id if self.bom and self.bom.drawing
            else None)
        self.on_change_with_drawing_image()
        self.on_change_with_drawing_lines()

    @fields.depends('bom', 'drawing', 'drawing_lines')
    def on_change_with_drawing_lines(self):
        Line = Pool().get('production.drawing.line')

        if not self.bom or not self.bom.drawing and hasattr(self, 'drawing_lines'):
            return []
        res = []
        for line in self.bom.drawing_lines:
            res.append(Line(
                    position=line.position,
                    product=line.product,
                    ))
        return res

    @fields.depends('bom')
    def on_change_with_drawing(self):
        return self.bom.drawing.id if self.bom and self.bom.drawing else None

    @fields.depends('drawing')
    def on_change_with_drawing_image(self, name=None):
        return self.drawing.image if self.drawing else None

    @classmethod
    def compute_request(cls, product, warehouse, quantity, date, company,
            order_point=None):
        Line = Pool().get('production.drawing.line')
        production = super(Production, cls).compute_request(product, warehouse,
            quantity, date, company, order_point)
        drawing_lines = []
        if production.bom and production.bom.drawing:
            production.drawing = production.bom.drawing
            for line in production.bom.drawing_lines:
                drawing_lines.append(Line(
                        position=line.position,
                        product=line.product,
                        ))
        production.drawing_lines = drawing_lines
        return production


class ProductionDrawingLine(ModelSQL, ModelView):
    'Production Drawing Line'
    __name__ = 'production.drawing.line'
    production = fields.Many2One('production', 'Production', required=True,
        ondelete='CASCADE')
    position = fields.Many2One('production.drawing.position',
        'Drawing Position', required=True, ondelete='RESTRICT', states={
            'readonly': True,
            })
    product = fields.Many2One('product.product', 'Product')
    lot = fields.Many2One('stock.lot', 'Lot', ondelete='RESTRICT', domain=[
            ('product', '=', Eval('product', -1)),
            ('id', 'in', Eval('valid_lots', [])),
            ])
    valid_lots = fields.Function(fields.Many2Many('stock.lot', None,
                'Product'), 'get_valid_lots')

    @classmethod
    def __setup__(cls):
        super(ProductionDrawingLine, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('check_bom_drawing_position_uniq', Unique(t, t.production,
                t.position),
                'Drawing Position must be unique per BOM.'),
            ]

    def get_valid_lots(self, name):
        return [x.lot.id for x in self.production.inputs if x.lot]
