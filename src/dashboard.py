import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        '/assets/css/dashboard.css']

platform_surface_variables = {
    'C-MAN WEATHER STATIONS': ['sst', 'atmp', 'slp', 'windspd', 'winddir'],
    'DRIFTING BUOYS (GENERIC)': ['sst', 'slp'],
    'ICE BUOYS': ['slp'],
    'MOORED BUOYS (GENERIC)': ['sst', 'atmp', 'slp', 'windspd', 'winddir', 'wvht', 'dewpoint'],
    'RESEARCH': ['sst', 'atmp', 'slp', 'windspd', 'winddir', 'dewpoint'],
    'SHIPS (GENERIC)': ['sst', 'atmp', 'slp', 'windspd', 'winddir', 'clouds', 'dewpoint'],
    'SHORE AND BOTTOM STATIONS (GENERIC)': ['sst', 'atmp', 'precip', 'slp', 'windspd', 'winddir', 'clouds', 'dewpoint'],
    'TIDE GAUGE STATIONS (GENERIC)': ['sst', 'atmp', 'slp', 'windspd', 'winddir', 'dewpoint'],
    'TROPICAL MOORED BUOYS': ['sst', 'atmp', 'windspd', 'winddir'],
    'TSUNAMI WARNING STATIONS': ['water_col_ht'],
    'UNKNOWN': ['waterlevel_met_res', 'waterlevel_wrt_lcd'],
    'UNMANNED SURFACE VEHICLE': ['sst', 'atmp', 'slp', 'hur'],
    'VOLUNTEER OBSERVING SHIPS': ['sst', 'atmp', 'slp', 'windspd', 'winddir', 'clouds', 'dewpoint'],
    'VOLUNTEER OBSERVING SHIPS (GENERIC)': ['sst', 'atmp', 'slp', 'windspd', 'winddir', 'wvht', 'clouds', 'dewpoint'],
    'VOSCLIM': ['waterlevel_met_res', 'waterlevel_wrt_lcd'],
    'WEATHER AND OCEAN OBS': ['sst', 'atmp', 'slp', 'windspd', 'winddir', 'wvht', 'dewpoint'],
    'WEATHER BUOYS': ['sst', 'atmp', 'slp', 'windspd', 'winddir', 'wvht', 'dewpoint'],
    'WEATHER OBS': ['atmp', 'slp', 'windspd', 'winddir']
}
platform_depth_variables = {
    'AUTONOMOUS PINNIPEDS': ['ztmp'],
    'CLIMATE REFERENCE MOORED BUOYS': ['ztmp', 'zsal'],
    'GLIDERS': ['ztmp', 'zsal'],
    'ICE BUOYS': ['ztmp'],
    'OCEAN TRANSPORT STATIONS (GENERIC)': ['ztmp', 'zsal'],
    'PROFILING FLOATS AND GLIDERS (GENERIC)': ['ztmp', 'zsal'],
    'SHORE AND BOTTOM STATIONS (GENERIC)': ['ztmp', 'zsal'],
    'TROPICAL MOORED BUOYS': ['ztmp', 'zsal'],
}

# use date = "now-7days", but if updates stop you can still test using a specific date
#  ... for testing l  ocation_date = "2020-03-12T23:59:00Z"
location_date = "now-7days"

# use plot_dates = now-14days
# ... for testing   plot_date = "2020-03-05T23:59:00Z"
plot_date = "now-14days"

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv(
    'http://dunkel.pmel.noaa.gov:8336/erddap/tabledap/osmc_gts.csv?platform_code%2Cplatform_type%2Ctime%2Clongitude%2Clatitude&distinct()&orderByMax("platform_code,time")&time>=' + location_date,
    skiprows=[1])


