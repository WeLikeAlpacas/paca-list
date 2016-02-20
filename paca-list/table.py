# encoding: utf-8
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.safestring import mark_safe
from django.template import Template, RequestContext


paca_table_template = """
<div class="table-responsive">
    <table class="{classes}">
      <thead>
      {list_headers}
      </thead>
      <tbody>
      {list_rows}
      </tbody>
    </table>
    {{% include 'partials/pagination_table.html' %}}
</div>
"""


@python_2_unicode_compatible
class PacaTable(object):
    template = paca_table_template
    table_header_template = "<th>{header}</th>"
    row_template = "<tr>{list_columns}</tr>"
    column_template = "<td>{column_value}</td>"
    tools_column_template = """
      <td class="text-right table-icons-column">
        {actions}
      </td>
    """
    tools_edit_template = """
      <a data-no-pjax
         href="{url}"
         {disabled}
         title="{title} Edit">
          <span class="fa fa-pencil"></span>
      </a>
    """
    tools_delete_template = """
      <a data-no-pjax
         href="{url}"
         title="{title} Delete"
         data-modal-delete="#modal-delete"
         {disabled}
         data-modal-name="">
          <span class="fa fa-trash-o"></span>
      </a>
    """

    def __init__(self, title, fields, edit_url, delete_url, objects=None):
        self.title = title
        self.fields = fields
        self.edit_url = edit_url
        self.delete_url = delete_url
        self.objects = objects
        self.classes = ['table', 'table-hover']

    def get_css_classes(self):
        return " ".join(self.classes)

    def print_header(self, field=None):
        if not field:
            return self.table_header_template.format(header="")
        return self.table_header_template.format(header=force_text(field.label))

    def print_headers(self):
        output = []
        for field in self.fields:
            output.append(self.print_header(field))

        # Add header for tools column
        output.append(self.print_header())
        return ''.join(output)

    def print_tools_column(self, obj):
        actions = []
        delete_kwargs = {'url': '#', 'disabled': 'disabled', 'title': self.title}
        edit_kwargs = {'url': '#', 'disabled': 'disabled', 'title': self.title}
        if getattr(obj, 'can_be_edited', lambda x, context: True)(self.request, context=self.context):
            edit_kwargs.update({'url': self.edit_url([obj.id]), 'disabled': ''})
        if getattr(obj, 'can_be_deleted', lambda x, context: True)(self.request, context=self.context):
            delete_kwargs.update({'url': self.delete_url([obj.id]), 'disabled': ''})

        actions.append(self.tools_edit_template.format(**edit_kwargs))
        actions.append(self.tools_delete_template.format(**delete_kwargs))

        return self.tools_column_template.format(actions=''.join(actions))

    def print_column(self, field, obj):
        return self.column_template.format(column_value=field.render(obj))

    def print_columns(self, obj):
        output = []
        for field in self.fields:
            output.append(self.print_column(field, obj))

        output.append(self.print_tools_column(obj))
        return ''.join(output)

    def print_row(self, obj):
        return self.row_template.format(list_columns=self.print_columns(obj))

    def print_rows(self):
        output = []
        for obj in self.objects:
            output.append(self.print_row(obj))

        return ''.join(output)

    def render(self, **kwargs):
        list_headers = self.print_headers()
        list_rows = self.print_rows()
        classes = self.get_css_classes()
        template = Template(self.template.format(list_headers=list_headers, list_rows=list_rows,
                                                 classes=classes, **kwargs))
        return mark_safe(template.render(RequestContext(self.request, self.context)))

    def prepare(self, objects, request, context={}):
        self.objects = objects
        self.request = request
        self.context = context

    def __str__(self):
        return self.render()
