''' Interactive filtering of screened CURATED COFs.
'''
import datetime
import glob,os
from os.path import dirname, join

import pandas as pd
from scipy.signal import savgol_filter

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select, HoverTool, Span, DataTable, TableColumn, NumberFormatter, TextInput, Div, CustomJS, Button
from bokeh.plotting import figure

#reading COFs results
cofs = pd.read_csv(join(dirname(__file__), "all_oldnew_conv.csv"))

cofs = cofs.drop(['pk', 'homo_energy', 'lumo_energy', 'path',
       'potential', 'var', 'homo_align', 'lumo_align', 'direct_band_gap_energy',
       'vbm', 'cbm', 'cellopt_retrieved', 'spatial_overlap','Unnamed: 0'],axis=1)

#possible redox reactions energies
HER = -4.4 #https://www.mdpi.com/2073-4344/10/8/836,https://arxiv.org/pdf/1909.00979.pdf,https://doi.org/10.1002/adts.201800146 what about at pH 7?
OER = -5.629
CO2_CH4 = -3.79 #https://doi.org/10.1039/C5TA06982C,https://pubs.acs.org/doi/10.1021/jp300590d
CO2_CH3OH = -3.65
CO2_HCOOH = -3.42
VIS_E = 3.2
N2_NH3 = -4.3 #4.2-4.3,https://doi.org/10.1021/acscentsci.0c00552
TEOA = -5.47
TEA = -5.34

def get_dataset(src, ox, red, bgr, mer, mhr, ovlpr):
    filt_redox = src[(src['bandgap_corr']<bgr)&(src['homo_align_corr']<ox)\
                         &(src['lumo_align_corr']>red)]
    filt_m = filt_redox[(filt_redox['effective_mass_electron']<mer)&(filt_redox['effective_mass_hole']<mhr)]
    filt_final = filt_m[(filt_m['spatial_overlap_corr']<ovlpr)]
    exc = cofs[~(cofs['label'].isin(filt_final['label']))].reset_index(drop=True)
    return ColumnDataSource(data=filt_final),ColumnDataSource(data=exc)

def make_plot(source, exc, ox, red, bgr, title):

    desc = source.data['label']
    descexc = exc.data['label']
    homo = ColumnDataSource(data=dict(x=source.data['bandgap_corr'], y=source.data['homo_align_corr'], desc=desc))
    lumo = ColumnDataSource(data=dict(x=source.data['bandgap_corr'], y=source.data['lumo_align_corr'], desc=desc))
    homo_exc = ColumnDataSource(data=dict(x=exc.data['bandgap_corr'], y=exc.data['homo_align_corr'], desc=descexc))
    lumo_exc = ColumnDataSource(data=dict(x=exc.data['bandgap_corr'], y=exc.data['lumo_align_corr'], desc=descexc))
    hover = HoverTool(tooltips=[
        ("index", "$index"),
        ("(x,y)", "(@x,@y)"),
        ('desc', '@desc'),
    ])
    p = figure(plot_width=800, plot_height=400, tools=[hover], x_axis_label='Adjusted Band Gap [eV]', y_axis_label='Adjusted IP/EA energies [eV]', title=title)
    p.circle('x','y', size=10, source=homo, color='red')
    p.circle('x','y', size=10, source=lumo, color='blue')
    p.circle('x','y', size=10, source=homo_exc, color='red',alpha=0.05)
    p.circle('x','y', size=10, source=lumo_exc, color='blue',alpha=0.05)
    redline = Span(location=ox,dimension='width',line_color='green',line_dash='dashed',line_width=2)
    oxline = Span(location=red,dimension='width',line_color='purple',line_dash='dashed',line_width=2)
    bgrline = Span(location=bgrs[bgr],dimension='height',line_color='black',line_dash='dashed',line_width=2)

    p.add_layout(redline)
    p.add_layout(oxline)
    p.add_layout(bgrline)

    return p

def update_plot(attrname, old, new):
    ox = ox_select.value
    red = red_select.value
    bgr = bgr_select.value
    mer = mer_select.value
    mhr = mhr_select.value
    ovlpr = ovlpr_select.value

    if ox == 'Type a value':
        ox_input.visible = True
    else:
        ox_input.visible = False
        oxname = ox
    if red == 'Type a value':
        red_input.visible = True
    else:
        red_input.visible = False
        redname = red
    if bgr == 'Type a value':
        bgr_input.visible = True
    else:
        bgr_input.visible = False
    if mer == 'Type a value':
        mer_input.visible = True
    else:
        mer_input.visible = False
    if mhr == 'Type a value':
        mhr_input.visible = True
    else:
        mhr_input.visible = False
    if ovlpr == 'Type a value':
        ovlpr_input.visible = True
    else:
        ovlpr_input.visible = False

    if ox_input.value and ox == 'Type a value':
        oxval = float(ox_input.value.strip())
        oxname = str(oxval)
    else:
        oxval = oxs[ox]
        oxname = ox
    if red_input.value and red == 'Type a value':
        redval = float(red_input.value.strip())
        redname = str(redval)
    else:
        redval = reds[red]
        redname = red
    
    if bgr_input.value and bgr == 'Type a value':
        bgrval = float(bgr_input.value.strip())
    else:
        bgrval = bgrs[bgr]
    if mer_input.value and mer == 'Type a value':
        merval = float(mer_input.value.strip())
    else:
        merval = mers[mer]
    if mhr_input.value and mhr == 'Type a value':
        mhrval = float(mhr_input.value.strip())
    else:
        mhrval = mhrs[mhr]
    if ovlpr_input.value and ovlpr == 'Type a value':
        ovlprval = float(ovlpr_input.value.strip())
    else:
        ovlprval = ovlprs[ovlpr]
    
    src,exc = get_dataset(cofs, oxval, redval, bgrval, merval, mhrval, ovlprval)
    source.data.update(src.data)

    title = "Filtered CURATED COFs for photocatalytic " + redname + "/" + oxname
    layout.children[0].children[1] = make_plot(source, exc, oxval, redval, bgr, title) 
    