# mapbox={'style': 'open-street-map'},
def serve_layout():
    dff = df
    platform_count = dff.shape[0]
    dff['platform_color'] = dff['platform_type'].apply(platform_color)
    dff['map_text'] = dff.apply(map_text, axis=1)
    return html.Div([
        html.Div([
            html.Div(['OSMC Dashboard'], className='admin-header-text'),
            html.Div(id='platform_info', className='admin-header-subtext'),
            html.Div(id='loaders', children=[
                dcc.Loading(id="loading-2", children=[html.Div(id="loading-output-2")], type="default", color="yellow"),
            ])
        ], className='grid-container admin-header'),
        html.Div([
            html.Div([
                dcc.Graph(
                    id='map-div',
                    figure={
                        'data': [dict(
                            type='scattergeo',
                            mode='markers',
                            lon=dff['longitude'],
                            lat=dff['latitude'],
                            text=dff['map_text'],
                            marker={
                                'size': 10,
                                'opacity': 0.9,
                                'line': {'width': 1, 'color': 'white'},
                                'color': dff['platform_color']
                            }
                        )],
                        'layout': dict(
                            margin={"r": 0, "t": 0, "l": 0, "b": 0},
                            height=300,
                            hovermode='closest',
                            hoverinfo="lat+lon+text",
                            hovertemplate='<b>%{text}</b>',
                            geo=dict(
                                scope='world',
                                resolution=50,
                                showcoastlines=True, coastlinecolor="RebeccaPurple",
                                showland=True, landcolor="LightGreen",
                                showocean=True, oceancolor="LightBlue"
                            )
                        )
                    }
                )
            ], style={'width': '90%', 'display': 'inline-block', 'padding': '0 0', 'grid-column':'1 / span 2'}),
                html.Div([

                        dcc.Graph(id='atmp')

                ], id='atmp_parent', style={'display': 'none'}),
                html.Div([
                    dcc.Graph(id='sst')
                ], id='sst_parent', style={'display': 'none'}),
                html.Div([
                    dcc.Graph(id='slp')
                ], id='slp_parent', style={'display': 'none'}),
                html.Div([
                    dcc.Graph(id='dewpoint')
                ], id='dewpoint_parent', style={'display': 'none'}),
                html.Div([
                    dcc.Graph(id='wvht')
                ], id='wvht_parent', style={'display': 'none'}),
                html.Div([
                    dcc.Graph(id='windspd')
                ], id='windspd_parent', style={'display': 'none'}),
                html.Div([
                    dcc.Graph(id='winddir')
                ], id='winddir_parent', style={'display': 'none'}),
                html.Div([
                    dcc.Graph(id='precip')
                ], id='precip_parent', style={'display':'none'}),
                html.Div([

                    dcc.Graph(id='zsal')

                ], id='zsal_parent', style={'visibility': 'hidden'}),
                html.Div([

                    dcc.Graph(id='ztmp')

                ], id='ztmp_parent', style={'visibility': 'hidden'}),
        ], style={'display': 'grid', 'grid-template-columns': '25vw 25vw 25vw 25vw', 'grid-template-rows': 'auto'}, id='outer_grid'),
        html.Div(id='load-urls', style={'display':'none'}),
        html.Div(id='data-div', style={'display':'none'}),
        html.Div(id='selected')
    ])


def map_text(row):
    return 'Platform code = ' + str(row['platform_code']) + '<br>Platform type = ' + str(row['platform_type'])


def platform_color(type):
    if type == 'AUTONOMOUS PINNIPEDS':
        return '#FF0000'
    if type == 'C-MAN WEATHER STATIONS':
        return '#FF7F00'
    if type == 'CLIMATE REFERENCE MOORED BUOYS':
        return '#FFD400'
    if type == 'DRIFTING BUOYS (GENERIC)':
        return '#FFFF00'
    if type == 'GLIDERS':
        return '#BFFF00'
    if type == 'ICE BUOYS':
        return '#6AFF00'
    if type == 'MOORED BUOYS (GENERIC)':
        return '#00EAFF'
    if type == 'OCEAN TRANSPORT STATIONS (GENERIC)':
        return '#0095FF'
    if type == 'PROFILING FLOATS AND GLIDERS (GENERIC)':
        return '#0040FF'
    if type == 'RESEARCH':
        return '#AA00FF'
    if type == 'SHIPS (GENERIC)':
        return '#FF00AA'
    if type == 'SHORE AND BOTTOM STATIONS (GENERIC)':
        return '#EDB9B9'
    if type == 'TIDE GAUGE STATIONS (GENERIC)':
        return '#E7E9B9'
    if type == 'TROPICAL MOORED BUOYS':
        return '#B9EDE0'
    if type == 'TSUNAMI WARNING STATIONS':
        return '#B9D7ED'
    if type == 'UNKNOWN':
        return '#DCB9ED'
    if type == 'UNMANNED SURFACE VEHICLE':
        return '#8F2323'
    if type == 'VOLUNTEER OBSERVING SHIPS':
        return '#8F6A23'
    if type == 'VOLUNTEER OBSERVING SHIPS (GENERIC)':
        return '#4F8F23'
    if type == 'VOSCLIM':
        return '#23628F'
    if type == 'WEATHER AND OCEAN OBS':
        return '#6B238F'
    if type == 'WEATHER BUOYS':
        return '#000000'
    if type == 'WEATHER OBS':
        return '#737373'
    return '#FFFFFF'


def make_layout(title, axis_title):
    return dict(
        title=title,
        xaxis={
            'title': 'time',
        },
        yaxis={
            'title': axis_title,
        },
        height=300,
        automargin="true",
        hovermode='closest',
        clickmode='event+select'
    )


