''' User input script '''

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Spacer, FileInput, ColumnDataSource, Select, TextInput, TextAreaInput, DataTable, TableColumn, TextInput, CustomJS, Button
from config_upl import *
from os.path import dirname, join

## All input data needed
firstname_input = TextInput(value="", title="First Name", width=WWIDTH)
lastname_input = TextInput(value="", title="Last Name", width=WWIDTH)
email_input = TextInput(value="", title="Email Address", width=WWIDTH)
affiliation_input = TextInput(value="", title="Affiliation", width=WWIDTH)
position_input = TextInput(value="", title="Position", width=WWIDTH)
structurename_input = TextInput(value="", title="Structure Label", width=WWIDTH)
structureDOI_input = TextInput(value="", title="Structure DOI", width=WWIDTH)
remarks_area_input = TextAreaInput(value="", rows=6, title="Remarks", width=WWIDTH)
# Type drop down
list_types = ["Experimental", "Hypothetical"]
consent_labels = ["", "I Agree"]
type_select = Select(title='Structure Type', options=list({i:i for i in list_types}.keys()), value=list_types[0], width=WWIDTH)
consent_select = Select(title='User Consent', options=list({i:i for i in consent_labels}.keys()), value=consent_labels[0], width=WWIDTH)
# cif file
cif_input = FileInput(accept=".cif", width=WWIDTH)

## Updates
# Single Line Input
firstname_input.js_on_change("value", CustomJS(code="""
    console.log('text_input: value=' + this.value, this.toString())
"""))
lastname_input.js_on_change("value", CustomJS(code="""
    console.log('text_input: value=' + this.value, this.toString())
"""))
email_input.js_on_change("value", CustomJS(code="""
    console.log('text_input: value=' + this.value, this.toString())
"""))
affiliation_input.js_on_change("value", CustomJS(code="""
    console.log('text_input: value=' + this.value, this.toString())
"""))
position_input.js_on_change("value", CustomJS(code="""
    console.log('text_input: value=' + this.value, this.toString())
"""))
structurename_input.js_on_change("value", CustomJS(code="""
    console.log('text_input: value=' + this.value, this.toString())
"""))
structureDOI_input.js_on_change("value", CustomJS(code="""
    console.log('text_input: value=' + this.value, this.toString())
"""))

# Multiple Lines Input
remarks_area_input.js_on_change("value", CustomJS(code="""
    console.log('text_area_input: value=' + this.value, this.toString())
"""))

## Save button
submitbutton = Button(label="Submit", button_type="success", width=WWIDTH)

## Make a table
table_data = ColumnDataSource(data={"First":[firstname_input.value], "Last":[lastname_input.value],
                                    "Email":[email_input.value], "Affiliation":[affiliation_input.value],
                                    "Position":[position_input.value], "Label":[structurename_input.value],
                                    "DOI":[structureDOI_input.value], "Type":[type_select.value],
                                    "Remarks":[remarks_area_input.value], "Consent":[consent_select.value],
                                    "Cifdata":[cif_input.value]})

columns = [TableColumn(field='First',title='First'),
           TableColumn(field='Last',title='Last'),
           TableColumn(field='Email',title='Email'),
           TableColumn(field='Affiliation',title='Affiliation'),
           TableColumn(field='Position',title='Position'),
           TableColumn(field='Label',title='Label'),
           TableColumn(field='DOI',title='DOI'),
           TableColumn(field='Type',title='Type'),
           TableColumn(field='Remarks',title='Remarks'),
           TableColumn(field='Consent',title="Consent"),
           TableColumn(field='Cifdata', title='Cifdata')]

table = DataTable(source=table_data, columns=columns, width=250,
                  index_position=None, sortable=False, selectable=False)

def update_table(attrname, old, new):  
    first_val = {"First":[firstname_input.value.strip()]}
    last_val = {"Last":[lastname_input.value.strip()]}
    email_val = {"Email":[email_input.value.strip()]}
    affiliation_val = {"Affiliation":[affiliation_input.value.strip()]}
    posistion_val = {"Position":[position_input.value.strip()]}
    label_val = {"Label":[structurename_input.value.strip()]}
    DOI_val = {"DOI":[structureDOI_input.value.strip()]}
    type_val = {"Type":[type_select.value]}
    remarks_val = {"Remarks":[remarks_area_input.value.strip()]}
    consent_val = {"Consent":[consent_select.value]}
    cifdata_val = {"Cifdata":[cif_input.value]}

    table_data.data.update(first_val)
    table_data.data.update(last_val)
    table_data.data.update(email_val)
    table_data.data.update(affiliation_val)
    table_data.data.update(posistion_val)
    table_data.data.update(label_val)
    table_data.data.update(DOI_val)
    table_data.data.update(type_val)
    table_data.data.update(remarks_val)
    table_data.data.update(consent_val)
    table_data.data.update(cifdata_val)

firstname_input.on_change('value', update_table)
lastname_input.on_change('value', update_table)
email_input.on_change('value', update_table)
affiliation_input.on_change('value', update_table)
position_input.on_change('value', update_table)
structurename_input.on_change('value', update_table)
structureDOI_input.on_change('value', update_table)
type_select.on_change('value', update_table)
remarks_area_input.on_change('value', update_table)
consent_select.on_change('value', update_table)
cif_input.on_change('value', update_table)
submitbutton.js_on_click(CustomJS(args=dict(source=table_data),
                            code=open(join(dirname(__file__), "static/js/download_csv.js")).read()))

## Generate the page
layout = column(row(column(firstname_input, affiliation_input, structurename_input, type_select, email_input, remarks_area_input), column(lastname_input, position_input, structureDOI_input, consent_select, Spacer(margin=(0,0,18,0)), cif_input)), row(submitbutton))
curdoc().add_root(layout)
curdoc().title = "Upload"