ox = 'Oxygen evolution reaction'
red = 'Hydrogen evolution reaction'
bgr = 'Visible light'
mer = '10'
mhr = '10'
ovlpr = '0.50'

oxs = {
    'Oxygen evolution reaction': OER,
    'Triethanolamine as sacrificial donor': TEOA,
    'Triethylamine as sacrificial donor': TEA,
    'Type a value': 0
}

reds = {
    'Hydrogen evolution reaction': HER,
    'Nitrogen reduction to amine': N2_NH3,
    'CO2 reduction to methane': CO2_CH4,
    'CO2 reduction to methanol': CO2_CH3OH,
    'CO2 reduction to formic acid': CO2_HCOOH,
    'Type a value': 0
}

bgrs = {
    'Visible light': VIS_E,
    'Type a value': 0
}

mers = {
    '1': 1,
    '10': 10,
    '50': 50,
    '100': 100,
    'Type a value': 0
}

mhrs = {
    '1': 1,
    '10': 10,
    '50': 50,
    '100': 100,
    'Type a value': 0
}

ovlprs = {
    '0.25': 0.25,
    '0.50': 0.50,
    '0.75': 0.75,
    '1.00': 1.00,
    'Type a value': 0
}


ox_select = Select(value=ox, title='Oxidation reaction energy w.r.t. vacuum [eV] (1)', options=sorted(oxs.keys()))
red_select = Select(value=red, title='Reduction reaction energy w.r.t. vacuum [eV] (1)', options=sorted(reds.keys()))
bgr_select = Select(value=bgr, title='Band gap upper limit [eV]', options=sorted(bgrs.keys()))
mer_select = Select(value=mer, title="Effective mass electron [m/me]", options=sorted(mers.keys()))
mhr_select = Select(value=mhr, title="Effective mass hole [m/me]", options=sorted(mhrs.keys()))
ovlpr_select = Select(value=ovlpr, title="Charge recombination descriptor [0-1]", options=sorted(ovlprs.keys()))

ox_input = TextInput(visible=False)
red_input = TextInput(visible=False)
bgr_input = TextInput(visible=False)
mer_input = TextInput(visible=False)
mhr_input = TextInput(visible=False)
ovlpr_input = TextInput(visible=False)

source,exc = get_dataset(cofs, oxs[ox], reds[red], bgrs[bgr], mers[mer], mhrs[mhr], ovlprs[ovlpr])
title = "Filtered CURATED COFs for photocatalytic " + red + "/" + ox

columns = [
    TableColumn(field='label',title='CURATED COF ID'),
    TableColumn(field='bandgap_corr', title='Adjusted Band Gap [eV]', formatter=NumberFormatter(format="0.00")),
    TableColumn(field='effective_mass_electron',title='m* electron [m/me]', formatter=NumberFormatter(format="0.00")),
    TableColumn(field='effective_mass_hole',title='m* hole [m/me]', formatter=NumberFormatter(format="0.00")),
    TableColumn(field='spatial_overlap_corr',title='Charge recomb. descript.', formatter=NumberFormatter(format="0.00")),
]
data_table = DataTable(source=source, columns=columns, width=800)

text = Div(text="""Values displayed here are to be considered with caution. Please keep in mind that this is a screening approach, therefore further theoretical and experimental studies are encouraged. (1) The redox potentials are approximate, please refer to the following references for specifications on pH and medium. References: <a href="https://doi.org/10.1002/adts.201800146">HER/OER</a>, <a href="https://doi.org/10.1039/C5TA06982C">CO2RR</a>, <a href="https://doi.org/10.1021/acscentsci.0c00552">NRR</a>, <a href="https://doi.org/10.1016/j.crci.2015.11.026">Sacrificial agents</a>, <a href="https://doi.org/10.1021/ja073946i">Vacuum</a>. You can find the names and original articles for each COF in the <a href="https://www.materialscloud.org/discover/curated-cofs#mcloudHeader">CURATED COFs</a>.""", #change link to original work
width=250, height=200)

button = Button(label="Download",width=250)
button.js_on_event("button_click", CustomJS(args=dict(source=source),
                            code=open(join(dirname(__file__), "download.js")).read()))

for w in [ox_select,ox_input,red_select,red_input,bgr_select,bgr_input,mer_select,mer_input,mhr_select,mhr_input,ovlpr_select,ovlpr_input]:
    w.on_change('value',update_plot)

controls = column(ox_select,ox_input,red_select,red_input,bgr_select,bgr_input,mer_select,mer_input,mhr_select,mhr_input,ovlpr_select,ovlpr_input)

layout = column(row(controls,make_plot(source, exc, oxs[ox], reds[red], bgr, title)),row(data_table,column(text,button)))
curdoc().add_root(layout)
curdoc().title = "COFs for photocatalysis"
