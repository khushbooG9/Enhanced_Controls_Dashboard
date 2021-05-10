import dash
#from jitcache import Cache
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#cache = Cache()
app = dash.Dash(__name__, 
	meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"},]
)
server = app.server
app.config.suppress_callback_exceptions = True