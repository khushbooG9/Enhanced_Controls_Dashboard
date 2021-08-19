from logging import debug
import dash

# README: to use icons, choose an icon here: https://fontawesome.com/v5.15/icons?d=gallery&p=2&m=free
# then, add an empty html.I() with the className from above
# see more here: https://github.com/facultyai/dash-bootstrap-components/issues/319#issuecomment-590478161
FONT_AWESOME_CSS = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"

app = dash.Dash(external_stylesheets=[FONT_AWESOME_CSS])
server = app.server
app.config.suppress_callback_exceptions = False