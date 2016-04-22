import bokeh.plotting as bk
from bokeh.plotting import figure
from bokeh.models import HoverTool
from bokeh.io import show
from bokeh.models.widgets import Panel, Tabs
from bokeh.embed import file_html
from bokeh.resources import JSResources, CSSResources
import pandas as pd
from jinja2 import Template
from ..helpers.regexes import *

import datetime
import collections
import os

bk.output_notebook()
colors = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17bec"]

"""
Created by:
Patrick Brockmann - LSCE
2015/10/11

Additions by:
Christopher Heiser - NAU LiPD
2016/04/21
"""


def _dotnotation_for_nested_dictionary(d, key, dots):
    """
    Flattens nested data structures using dot notation.
    :param d:
    :param key:
    :param dots:
    :return:
    """
    if key == 'chronData':
        # Not interested in expanding chronData. Keep it as a chunk.
        dots[key] = d
    elif isinstance(d, dict):

        for k in d:
            _dotnotation_for_nested_dictionary(d[k], key + '.' + k if key else k, dots)
    elif isinstance(d, list) and \
            not all(isinstance(item, (int, float, complex, list)) for item in d):
        for n, d in enumerate(d):
            _dotnotation_for_nested_dictionary(d, key + '.' + str(n) if key != "" else key, dots)
    else:
        dots[key] = d

    return dots


def LiPD_to_df(dict_in):
    """
    Create a pandas dataframe using LiPD metadata and CSV data
    :param dict dict_in: LiPD metadata dictionary
    :return obj: Metadata DF, CSV DF
    """
    dict_in_dotted = {}
    _dotnotation_for_nested_dictionary(dict_in, '', dict_in_dotted)
    dict_in_dotted = collections.OrderedDict(sorted(dict_in_dotted.items()))
    df_meta = pd.DataFrame(list(dict_in_dotted.items()), columns=["Key", "Value"])
    df_data = pd.DataFrame(_get_lipd_cols(dict_in))

    return df_meta, df_data


def TS_to_df(dict_in):
    """
    Create a data frame from one TimeSeries object
    :param dict dict_in: Time Series dictionary
    :return obj: 3 Data Frame objects
    """
    s = collections.OrderedDict(sorted(dict_in.items()))
    # Put key-vars in a data frame to make it easier to visualize
    df_meta = pd.DataFrame(list(s.items()), columns=['Key', 'Value'])
    # Plot the variable + values vs year, age, depth (whichever are available)
    df_data = pd.DataFrame(_get_ts_cols(dict_in))
    # Plot the chronology variables + values in a data frame
    try:
        df_chron = dict_in["chronData_df"]
    except KeyError:
        df_chron = "Chronology not available"

    return df_meta, df_data, df_chron


def _get_ts_cols(dict_in):
    """
    Get variable + values vs year, age, depth (whichever are available)
    :param dict dict_in: TimeSeries dictionary
    :return dict: Key: variableName, Value: Panda Series object
    """
    d = {}
    try:
        # Get the main column data first
        units = " (" + dict_in["paleoData_units"] + ")"
    except KeyError:
        units = ""
    try:
        d[dict_in["paleoData_variableName"] + units] = dict_in["paleoData_values"]
    except KeyError:
        pass

    # Start looking for the additional special columns
    for k, v in dict_in.items():
        if re_pandas_x_num.match(k):
            try:
                units = " (" + dict_in[k + "Units"] + ")"
            except KeyError:
                units = ""
            d[k + units] = v

    return d


def _get_lipd_cols(dict_in):
    """
    Grab the variableName and values data from each paleoData table in the LiPD metadata
    :param dict dict_in: LiPD metadata dictionary
    :return dict: Dictionary of { variableName: [valuesArray] }
    """
    d = {}
    try:
        # TODO: make sure this accounts for multiple tables
        for table, table_data in dict_in['paleoData'].items():
            for var, arr in table_data["columns"].items():
                d[var] = pd.Series(arr["values"])
    except KeyError:
        pass

    return d


def _get_chron_cols(dict_in):
    """

    :param dict_in:
    :return:
    """
    return


def PDS_to_LiPD(PDS_inputfile, verbose=True):
    """

    :param PDS_inputfile:
    :param verbose:
    :return:
    """
    dfD, dfM = PDS_to_df(PDS_inputfile)
    dict_out = df_to_LiPD(dfD, dfM, verbose=verbose)

    return dict_out


def LiPD_to_PDS(dict_in, PDS_outputfile):
    """

    :param dict_in:
    :param PDS_outputfile:
    :return:
    """
    dfD, dfM = LiPD_to_df(dict_in)
    df_to_PDS(dfD, dfM, PDS_outputfile)
    return


