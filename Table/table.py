from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, TableColumn, DataTable
from bokeh.io import show
import pandas as pd

df = pd.DataFrame({
    'SubjectID': ['Subject_01','Subject_02','Subject_03'],
    'Result_1': ['Positive','Negative','Negative'],
    'Result_2': ['Negative','Negative','Negative'],
    'Result_3': ['Negative','Invalid','Positive'],
    'Result_4': ['Positive','Negative','Negative'],
    'Result_5': ['Positive','Positive','Negative']
})
  
source = ColumnDataSource(df)

from bokeh.models import HTMLTemplateFormatter

def get_html_formatter(my_col):
    template = """
        <div style="background:<%= 
            (function colorfromint(){
                if(result_col == 'Positive'){
                    return('white')}
                else if (result_col == 'Negative')
                    {return('white')}
                else if (result_col == 'Invalid')
                    {return('white')}
                }()) %>; 
            color: black"> 
        <%= value %>
        </div>
    """.replace('result_col',my_col)
    
    return HTMLTemplateFormatter(template=template)

columns = [
    TableColumn(field='SubjectID', title='SubjectID'),
    TableColumn(field='Result_1', title='Result 1', formatter=get_html_formatter('Result_1')),
    TableColumn(field='Result_2', title='Result 2', formatter=get_html_formatter('Result_2')),
    TableColumn(field='Result_3', title='Result 3', formatter=get_html_formatter('Result_3')),
    TableColumn(field='Result_4', title='Result 4', formatter=get_html_formatter('Result_4')),
    TableColumn(field='Result_5', title='Result 5', formatter=get_html_formatter('Result_5'))
    ]

myTable = DataTable(source=source, columns=columns)

show(myTable)