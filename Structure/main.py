# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object, too-many-locals, redefined-outer-name
from __future__ import print_function
from __future__ import absolute_import
from os.path import dirname, join
import os
import pandas as pd
import subprocess

from bokeh.layouts import layout, column, row, widgetbox 
import bokeh.models as bmd
from bokeh.io import curdoc
from jsmol_bokeh_extension import JSMol
from bokeh.models import ColumnDataSource, TextInput
from bokeh.models.widgets import DataTable, TableColumn, HTMLTemplateFormatter, StringFormatter, PreText, Button

html = bmd.Div(text=open(join(dirname(__file__), 'description.html')).read(),
               width=800)

download_js = open(join(dirname(__file__), 'static', 'download.js')).read()

script_source = bmd.ColumnDataSource()

plot_info = PreText(text='', width=300, height=100)

btn_download_table = Button(label='Download json', button_type='primary')
btn_download_cif = Button(label='Download cif', button_type='primary')

def get_name_from_url():
    """Get structure name from URL parameter."""
    args = curdoc().session_context.request.arguments
    print(args)
    try:
        name = args.get('name')[0]
        if isinstance(name, bytes):
            name = name.decode()
    except (TypeError, KeyError):
        name = 'RSM0011'

    return name

def table_widget(name):  # disable=redefined-outer-name
    """Create table widget."""


    FILE = './data/datatable.csv'
    print(os.listdir())
    df = pd.read_csv(FILE)
    entry = df.loc[df['Label'] == name]

    data = {}    
    for i in list(entry.columns):
        data.update({i: entry[i].values[0]})

    data = dict(
        labels = list(data.keys()),
        values = list(data.values())
    )
    source = ColumnDataSource(data)

    columns = [
        TableColumn(field='labels', title='Property', formatter=StringFormatter(text_align="center")),
        TableColumn(field='values', title='Value', formatter=HTMLTemplateFormatter())
    ]
    
    data_table = DataTable(source=source,
                           columns=columns,
                           width=500,
                           height=500,
                           index_position=None,
                           fit_columns=True)



    return widgetbox(data_table)

def get_cif_content_from_disk(filename):
    """ Load CIF content from disk """
    with open(filename, 'r') as f:
        content = f.read()
    return content

structure_name = get_name_from_url()

ciffile = f'{structure_name}.cif'
ciffile =  os.path.join('./data/CIFs', ciffile)
if os.path.exists(ciffile):
    print(f'{ciffile} found!')

cifcontent = get_cif_content_from_disk(ciffile)

info = dict(
        height='100%',
        width='100%',
        serverURL='https://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php',
        use='HTML5',
        j2sPath='https://chemapps.stolaf.edu/jmol/jsmol/j2s',
        script="""
set antialiasDisplay ON; background white; set displayCellParameters FALSE; set disablePopupMenu FALSE;
load data "cifstring"
{}
end "cifstring"
    """.format(cifcontent)
    )

applet = JSMol(
    width=500,
    height=500,
    script_source=script_source,
    info=info,
    #js_url='detail/static/jsmol/JSmol.min.js',
)

def extend_structure(enxtension = [1,1,1]):
    global ciffile
    print(x_input.value)
    for i, ax in enumerate([x_input.value, y_input.value, z_input.value]):
        try:
            new = int(ax)
            enxtension[i] = new
        except:
            pass

    TEMP = 'temp_cif.cif'
    print('running subprocess')
    command = ['manage_crystal', 
                    ciffile, 
                    f'-x {enxtension[0]}',
                    f'-y {enxtension[1]}',
                    f'-z {enxtension[2]}',
                    f'-o{TEMP}']
    print(command)
    subprocess.run(command)

    
    with open(f'./{TEMP}', 'r+') as f:
        extended_content = f.read()
    
    os.remove(TEMP)

    info_new = dict(
        height='100%',
        width='100%',
        serverURL='https://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php',
        use='HTML5',
        j2sPath='https://chemapps.stolaf.edu/jmol/jsmol/j2s',
        script="""
set antialiasDisplay ON; background white; set displayCellParameters FALSE; set disablePopupMenu FALSE;
load data "cifstring"
{}
end "cifstring"
    """.format(extended_content)
    )

    applet_new = JSMol(
        width=500,
        height=500,
        script_source=script_source,
        info=info_new,
        #js_url='detail/static/jsmol/JSmol.min.js',
    )

    ly.children[0].children[0]= applet_new

    return applet


duplicate_btm = bmd.Button(label = 'Enlarge Structure')
duplicate_btm.on_click(extend_structure)





# Create a text input field with an initial value of 'Default Text' and apply the callback
x_input = TextInput(value='', title='x:', width = 40)
y_input = TextInput(value='', title='y:', width = 40)
z_input = TextInput(value='', title='z:', width = 40)

ly = row(
        column(
    applet, 
    #btn_download_cif, 
    row(
        x_input, 
        y_input, 
        z_input
        ), 
    duplicate_btm
    ),
        bmd.Spacer(width = 50),
        column(
            table_widget(structure_name), 
            #btn_download_table
            )
)

# We add this as a tab
tab = bmd.Panel(child=ly, title=structure_name)
tabs = bmd.widgets.Tabs(tabs=[tab])

# Put the tabs in the current document for display
curdoc().title = 'Structure'
curdoc().add_root(layout([html, tabs]))