def make_figure(ts, title, label):
    if label in ts:
        reduced = ts.dropna(subset=[label])
        if reduced.shape[0] == 0:
            return dict(figure={'data' : [], 'layout': {}}, style=dict(display='none'), count=0)
        else:
            data = [dict(x=reduced['time'], y=reduced[label])]
            layout = make_layout(title, label)
            return dict(figure={'data': data, 'layout': layout}, style=dict(display='inline-block'), count=1)
    else:
        return dict(figure={'data' : [], 'layout': {}}, style=dict(display='none'), count=0)


app.layout = serve_layout


@app.callback([
    dash.dependencies.Output('load-urls', 'children'),
    dash.dependencies.Output('platform_info', 'children'),
],
    [dash.dependencies.Input('map-div', 'clickData')])
def data_url(selection):
    if selection is None:
        raise dash.exceptions.PreventUpdate()
    else:
        point = selection['points'][0]
        point_text = point['text']
        point_text = point_text.replace('<br>', ' ')
        contents = point_text.split()
        platform_code = contents[3].strip()
        platform_type = ' '.join(contents[7:len(contents)])
        title = 'Platform code=' + platform_code + ' Platform type=' + platform_type
        surf_url="none"
        depth_url = "none"
        if platform_type in platform_surface_variables:
            surf_vars = '%2C'.join(platform_surface_variables[platform_type])
            # TODO figure out != NaN for all variables
            surf_url = 'http://dunkel.pmel.noaa.gov:8336/erddap/tabledap/osmc_gts.csv?time%2C' + surf_vars + '&platform_code="' + platform_code + '"&orderBy("time")&time>' + plot_date
        if platform_type in platform_depth_variables:
            # TODO figure out sort order (and != NaN)
            depth_vars = '%2C'.join(platform_depth_variables[platform_type])
            depth_url = 'http://dunkel.pmel.noaa.gov:8336/erddap/tabledap/osmc_gts.csv?time%2Cobservation_depth%2C' + depth_vars + '&platform_code="' + platform_code + '"&orderBy("time,observation_depth")&time>' + plot_date
        data_calls = {
            'surface': surf_url,
            'depth': depth_url
        }

        return json.dumps(data_calls), title

