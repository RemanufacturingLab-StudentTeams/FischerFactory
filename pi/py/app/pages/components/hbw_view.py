from dash import html, callback, Input, Output
from state import PageStateManager

hbw_view = html.Div(
    [
        html.H2('HBW View'),
        html.Div([
# dynamically generated
        ], className='hbw-view-container button-menu', id='hbw-view-container')
    ],
    className='hbw-view'
)

@callback(
    Output('hbw-view-container', 'children'),
    Input('updater', 'n_intervals'),
    prevent_initial_call=True
)
def display_hbw(n_intervals):    
    psm = PageStateManager()
    page = 'global'
    
    buttons = [
        (
            html.Div(
                psm.get(page, f'rack_workpiece_[{x},{y}]_s_id', False),
                className='puck-' + psm.get(page, f'rack_workpiece_[{x},{y}]_s_type', False).lower() # class names will become 'puck-red', 'puck-blue', 'puck-white' or 'empty'
            )
            if psm.get(page,f'rack_workpiece_[{x},{y}]_s_type',False)
            else html.Div(className='puck-empty')
        )
            for x in range(3) 
            for y in range(3)
    ]
    
    return [
            html.Div(),
            html.Span('1', className='label'),
            html.Span('2', className='label'),
            html.Span('3', className='label'),
            html.Span('A', className='label'),
            *buttons[0:3], # button 0 to 3 exclusive, so the first 3
            html.Span('B', className='label'),
            *buttons[3:6],
            html.Span('C', className='label'),
            *buttons[6:9]
    ]

__all__ = ['hbw_view', 'display_hbw']