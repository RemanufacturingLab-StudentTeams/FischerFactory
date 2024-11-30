from dash import html

hbw_view = html.Div(
    [
        html.H2('HBW View'),
        html.Div([
            html.Div(),
            html.Span('1', className='label'),
            html.Span('2', className='label'),
            html.Span('3', className='label'),
            html.Span('A', className='label'),
            html.Button(),
            html.Button(),
            html.Button(),
            html.Span('B', className='label'),
            html.Button(),
            html.Button(),
            html.Button(),
            html.Span('C', className='label'),
            html.Button(),
            html.Button(),
            html.Button(),
        ], className='hbw-view-container button-menu')
    ],
    className='hbw-view'
)

__all__ = ['hbw_view']