# Combining the surface and depth calls into one call back and making one JSON with both
@app.callback([
    dash.dependencies.Output('atmp', 'figure'),
    dash.dependencies.Output('atmp_parent', 'style'),
    dash.dependencies.Output('precip', 'figure'),
    dash.dependencies.Output('precip_parent', 'style'),
    dash.dependencies.Output('slp', 'figure'),
    dash.dependencies.Output('slp_parent', 'style'),
    dash.dependencies.Output('sst', 'figure'),
    dash.dependencies.Output('sst_parent', 'style'),
    dash.dependencies.Output('winddir', 'figure'),
    dash.dependencies.Output('winddir_parent', 'style'),
    dash.dependencies.Output('windspd', 'figure'),
    dash.dependencies.Output('windspd_parent', 'style'),
    dash.dependencies.Output('wvht', 'figure'),
    dash.dependencies.Output('wvht_parent', 'style'),
    dash.dependencies.Output('ztmp_parent', 'style'),
    dash.dependencies.Output('ztmp', 'figure'),
    dash.dependencies.Output('zsal_parent', 'style'),
    dash.dependencies.Output('zsal', 'figure'),
    dash.dependencies.Output("loading-output-2", "children"),
],
    [dash.dependencies.Input('load-urls', 'children')]
)
def read_data(calls_json):
    # read both surface and depth data
    # start with surface
    if calls_json is None:
        raise dash.exceptions.PreventUpdate()
    else :
        calls_json = json.loads(calls_json)
    if 'surface' not in calls_json:
        column_names = ["NO DATA"]
        sdf = pd.DataFrame(columns=column_names)
    else:
        url = calls_json['surface']
        if url != 'none':
            sdf = pd.read_csv(url, skiprows=[1])
        else:
            column_names = ["NO DATA"]
            sdf = pd.DataFrame(columns=column_names)

    if 'depth' not in calls_json:
        column_names = ["NO DATA"]
        zdf = pd.DataFrame(columns=column_names)
    else:
        url = calls_json['depth']
        if url != 'none':
            zdf = pd.read_csv(url, skiprows=[1])
        else:
            column_names = ["NO DATA"]
            zdf = pd.DataFrame(columns=column_names)
    # make graphs and return them without writing data to the empty dif
    if 'NO DATA' in sdf:
        splots = {'data': [], 'layout': {}}, dict(display='none'), {'data': [], 'layout': {}}, dict(display='none'), {'data': [], 'layout': {}}, dict(display='none'), {'data': [], 'layout': {}}, dict(display='none'), {'data': [], 'layout': {}}, dict(display='none'), {'data': [], 'layout': {}}, dict(display='none'), {'data': [], 'layout': {}}, dict(display='none')
    else :
        airt = make_figure(sdf, 'Air Temperature', 'atmp')
        precip = make_figure(sdf, 'Precipitation', 'precip')
        slp = make_figure(sdf, 'Sea Level Presure', 'slp')
        sst = make_figure(sdf, 'Sea Surface Temperature', 'sst')
        winddir = make_figure(sdf, 'Wind Direction', 'winddir')
        windspd = make_figure(sdf, 'Wind Speed', 'windspd')
        wvht = make_figure(sdf, 'Wave Height', 'wvht')
        count = airt['count'] + precip['count'] + slp['count'] + sst['count'] + winddir['count'] + windspd['count'] + wvht['count']
        double_span = 'span 2'
        single_span = 'auto'
        if count < 4:
            if airt['count'] == 1:
                airt['style']['grid-column'] = double_span
            if precip['count'] == 1:
                precip['style']['grid-column'] = double_span
            if slp['count'] == 1:
                slp['style']['grid-column'] = double_span
            if sst['count'] == 1:
                sst['style']['grid-column'] = double_span
            if winddir['count'] == 1:
                winddir['style']['grid-column'] = double_span
            if windspd['count'] == 1:
                windspd['style']['grid-column'] = double_span
            if wvht['count'] == 1:
                wvht['style']['grid-column'] = double_span
        else:
            if airt['count'] == 1:
                airt['style']['grid-column'] = single_span
            if precip['count'] == 1:
                precip['style']['grid-column'] = single_span
            if slp['count'] == 1:
                slp['style']['grid-column'] = single_span
            if sst['count'] == 1:
                sst['style']['grid-column'] = single_span
            if winddir['count'] == 1:
                winddir['style']['grid-column'] = single_span
            if windspd['count'] == 1:
                windspd['style']['grid-column'] = single_span
            if wvht['count'] == 1:
                wvht['style']['grid-column'] = single_span
        splots = airt['figure'], airt['style'], precip['figure'], precip['style'], slp['figure'], slp['style'], sst['figure'], sst['style'], winddir['figure'], winddir['style'], windspd['figure'], windspd['style'], wvht['figure'], wvht['style']

    if 'NO DATA' in zdf:
        zplots = dict(visibility='hidden'), {'data': [], 'layout': {}},  dict(visibility='hidden'), {'data': [], 'layout': {}}
    else:
        # Remove all zsal rows that have no data to make zsal interpolated grid
        zsal_data = zdf.loc[zdf['zsal'].notna()]
        zsal_plot = make_depth_plot(zsal_data, 'zsal')
        # Remove all rows that have no data to make ztmp plot
        ztmp_data = zdf.loc[zdf['ztmp'].notna()]
        ztmp_plot = make_depth_plot(ztmp_data, 'ztmp')
        zplots = sum ((ztmp_plot, zsal_plot), ())
    # Concatenate the tuples, that last bit turns the string '' into a tuple,
    # Passing an empty string to the loading div to shut off the loading animation
    all_plots = splots + zplots + ('',)
    return all_plots

def make_depth_plot(depth_frame, var):
    # make a regularly spaced axis base on the min and max depth for all dives
    minn = depth_frame['observation_depth'].min()
    maxx = depth_frame['observation_depth'].max()
    regular_depths = np.linspace(minn, maxx, num=250, endpoint=True)


    # Question 10 https://stackoverflow.com/questions/47152691/how-to-pivot-a-dataframe
    # Takes the long string of dives and organizes it in columns by series
    # The first column is the depth, then columns for the observations followed by another column of depths
    # for the next dive and so on
    depth_frame.insert(0, 'count', depth_frame.groupby('time').cumcount())
    df2 = depth_frame.pivot(index='count', columns='time', values=['observation_depth','zsal','ztmp'])

    # Pull out all the times (not guaranteed to be sorted so sort them)
    times = df2.columns.unique(level=1).values
    times.sort()

    # make empty dataframes for the interpolated data
    depth_interp = pd.DataFrame(columns=times, index=regular_depths)
    # Interpolate the values of zsal and ztmp onto the regular depth axis
    for t in times:
        dive = df2.xs(t, level='time', axis=1)
        dive_var = np.interp(regular_depths, dive['observation_depth'],dive[var])
        depth_interp[t] = dive_var

    plot_data = [dict(x=times, y=regular_depths, z=depth_interp.values, type='heatmap', xgap=2)]
    if ( var == 'zsal'):
        title = 'Salinity'
    else:
        title = 'Temperature'
    plot_layout = dict(autosize=True,
                       yaxis={'automargin': 'true', 'autorange': 'reversed'},
                       title=title)
    if depth_interp.isnull().all().all():
        return dict(visibility='hidden'), {'data': plot_data, 'layout': plot_layout}
    else:
        return dict(visibility='visible'), {'data': plot_data, 'layout': plot_layout}

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server()