def df_plot(dfD, xCol, yCols, width=600, height=600):
    """

    :param dfD:
    :param xCol:
    :param yCols:
    :param width:
    :param height:
    :return:
    """
    hover1 = HoverTool(tooltips=[("x,y", "(@x, @y)")])
    tools1 = ["pan,resize,box_zoom,wheel_zoom,crosshair",hover1,"reset,save"]
    hover2 = HoverTool(tooltips=[("x,y", "(@x, @y)")])
    tools2 = ["pan,resize,box_zoom,wheel_zoom,crosshair",hover2,"reset,save"]

    plot1 = figure(width=width, height=height, tools=tools1)
    plot2 = figure(width=width, height=height, tools=tools2,
                   x_range=plot1.x_range, y_range=plot1.y_range)

    tab1 = Panel(child=plot1, title="line + points")
    tab2 = Panel(child=plot2, title="points only")

    for i in yCols:
        if dfD.iloc[:,i].count() > 0:
            plot1.line(dfD.iloc[:,xCol],dfD.iloc[:,i], line_color=colors[i], line_width=1, legend=dfD.columns[i])
            plot1.scatter(dfD.iloc[:,xCol],dfD.iloc[:,i], marker="+", line_color=colors[i], line_width=1, legend=dfD.columns[i])
            plot2.scatter(dfD.iloc[:,xCol],dfD.iloc[:,i], marker="+", line_color=colors[i], line_width=1, legend=dfD.columns[i])

    tabs = Tabs(tabs=[ tab1, tab2 ])
    show(tabs)

    return tabs


def PDS_to_html(PDS_inputfile, xCol, yCols, HTML_outputfile, title=None, width=600, height=600):
    """

    :param PDS_inputfile:
    :param xCol:
    :param yCols:
    :param HTML_outputfile:
    :param title:
    :param width:
    :param height:
    :return:
    """
    dfD, dfM = PDS_to_df(PDS_inputfile)
    plot = df_plot(dfD, xCol, yCols, width=width, height=height)
    with open('my_template.jinja', 'r') as f:
        template = Template(f.read())
    js_resources = JSResources(mode='inline')
    css_resources = CSSResources(mode='inline')
    if not title:
        title = os.path.basename(PDS_inputfile)
    html = file_html(plot, None, title, template=template,
                     js_resources = js_resources, css_resources=css_resources,
                     template_variables={"metadata": dfM.sort_values(by='Attribute').to_html(index=False),
                                         "H3_title": title,
                                         "footer": "Created the " + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') })
    with open(HTML_outputfile, 'w') as f:
        f.write(html)
    return


def PDS_to_df(PDS_inputfile):
    """

    :param PDS_inputfile:
    :return:
    """
    df_data = pd.read_excel(PDS_inputfile, sheetname='Data')
    df_meta = pd.read_excel(PDS_inputfile, sheetname='Metadata', header=None, names=['Attribute', 'Value'])

    return df_data, df_meta


def df_to_PDS(df_data, df_meta, PDS_outputfile):
    """

    :param df_data:
    :param df_meta:
    :param PDS_outputfile:
    :return:
    """
    writer = pd.ExcelWriter(PDS_outputfile)

    df_data.to_excel(writer, sheet_name="Data", index=False)
    df_meta.to_excel(writer, sheet_name="Metadata", index=False, header=False)

    writer.save()
    return


def df_to_LiPD(df_data, df_meta, verbose=True):
    """

    :param df_data:
    :param df_meta:
    :param verbose:
    :return:
    """
    dict_out = collections.OrderedDict()
    parameters = df_data.columns
    for index, row in df_meta.iterrows():
        attributes = row['Attribute'].split('.')

        parameter = attributes[0]
        if len(attributes) == 1:
            if parameter in parameters:
                if verbose:
                    print('df_to_LiPD: Warning: at line %4d : %s is a parameter with no attribute => line '
                          'ignored'.format(index+1, parameter))
                continue
        else:
            if parameter not in parameters:
                if verbose:
                    print('df_to_LiPD: Warning: at line %4d : %s not present in Data worksheet => considered as '
                          'global attribute'.format(index+1, parameter))

        d = dict_out
        for attribute in attributes[0:-1] :
            d = d.setdefault(attribute, {})

        if d.get(attributes[-1]):
            if verbose:
                print('df_to_LiPD: Warning: at line %4d : %s already set with value %s => overwritten with new value '
                      '%s'.format(index+1, row['Attribute'], d.get(attributes[-1]), row['Value']))

        if row['Value'] == "True" :
            row['Value'] = True
        if row['Value'] == "False" :
            row['Value'] = False
        if isinstance(row['Value'], datetime.datetime):
            row['Value'] = row['Value'].isoformat()

        d[attributes[-1]] = row['Value']

    return dict_out
