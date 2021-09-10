from trytond.model import ModelSQL, ModelView, DeactivableMixin, fields

__all__ = ['Drawing', 'DrawingPosition']


class Drawing(DeactivableMixin, ModelSQL, ModelView):
    'Production Drawing'
    __name__ = 'production.drawing'
    name = fields.Char('Name', required=True)
    image = fields.Binary('Image')
    positions = fields.One2Many('production.drawing.position', 'drawing',
        'Positions')


class DrawingPosition(ModelSQL, ModelView):
    'Production Drawing Position'
    __name__ = 'production.drawing.position'
    drawing = fields.Many2One('production.drawing', 'Drawing',
        required=True, ondelete='CASCADE')
    name = fields.Char('Name', required=True)
