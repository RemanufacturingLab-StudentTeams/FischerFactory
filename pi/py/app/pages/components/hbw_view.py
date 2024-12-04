from dash import html

hbw_view = html.Div(
    [
        html.H2('HBW View'),
        html.Div([
# dynamically generated
        ], className='hbw-view-container button-menu')
    ],
    className='hbw-view'
)

__all__ = ['hbw_view']