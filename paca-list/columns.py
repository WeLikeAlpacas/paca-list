# encoding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text


class BaseColumn(object):

    def __init__(self, name, label):
        self.name = name
        self.label = label

    def get_values(self, obj):
        # Check if field has choices
        value = getattr(obj, 'get_%s_display' % self.name, lambda: None)()
        if not value:
            value = getattr(obj, self.name, '')
        return {'value': value}

    def render(self, obj):
        values = dict((key, value.encode('utf-8'))
                      for (key, value)
                      in self.get_values(obj).iteritems())
        return self.template.format(**values)


class DefaultColumn(BaseColumn):
    template = """{value}"""


class ForeignKeyColumn(DefaultColumn):
    def __init__(self, *args, **kwargs):
        self.related_model = kwargs.pop('related_model')
        super(ForeignKeyColumn, self).__init__(*args, **kwargs)

    def get_values(self, obj):
        related_object = getattr(obj, self.related_model)
        return {'value': getattr(related_object, self.name, '')}


class UlColumn(BaseColumn):
    template = """
    <ul class="list-unstyled">
        {value}
    </ul>
    """

    def __init__(self, *args, **kwargs):
        self.value_field = kwargs.pop('value_field')
        super(UlColumn, self).__init__(*args, **kwargs)

    def get_values(self, obj):
        output = []
        value = getattr(obj, self.name, [])
        for v in value.all():
            output.append("<li>{0}</li>".format(getattr(v, self.value_field, '')))

        return {'value': ''.join(output)}


class TitleUlColumn(UlColumn):

    def __init__(self, *args, **kwargs):
        self.title_field = kwargs.pop('title_field')
        self.order = kwargs.pop('order', '')
        super(TitleUlColumn, self).__init__(*args, **kwargs)

    def get_values(self, obj):
        output = []
        value = getattr(obj, self.name, [])
        title = None
        for v in value.order_by("{0}{1}".format(self.order, self.title_field)):
            if not title or title != getattr(v, self.title_field):
                output.append("<strong>{0}</strong>".format(getattr(v, self.title_field).capitalize()))
                title = getattr(v, self.title_field)

            output.append("<li>{0}</li>".format(v))

        return {'value': ''.join(output)}


class BooleanColumn(DefaultColumn):
    template = """{value} {extra_value}"""
    extra_template = """<br /><span class="text-muted"><em>{value}</em></span>"""

    def __init__(self, *args, **kwargs):
        self.extra_name = kwargs.pop('extra_name', None)
        self.extra_label = kwargs.pop('extra_label', None)
        super(BooleanColumn, self).__init__(*args, **kwargs)

    def get_values(self, obj):
        extra_value = ''
        value = force_text([_(u'No'), _(u'Yes')][getattr(obj, self.name, '')])
        if getattr(obj, self.extra_name):
            extra_value = self.extra_template.format(value=unicode(self.extra_label))

        return {'value': value, 'extra_value': extra_value}
