import dash
from time import sleep
from dash import dcc, html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from database.xata_api import XataAPI
from datetime import datetime, timedelta
from dash_holoniq_wordcloud import DashWordcloud
import pandas as pd

# Initialize the app
app = dash.Dash(__name__)
xata = XataAPI()

DEFAULT_START_DATE = (datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d')
DEFAULT_END_DATE = datetime.now().strftime('%Y-%m-%d')
loading_style = {'position': 'absolute', 'align-self': 'center'}

# Define the layout of the app
app.layout = html.Div([
    html.H1("What's going on man!", className='title is-1'),
    html.Div(className='container', children=[
        html.Div(className='columns', children=[
            html.Div(className='column', id='resumen', children=[]),
            html.Div(className='column', id='resumen_graph', children=[
                dcc.Graph(id='article_timeline', style={"display": "none"}),
                html.Img(id='graph-loading', src="https://cdn.dribbble.com/users/1040528/screenshots/5100277/eye.gif", children=[], style={"display": "inline"})
            ]
            ),
#            html.Div(className='column', children=[]),
        ]),
    ]),
    dcc.Interval(id='heartbeat', interval=10 * 1000, n_intervals=0),
    # dcc.Loading(id='poinet-loading', className='gifloader', children=[
    #     dcc.Graph(id='poi-net')
    # ]),
    dcc.Loading(id='encontrados-loading', className='gifloader', children=[
        html.H2(id='encontrados', className='title is-2 is-center'),]),
        html.Div(className='', children=[
        html.Div(className='columns', children=[
            html.Div(className='column', id='formCol', children=[
                    html.Div(className='form', children=[
                                        html.Div(className="field is-grouped", children=[
                                            html.Label('Title contains: ', className='control label'),
                                            html.Div(className='control', children=[
                                                dcc.Input(id='title_search',
                                                          type='text',
                                                          placeholder='Search in headlines',
                                                          className='input')
                                            ]),
                                        ]),
                                        html.Div(className="field is-grouped", children=[
                                            html.Label('Body contains: ', className='control label'),
                                            html.Div(className='control', children=[
                                                dcc.Input(id='body_search',
                                                          type='text',
                                                          placeholder='Search in headlines',
                                                          className='input')
                                            ]),
                                        ]),
                                        html.Div(className="field is-grouped", children=[
                                            html.Label('URL contains: ', className='control label'),
                                            html.Div(className='control', children=[
                                                dcc.Input(id='url_search',
                                                          type='text',
                                                          placeholder='Search in headlines',
                                                          className='input')
                                            ]),
                                        ]),
                                        html.Div(className="field is-grouped", children=[
                                            html.Label('POI: ', className='control label'),
                                            html.Div(className='control', children=[
                                                dcc.Input(id='poi_search',
                                                          type='text',
                                                          placeholder='Search for POI',
                                                          className='input')
                                            ]),
                                        ]),
                                        html.Div(id="date_search_group", className='field is-grouped is-centered', children=[
                                            html.Label("Fechas: ", className='control label'),
                                            html.Div(className='control', children=[
                                                dcc.DatePickerRange(id='date_search',
                                                                    start_date=DEFAULT_START_DATE,
                                                                    end_date=DEFAULT_END_DATE),
                                            ]),
                                        ]),
                                        html.Div(className='field is-grouped', children=[
                                            html.Div('Sitio: ', className='control label'),
                                            html.Div(className='control dropdown', children=[
                                                dcc.Dropdown(
                                                    options=[{'label': 'ABC Color', 'value': 'abc'},
                                                             {'label': 'La Nación Py', 'value': 'lanacion'},
                                                             {'label': 'Todos', 'value': 'all'}],
                                                    id='sel_site', value='all')
                                            ]),

                                        ]),
                                        html.Div(className='field is-grouped', children=[
                                            html.Div('Limit: ', className='control label'),
                                            html.Div(className='control', children=[
                                                dcc.Input(type='number',
                                                          min=1,
                                                          id='limit',
                                                          className='control input',
                                                          value=500)
                                            ])

                                        ]),
                                        # html.Div(className='field is-grouped', children=[
                                        #     html.Div('Key: ', className='control label'),
                                        #     html.Div(className='control dropdown', children=[
                                        #         dcc.Dropdown(
                                        #             options=[{'label': 'Personas', 'value': 'PER'},
                                        #                      {'label': 'Organizaciones', 'value': 'ORG'},
                                        #                      {'label': 'Misc.', 'value': 'MISC'}],
                                        #             id='sel_key', value='PER')
                                        #     ]),
                                        # ]),
                                        dcc.Loading(id='searchbtn-loading', className='gifloader', type='default',
                                                    children=[html.Button("Buscar", id="search", className='button is-info')]),
                                        # dcc.Loading(id='poibtn-loading', className='gifloader', type='default',
                                        #             children=[html.Button("POIs", id='poi-btn', className='button is-info')]),
                                    ])
            ]),
            html.Div(className='column', id='wordcloudCol', children=[
                dcc.Loading(id='wordcloud-loading', className='gifloader', children=[
                    DashWordcloud(id='wordcloud',
                              list=[],
                              width=700, height=600,
                              gridSize=16,
                              color='#f0f0c0',
                              backgroundColor='#001f00',
                              shuffle=False,
                              rotateRatio=0.5,
                              shrinkToFit=True,
                              shape='circle',
                              hover=True
                              ),]),
            ]),
            html.Div(className='column', id='infoCol',
                     children=[
                         dcc.Loading(id='table-loading', className='gifloader', children=[
                             html.Div(id='clicktable', className='clicktable', children=[])
                         ]),
                     ]),

        ]),
    ]),
    dcc.Loading(id='table-loading', className='gifloader', children=[
        html.Div(id='result_table', className='resulttable', children=[]),
    ]),

    dcc.Store(id='articles'),
    dcc.Store(id='persons'),
    dcc.Store(id='tagged_articles'),
    dcc.Store(id='sites', data={
        'abc': xata.query('news_publisher', filter={'publisher_name': 'abc'})['records'][0]['id'],
        'lanacion': xata.query('news_publisher', filter={'publisher_name': 'lanacion'})['records'][0]['id'],
        'cincodias': xata.query('news_publisher', filter={'publisher_name': 'cincodias'})['records'][0]['id'],
        'ultimahora': xata.query('news_publisher', filter={'publisher_name': 'ultimahora'})['records'][0]['id']
    })
])

@app.callback(
    [Output('resumen', 'children')],
    [Input('heartbeat', 'n_intervals')]
)
def update_summary(n):
    res = xata.client.search_and_filter().aggregateTable('news_article', {
        'aggs': {'total': {'count': "*"}
                 }
        })
    data = res.json()
    total_articles = data["aggs"]["total"]
    res = xata.client.search_and_filter().aggregateTable('news_article', {
        'aggs': {'total': {'count': "*"},
                 'cost': {'sum': {'column': 'tokens'}}
                 },
        'filter': {
            '$exists': 'embedding'
                  }
        })
    data = res.json()
    embedded_articles = data["aggs"]["total"]
    total_cost = data['aggs']['cost']*0.0004/1000
    res = xata.client.search_and_filter().aggregateTable('news_article', {
        'aggs': {'total': {'count': "*"}}, 'filter': {
            '$exists': 'POIs'
        }})
    data = res.json()
    tagged_articles = data["aggs"]["total"]
    results_children = [
        html.Div(className='box', children=[
            html.H3(className='title is-3', children=[f'Total de artículos: {total_articles}']),
            html.H3(className='title is-3', children=[f'Artículos con tags: {tagged_articles} ']),
            html.H3(className='title is-3', children=[f'Artículos con embedding: {embedded_articles} ']),
            html.H3(className='title is-3', children=[f'Gastado en embedding*: {round(total_cost, 2)} $']),
        ])
    ]
    return results_children

@app.callback(
    [Output('article_timeline', 'figure'), Output('graph-loading', 'style'), Output('article_timeline', 'style')],
    [Input('heartbeat', 'n_intervals'), State('article_timeline', 'relayoutData')]
)
def update_statistics(n, zoom_info):
    graphs = []
    total_articles = 0
    for site in ['abc', 'lanacion', 'ultimahora', 'cincodias']:
        siteid = xata.query('news_publisher', filter={'publisher_name': site})['records'][0]['id']
        if site == 'abc':
            for source in ['abccolor', 'EFE']:
                res = xata.client.search_and_filter().aggregateTable('news_article', {
                    'aggs': {'byDay': {'dateHistogram': {'column': 'date', 'calendarInterval': 'day'}},
                             'total': {'count': '*'}}, 'filter': {
                        'source': source
                    }})
                if res.status_code == 200:
                    data = pd.DataFrame(res.json()['aggs']['byDay']['values'])
                    total_articles += res.json()['aggs']['total']
                    data['$key'] = pd.to_datetime(data['$key'])
                    graphs.append(dict(x=data['$key'], y=data['$count'], type='bar', name=source))
                else:
                    print(res.text)
        else:
            res = xata.client.search_and_filter().aggregateTable('news_article', {
                'aggs': {'byDay': {'dateHistogram': {'column': 'date', 'calendarInterval': 'day'}},
                         'total': {'count': '*'}},
                'filter':{
                    'publisher': siteid
                }})
            if res.status_code == 200:
                data = pd.DataFrame(res.json()['aggs']['byDay']['values'])
                if len(data)>0:
                    total_articles += res.json()['aggs']['total']
                    data['$key'] = pd.to_datetime(data['$key'])
                    graphs.append(dict(x=data['$key'], y=data['$count'], type='bar', name=site))
            else:
                print(res.text)

    for field in ['embedding', 'POIs']:
        res = xata.client.search_and_filter().aggregateTable('news_article', {
            'aggs': {'byDay': {'dateHistogram': {'column': 'date', 'calendarInterval': 'day'}}},
            'filter': {'$exists': field}
        })
        data = pd.DataFrame(res.json()['aggs']['byDay']['values'])
        data['$key'] = pd.to_datetime(data['$key'])
        graphs.append(dict(x=data['$key'], y=data['$count'], type='bar', name=field, base=0, opacity=0.5))

    fig = {
            'data': graphs,
            'layout': {
                'title': 'Conteo de Artículos',
                'barmode': 'stack',
                'xaxis': {
                    'range': [datetime.now()-timedelta(days=30), datetime.now()],
                    'rangeSlider': True
                },
                'yaxis': {},
            }
    }
    if zoom_info:
        for axis_name in ['axis',]:
            if f'x{axis_name}.range[0]' in zoom_info:
                fig['layout'][f'x{axis_name}']['range'] = [
                    zoom_info[f'x{axis_name}.range[0]'],
                    zoom_info[f'x{axis_name}.range[1]']
                ]
            if f'y{axis_name}.range[0]' in zoom_info:
                fig['layout'][f'y{axis_name}']['range'] = [
                    zoom_info[f'y{axis_name}.range[0]'],
                    zoom_info[f'y{axis_name}.range[1]']
                ]
    if fig:
        return fig, {'display': 'none'}, {'display': 'inline'}
    else:
        return None, {'display': 'inline'}, {'display': 'none'}

@app.callback(
    [Output('result_table', 'children')],
    [Input('articles', 'data'),
     State('sites', 'data')]
)
def update_results_table(articles, sites):

    rows = []
    for article in articles:
        row = []
        for key in ['date', 'title', 'subtitle', 'url', 'authors']:
            if key == 'url':
                try:
                    site = [key for key, value in sites.items() if value == article['publisher']['id']][0]
                except:
                    site = article['publisher']
                cell = html.Td(html.A(str(site), href=article[key]))
            elif key == 'authors':
                cell = html.Td(", ".join(article[key]))
            else:
                cell = html.Td(article[key])
            row.append(cell)
        rows.append(html.Tr(children=row))
    children = [html.Th(key) for key in ['Fecha', 'Titular', 'Resumen', 'URL', 'Autores', 'Sitio']]
    children.extend(rows)
    table = html.Table(children=children, className='table')
    return [table]

@app.callback(
    [Output("encontrados", "children"),
     Output('articles', 'data'),
     Output('search', 'children')],
    [Input("search", "n_clicks"),
     State('title_search', 'value'),
     State('date_search', 'start_date'),
     State('date_search', 'end_date'),
     Input('sel_site', 'value'),
     State('limit', 'value'),
     State('body_search', 'value'),
     State('url_search', 'value'),
     State('poi_search', 'value')]
)
def update_search(btn, text, start_date, end_date, site, limit, body, url_search, poi):
    query = {}
    date_q = {}
    if start_date:
        st_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        st_date = datetime.strptime(DEFAULT_START_DATE, '%Y-%m-%d')
    date_q['$gt'] = st_date
    if end_date:
        ed_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        ed_date = datetime.strptime(DEFAULT_END_DATE, '%Y-%m-%d')
    date_q['$lt'] = ed_date
    query['date'] = date_q
    if text:
        query['title'] = {'$contains': text}
                         #{'title':{'$contains': text.lower()}},
                         #{'title':{'$contains': text.capitalize()}}
                         #]
    if body:
        query['article_body'] = {'$contains': body}
    if site:
        if site != 'all':
            query['publisher.publisher_name'] = site
        else:
            query.pop('publisher.publisher_name', None)

    if url_search:
        query['url'] = {'$contains': url_search}
    if poi:
        query['POIs'] = {'$includes': poi}
    chunks = 0
    more = True
    cursor = None
    articles = []
    while more:
        cquery = dict(
            filter=query,
            page={'after': cursor, 'size': 20},
            sort={'date': 'desc'}
        )

        if cursor:
            cquery.pop('sort', None)
            cquery.pop('filter', None)

        res = xata.query('news_article', **cquery)
        articles.extend(res['records'])
        if res.get('meta', {}).get('page', {}).get('more', False):
            more = True
            chunks += 1
            if limit:
                if chunks * 20 >= limit:
                    more = False
            cursor = res["meta"]["page"]["cursor"]  # save next cursor for results
        else:
            more = False

    return f"Articulos encontrados: {len(articles)}", articles, 'Buscar'


@app.callback(
    [Output('wordcloud', 'list')],
    [Input('articles', 'data')]
)
def update_wordcloud(articles):
    persons = pd.DataFrame(articles)
    if 'POIs' in persons.columns:
        persons = persons[['POIs']].explode('POIs').groupby('POIs').value_counts().reset_index().sort_values(
            'count', ascending=False)
        x = persons['count']
        a = 10
        b = 30
        persons['count_norm'] = a + (x - x.min()) * (b - a) / (x.max() - x.min() + 1)
        persons['label'] = persons['POIs'].astype(str) + ' - ' + persons['count'].astype(str)
        bpersons = persons[['POIs', 'count_norm', 'label']].to_numpy()
    else:
        bpersons = []

    return [bpersons]


@app.callback(
    Output('clicktable', 'children'),
    [Input('wordcloud', 'click'),
     State('articles', 'data')]
)
def wordcloud_click(clickdata, articles):
    if clickdata:
        name = clickdata[0]
        result = []
        for article in articles:
            if name in article.get('POIs', []):
                result.append(html.Li(children=[
                    article['date'][:10]+': ',
                    html.A(article['title'], href=article['url'])]))
        return html.Div(children=[html.H3(name, className='title is-3'),
                                  html.Div(children=result)
               ])
    else:
        return ['']


def wordcloud_hover(item, dimension, event):
    return True


# def count_coincidences(related1, related2):
#     weight = 0
#     for key, value in related1.items():
#         if key in related2:
#             weight += min(value, related2[key])
#     return weight
# @app.callback(
#     [Output('poi-net', 'figure'), Output('poi-btn', 'children')],
#     [Input('poi-btn', 'n_clicks')]
# )
# def update_poi_graph(n):
#     articles = []
#     query = ""
#     chunks = 0
#     more = True
#     cursor=0
#     while more:
#         cquery = dict(
#             filter=query,
#             page={'after': cursor, 'size': 200},
#         )
#
#         if cursor:
#             cquery.pop('sort', None)
#             cquery.pop('filter', None)
#
#         res = xata.query('POI', **cquery)
#         articles.extend(res['records'])
#         if res.get('meta', {}).get('page', {}).get('more', False):
#             more = True
#             chunks += 1
#             if chunks > 5:
#                 more = False
#             cursor = res["meta"]["page"]["cursor"]  # save next cursor for results
#         else:
#             more = False
#     for i, poi in enumerate(articles):
#         related_pois = {}
#         for article in poi['articles']:
#             for cpoi in articles:
#                 if article in cpoi['articles'] and cpoi['label'] != poi['label']:
#                     if not related_pois.get(cpoi['label'], False):
#                         related_pois[cpoi['label']] = 1
#                     else:
#                         related_pois[cpoi['label']] += 1
#         poi['related'] = related_pois
#     df = pd.DataFrame(articles)
#     df['connections'] = df['related'].apply(lambda x: count_coincidences(x, df['related']))
#     # Create nodes
#     nodes = [go.Scatter(
#         x=[0],
#         y=[i],
#         mode='markers+text',
#         text=df.loc[i, 'label'],
#         textposition='middle right',
#         marker=dict(size=15),
#     ) for i in range(len(df))]
#
#     # Create connections
#     connections = []
#     for i in range(len(df)):
#         for j in range(i + 1, len(df)):
#             related1 = df.loc[i, 'related']
#             related2 = df.loc[j, 'related']
#             weight = count_coincidences(related1, related2)
#             if weight > 0:
#                 connections.append(go.Scatter(
#                     x=[0, 1],
#                     y=[i, j],
#                     mode='lines',
#                     line=dict(width=weight),
#                     hovertemplate='Weight: ' + str(weight),
#                 ))
#
#     # Create layout
#     layout = go.Layout(
#         title='Graph',
#         showlegend=False,
#         height=600,
#         hovermode='closest',
#         annotations=[
#             go.layout.Annotation(
#                 x=0,
#                 y=i,
#                 xref='x',
#                 yref='y',
#                 text=df.loc[i, 'label'],
#                 showarrow=False,
#             ) for i in range(len(df))
#         ]
#     )
#
#     # Create figure
#     figure = go.Figure(data=nodes + connections, layout=layout)
#
#     return figure, 'POI'
#

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)