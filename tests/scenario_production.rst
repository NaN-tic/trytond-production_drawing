===================
Production Scenario
===================

=============
General Setup
=============

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> today = datetime.date.today()
    >>> yesterday = today - relativedelta(days=1)
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company

Install product_cost_plan Module::

    >>> config = activate_modules('production_drawing')


Create company::

    >>> _ = create_company()
    >>> company = get_company()
    >>> tax_identifier = company.party.identifiers.new()
    >>> tax_identifier.type = 'eu_vat'
    >>> tax_identifier.code = 'BE0897290877'
    >>> company.party.save()

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.producible = True
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal(30)
    >>> template.save()
    >>> product.template = template
    >>> product.cost_price = Decimal(20)
    >>> product.save()

Create Components::

    >>> component1 = Product()
    >>> template1 = ProductTemplate()
    >>> template1.name = 'component 1'
    >>> template1.default_uom = unit
    >>> template1.type = 'goods'
    >>> template1.list_price = Decimal(5)
    >>> template1.cost_price = Decimal(1)
    >>> template1.save()
    >>> component1.template = template1
    >>> component1.save()

    >>> meter, = ProductUom.find([('symbol', '=', 'm')])
    >>> centimeter, = ProductUom.find([('symbol', '=', 'cm')])
    >>> component2 = Product()
    >>> template2 = ProductTemplate()
    >>> template2.name = 'component 2'
    >>> template2.default_uom = meter
    >>> template2.type = 'goods'
    >>> template2.list_price = Decimal(7)
    >>> template2.cost_price = Decimal(5)
    >>> template2.save()
    >>> component2.template = template2
    >>> component2.save()

Create Drawing::

    >>> Drawing = Model.get('production.drawing')
    >>> drawing = Drawing()
    >>> drawing.name = 'Drawing'
    >>> pos1 = drawing.positions.new()
    >>> pos1.name = 'R1'
    >>> pos2 = drawing.positions.new()
    >>> pos2.name = 'R2'
    >>> drawing.save()

Create Bill of Material::

    >>> BOM = Model.get('production.bom')
    >>> BOMInput = Model.get('production.bom.input')
    >>> BOMOutput = Model.get('production.bom.output')
    >>> bom = BOM(name='product')
    >>> input1 = BOMInput()
    >>> bom.inputs.append(input1)
    >>> input1.product = component1
    >>> input1.quantity = 5
    >>> input2 = BOMInput()
    >>> bom.inputs.append(input2)
    >>> input2.product = component2
    >>> input2.quantity = 150
    >>> input2.unit = centimeter
    >>> output = BOMOutput()
    >>> bom.outputs.append(output)
    >>> output.product = product
    >>> output.quantity = 1
    >>> bom.drawing = drawing
    >>> names = [str(x.position.name) for x in bom.drawing_lines]
    >>> sorted(names)
    ['R1', 'R2']
