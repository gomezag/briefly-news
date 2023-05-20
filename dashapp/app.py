import dash
from dash import dcc, html
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

# Define the layout of the app
app.layout = html.Div([
    html.H1("What's going on man!", className='title is-1'),
    html.Div(className='container', children=[
        html.Div(className='columns', children=[
            html.Div(className='column', id='resumen', children=[]),
            html.Div(className='column', children=[
                dcc.Graph(id='article_timeline'),
            ]),
#            html.Div(className='column', children=[]),
        ]),
    ]),
    dcc.Interval(id='heartbeat', interval=10 * 1000, n_intervals=0),
    dcc.Loading(id='encontrados-loading', className='gifloader', children=[
        html.H2(id='encontrados', className='title is-2 is-center'),]),
        html.Div(className='', children=[
        html.Div(className='columns', children=[
            html.Div(className='column', children=[
                    html.Div(className='', children=[
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
                                                          value=20)
                                            ])

                                        ]),
                                        html.Div(className='field is-grouped', children=[
                                            html.Div('Key: ', className='control label'),
                                            html.Div(className='control dropdown', children=[
                                                dcc.Dropdown(
                                                    options=[{'label': 'Personas', 'value': 'PER'},
                                                             {'label': 'Organizaciones', 'value': 'ORG'},
                                                             {'label': 'Misc.', 'value': 'MISC'}],
                                                    id='sel_key', value='PER')
                                            ]),
                                        ]),
                                        html.Button("Buscar", id="search", className='button is-info'),
                                        html.Button("Tagear", id="tag_btn", className='button is-info'),
                                    ])
            ]),
            html.Div(className='column', children=[
                dcc.Loading(id='form-loading', className='gifloader', children=[
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
            html.Div(className='column',
                     children=[
                         dcc.Loading(id='form-loading', className='gifloader', children=[
                             html.Div(id='clicktable', children=[])
                         ]),
                     ]),

        ]),
    ]),
    dcc.Loading(id='table-loading', className='gifloader', children=[
        html.Div(id='result_table', children=[]),
    ]),

    dcc.Store(id='articles'),
    dcc.Store(id='persons'),
    dcc.Store(id='tagged_articles'),
    dcc.Store(id='sites', data={
        'abc': xata.query('news_publisher', filter={'publisher_name': 'abc'})['records'][0]['id'],
        'lanacion': xata.query('news_publisher', filter={'publisher_name': 'lanacion'})['records'][0]['id']
    })
])



@app.callback(
    [Output('article_timeline', 'figure'), Output('resumen', 'children')],
    [Input('heartbeat', 'n_intervals'), State('article_timeline', 'relayoutData')]
)
def update_statistics(n, zoom_info):
    graphs = []
    total_articles = 0
    for site in ['abc', 'lanacion']:
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
                'aggs': {'byDay': {'dateHistogram': {'column': 'date', 'calendarInterval': 'day'}}}, 'filter':{
                    'publisher': siteid
                }})
            if res.status_code==200:
                data = pd.DataFrame(res.json()['aggs']['byDay']['values'])
                data['$key'] = pd.to_datetime(data['$key'])
                graphs.append(dict(x=data['$key'], y=data['$count'], type='bar', name=site))
            else:
                print(res.text)
    fig = {
            'data': graphs,
            'layout': {
                'title': 'Conteo de Artículos',
                'barmode': 'stack',
                'xaxis': {
                    'range':[datetime.now()-timedelta(days=30), datetime.now()],
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
    res = xata.client.search_and_filter().aggregateTable('news_article', {
        'aggs': {'byDay': {'dateHistogram': {'column': 'date', 'calendarInterval': 'day'}},
                 'total': {'count': "*"},
                 'cost': {'sum': {'column': 'tokens'}}}, 'filter': {
            '$exists': 'embedding'
        }})
    data = res.json()
    embedded_articles = data["aggs"]["total"]
    total_cost = data['aggs']['cost']*0.0004/1000
    results_children = [
        html.Div(className='box', children=[
            html.H3(className='title is-3', children=[f'Total de artículos: {total_articles}']),
            html.H3(className='title is-3', children=[f'Artículos con embedding: {embedded_articles} ']),
            html.H3(className='title is-3', children=[f'Gastado en embedding*: {round(total_cost, 2)} $']),
        ])
    ]
    return fig, results_children


@app.callback(
    [Output("encontrados", "children"),
     Output('articles', 'data'),
     Output('wordcloud', 'list'),
     Output('result_table', 'children')],
    [Input("search", "n_clicks"),
     State('title_search', 'value'),
     State('date_search', 'start_date'),
     State('date_search', 'end_date'),
     Input('sel_site', 'value'),
     State('limit', 'value'),
     State('body_search', 'value'),
     State('url_search', 'value'),
     State('sites', 'data')]
)
def update_search(btn, text, start_date, end_date, site, limit, body, url_search, sites):
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
    persons = pd.DataFrame(articles)
    persons = persons[['POIs']].explode('POIs').groupby('POIs').value_counts().reset_index().sort_values(
        'count', ascending=False)
    x = persons['count']
    a = 10
    b = 30
    persons['count_norm'] = a + (x - x.min()) * (b - a) / (x.max() - x.min() + 1)
    persons['label'] = persons['POIs'].astype(str) + ' - ' + persons['count'].astype(str)
    bpersons = persons[['POIs', 'count_norm', 'label']].to_numpy()


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
    return f"Articulos encontrados: {len(articles)}", articles, bpersons, [table]

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


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
