import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

RED = "#D0021B"
GOLD = "#FFCF00"
GREEN = "#22C55E"
DARK = "#1C1C2E"
GREY = "#6B7280"
WHITE= "#FFFFFF"
BG = "#0F0F1A"
CARD = "#1A1A2E"
CARD2= "#16213E"

import os
for path in ["brentford_2021_2026.csv", os.path.join(os.path.dirname(__file__), "brentford_2021_2026.csv")]:
    if os.path.exists(path):
        df = pd.read_csv(path)
        break

df['date'] = pd.to_datetime(df['date'])
df['result_win'] = (df['result'] == 'W').astype(int)

MATCH_COLS = ['match_id','date','season','venue','competition', 'result','result_win','goals_for','goals_against', 'possession','total_shots','shots_on_target','corners','fouls_committed']
match = df.drop_duplicates('match_id')[MATCH_COLS].copy()
match['season_n'] = match['season'].map({'21/22':1,'22/23':2,'23/24':3,'24/25':4,'25/26':5})

SEASONS = ['21/22','22/23','23/24','24/25','25/26']
PLAYERS = sorted(df['player_name'].unique().tolist())
CURR_S = match['season'].value_counts().index[0]

CL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=WHITE, family="Barlow, sans-serif"),
    margin=dict(l=40,r=20,t=30,b=40),
    xaxis=dict(gridcolor="#2A2A3E", zerolinecolor="#2A2A3E"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    height=270
)

def card(children, extra=None):
    s = {"background":CARD,"borderRadius":"12px","padding":"20px", "border":"1px solid #2A2A3E","marginBottom":"16px"}
    if extra: s.update(extra)
    return html.Div(children, style=s)

def kpi_box(label, value, color=WHITE):
    return html.Div([
        html.Div(str(value), style={"fontSize":"1.9rem","fontWeight":"900","color":color,"lineHeight":"1"}),
        html.Div(label, style={"fontSize":"0.68rem","color":GREY,"marginTop":"4px", "textTransform":"uppercase","letterSpacing":"1px"})
    ], style={"textAlign":"center","padding":"14px 8px"})

def sec(text):
    return html.Div([
        html.Span(text, style={"fontSize":"0.82rem","fontWeight":"700","color":WHITE, "textTransform":"uppercase","letterSpacing":"2px"}),
        html.Hr(style={"borderColor":RED,"borderWidth":"2px","marginTop":"5px", "width":"36px","marginLeft":"0","opacity":"1"})
    ], style={"marginBottom":"12px"})

def row(*cols, gap="12px"):
    return html.Div(list(cols), style={"display":"flex","gap":gap})

def col_flex(children, flex=1):
    return html.Div(children, style={"flex":str(flex),"minWidth":"0"})

NAV_STYLE = {"color":WHITE,"padding":"11px 16px","borderRadius":"8px", "marginBottom":"4px","fontWeight":"600","fontSize":"0.85rem"}

sidebar = html.Div([
    html.Div([
        html.Div("🐝", style={"fontSize":"2.4rem"}),
        html.Div("BRENTFORD", style={"fontSize":"0.95rem","fontWeight":"900","color":WHITE,"letterSpacing":"3px","marginTop":"4px"}),
        html.Div("FC ANALYTICS", style={"fontSize":"0.6rem","color":GOLD,"letterSpacing":"4px"}),
        dbc.Button(
            "Hide menu",
            id="sidebar-hide",
            n_clicks=0,
            style={
                "marginTop": "14px",
                "background": CARD2,
                "border": "1px solid #2A2A3E",
                "color": WHITE,
                "borderRadius": "8px",
                "padding": "6px 10px",
                "fontWeight": "700",
                "fontSize": "0.72rem",
                "letterSpacing": "1px",
            },
        ),
    ], style={"textAlign":"center","padding":"28px 0 28px"}),
    html.Div("NAVIGATION", style={"fontSize":"0.62rem","color":GREY,"letterSpacing":"3px", "marginBottom":"10px","paddingLeft":"16px"}),
    dbc.Nav([
        dbc.NavLink(html.Span("Team Overview"), href="/", active="exact", style=NAV_STYLE),
        dbc.NavLink(html.Span("Player Profiling"), href="/player", active="exact", style=NAV_STYLE),
        dbc.NavLink(html.Span("Season Stats"), href="/season", active="exact", style=NAV_STYLE),
        dbc.NavLink(html.Span("Project Overview"), href="/project", active="exact", style=NAV_STYLE),
    ], vertical=True, pills=True),
    html.Div([
        html.Hr(style={"borderColor":"#2A2A3E","opacity":"1"}),
        html.Div("2021 — 2026", style={"color":WHITE,"fontWeight":"700","fontSize":"0.85rem"}),
        html.Div("208 matches · 81 players · 5 seasons", style={"color":GREY,"fontSize":"0.72rem","marginTop":"2px"})
    ], style={"position":"absolute","bottom":"24px","left":"16px","right":"16px"}),
], id="sidebar", style={"width":"210px","minHeight":"100vh","background":DARK,"position":"fixed", "top":0,"left":0,"zIndex":100,"borderRight":"1px solid #2A2A3E", "fontFamily":"Barlow, sans-serif"})

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

app = dash.Dash(
    __name__,
    assets_folder=ASSETS_PATH,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Barlow:wght@400;600;700;800;900&display=swap",
    ],
    suppress_callback_exceptions=True,
)
app.title = "Brentford FC Analytics"

def team_page_content():
    return html.Div([
        row(
            html.Div([
                html.Div(
                    "TEAM OVERVIEW",
                    style={
                        "fontSize": "1.7rem",
                        "fontWeight": "900",
                        "color": WHITE,
                        "letterSpacing": "2px",
                    },
                ),
                html.Div(
                    "All competitions · 5 seasons",
                    style={"color": GREY, "fontSize": "0.82rem", "marginTop": "2px"},
                ),
            ]),
            html.Div(
                dcc.Dropdown(
                    id="team-season",
                    clearable=False,
                    value="All",
                    options=[{"label": "All Seasons", "value": "All"}]
                    + [{"label": s, "value": s} for s in SEASONS],
                    style={
                        "width": "170px",
                        "backgroundColor": CARD,
                        "color": WHITE,
                        "border": "1px solid #2A2A3E",
                    },
                ),
                style={"alignSelf": "center", "marginLeft": "auto"},
            ),
            gap="12px",
        ),
        html.Br(),
        card(html.Div(id="team-kpis", style={"display": "grid", "gridTemplateColumns": "repeat(6,1fr)"})),
        row(
            col_flex(
                card([sec("Results per Season"), dcc.Graph(id="t-results", config={"displayModeBar": False})])
            ),
            col_flex(
                card([sec("Goals For vs Against"), dcc.Graph(id="t-goals", config={"displayModeBar": False})])
            ),
        ),
        row(
            col_flex(
                card(
                    [
                        sec("Home vs Away Win Rate"),
                        dcc.Graph(id="t-venue", config={"displayModeBar": False}),
                    ]
                )
            ),
            col_flex(
                card(
                    [
                        sec("Possession by Result"),
                        dcc.Graph(id="t-poss", config={"displayModeBar": False}),
                    ]
                )
            ),
        ),
    ])

def player_page_content():
    return html.Div([
        html.Div("PLAYER PROFILING", style={"fontSize":"1.7rem","fontWeight":"900","color":WHITE,"letterSpacing":"2px"}),
        html.Div("Individual stats · Radar · Season evolution", style={"color":GREY,"fontSize":"0.82rem","marginTop":"2px","marginBottom":"20px"}),
        card(row(
            html.Div([
                html.Div("SEASON", style={"fontSize":"0.65rem","color":GREY,"letterSpacing":"2px","marginBottom":"5px"}),
                dcc.Dropdown(
                    id="p-season",
                    options=[{"label":"All Seasons","value":"All"}]+[{"label":s,"value":s} for s in SEASONS],
                    value="All",
                    clearable=False,
                    style={"width":"170px","backgroundColor":CARD2,"color":WHITE,"border":"1px solid #2A2A3E"},
                ),
            ]),
            html.Div([
                html.Div("PLAYER", style={"fontSize":"0.65rem","color":GREY,"letterSpacing":"2px","marginBottom":"5px"}),
                dcc.Dropdown(id="p1", options=[{"label":p,"value":p} for p in PLAYERS], value=PLAYERS[0], clearable=False,
                    style={"width":"260px","backgroundColor":CARD2,"color":WHITE,"border":"1px solid #2A2A3E"})
            ]),
            html.Div([
                html.Div("COMPARE WITH", style={"fontSize":"0.65rem","color":GREY,"letterSpacing":"2px","marginBottom":"5px"}),
                dcc.Dropdown(id="p2", options=[{"label":"None","value":"None"}]+[{"label":p,"value":p} for p in PLAYERS], value="None", clearable=False,
                    style={"width":"260px","backgroundColor":CARD2,"color":WHITE,"border":"1px solid #2A2A3E"})
            ])
        )),
        html.Div(id="p-card-row"),
        row(
            col_flex(card([sec("Rating per Season"), dcc.Graph(id="p-rating", config={"displayModeBar":False})])),
            col_flex(card([sec("Career Stats Table"), html.Div(id="p-table")]))
        ),
    ])

def season_page_content():
    return html.Div([
        row(
            html.Div([
                html.Div("SEASON STATS", style={"fontSize":"1.7rem","fontWeight":"900","color":WHITE,"letterSpacing":"2px"}),
                html.Div("Match-by-match breakdown · Top performers", style={"color":GREY,"fontSize":"0.82rem","marginTop":"2px"})
            ]),
            html.Div(dcc.Dropdown(id="s-sel", clearable=False, value=CURR_S,
                options=[{"label":s,"value":s} for s in SEASONS],
                style={"width":"150px","backgroundColor":CARD,"color":WHITE,"border":"1px solid #2A2A3E"}),
                style={"alignSelf":"center", "marginLeft": "auto"})
        ),
        html.Br(),
        html.Div(id="s-kpis"),
        row(
            col_flex(card([sec("Cumulative Wins"), dcc.Graph(id="s-form", config={"displayModeBar":False})])),
            col_flex(card([sec("Goals Timeline"), dcc.Graph(id="s-goals", config={"displayModeBar":False})]))
        ),
        card([sec("Top Performers"), html.Div(id="s-top")]),
        card([sec("Match Results"), html.Div(id="s-tbl")]),
    ])

def project_page_content():
    matches_n = int(match['match_id'].nunique()) if 'match_id' in match.columns else int(len(match))
    players_n = int(df['player_name'].nunique()) if 'player_name' in df.columns else int(len(PLAYERS))
    seasons_n = int(match['season'].nunique()) if 'season' in match.columns else int(len(SEASONS))
    comps_n = int(match['competition'].nunique()) if 'competition' in match.columns else None

    dataset_line = f"{matches_n} matches · {players_n} players · {seasons_n} seasons"
    if comps_n is not None:
        dataset_line += f" · {comps_n} competitions"

    intro_md = (
        "This project focuses on analyzing Brentford FC’s performance over the period 2021 to 2026 "
        "using a dataset sourced from "
        "[Kaggle](https://kaggle.com/datasets/543718cc009af71cc9dc369fb12aa33f8c5369747315f1ccece2749811839f2a). "
        "The objective is to explore match results, team statistics, and key performance indicators "
        "in order to understand how the club has evolved across recent seasons.\n\n"
        "By applying data analysis and visualization techniques, we aim to transform raw football data "
        "into meaningful insights. This will help identify important trends, performance patterns, and "
        "the main factors influencing match outcomes over time."
    )

    dashboard_md = (
        "### Team Overview\n"
        "- Filter: Season (All Seasons or a single season)\n"
        "- KPIs: Matches, Wins, Win Rate, Avg GF, Avg GA, Clean Sheets\n"
        "- Charts: Results per Season · Goals For vs Against · Home vs Away Win Rate · Possession by Result\n\n"
        "### Player Profiling\n"
        "- Filter: Season + Player + optional Compare With\n"
        "- Cards: position, appearances, goals, assists, average rating\n"
        "- Radar: Shots · Key Passes · Tackles Won · Total Passes · Goals · Assists (scaled to squad max)\n"
        "- Trend + table: Rating per Season and career averages\n\n"
        "### Season Stats\n"
        "- Filter: Season\n"
        "- KPIs: Played, Wins/Draws/Losses, Goals For/Against, Clean Sheets, Win Rate\n"
        "- Charts: Cumulative Wins and Goals Timeline\n"
        "- Tables: Top Performers (G+A) and Match Results (sortable)\n\n"
        "### Navigation\n"
        "- Use the sidebar to switch tabs. Click **Hide menu** to collapse it, then use the ☰ button to show it again."
    )

    color_md = (
        "- **Green**: wins / win-rate\n"
        "- **Gold**: draws / highlights\n"
        "- **Red**: losses\n"
        "- **Grey / Dark**: goals against / neutral UI\n"
    )

    return html.Div([
        html.Div(
            "PROJECT OVERVIEW",
            style={"fontSize": "1.7rem", "fontWeight": "900", "color": WHITE, "letterSpacing": "2px"},
        ),
        html.Div(
            "About this dashboard",
            style={"color": GREY, "fontSize": "0.82rem", "marginTop": "2px", "marginBottom": "20px"},
        ),
        row(
            col_flex(
                card(
                    [
                        sec("Project"),
                        html.Div(
                            "🐝 Brentford FC Football Analytics Project",
                            style={"color": WHITE, "fontWeight": "900", "fontSize": "1.1rem"},
                        ),
                        html.Div(
                            "Academic Year 2025–2026",
                            style={"color": GREY, "fontSize": "0.82rem", "marginTop": "6px"},
                        ),
                        html.Div(
                            dataset_line,
                            style={"color": WHITE, "fontSize": "0.85rem", "marginTop": "10px", "fontWeight": "800"},
                        ),
                        html.Div(
                            "Data file: brentford_2021_2026.csv",
                            style={"color": GREY, "fontSize": "0.78rem", "marginTop": "4px"},
                        ),
                    ]
                )
            ),
            col_flex(
                card(
                    [
                        sec("Details"),
                        html.Table(
                            [
                                html.Tbody(
                                    [
                                        html.Tr(
                                            [
                                                html.Td(
                                                    "Student",
                                                    style={
                                                        "color": GREY,
                                                        "padding": "6px 8px",
                                                        "fontSize": "0.8rem",
                                                        "whiteSpace": "nowrap",
                                                    },
                                                ),
                                                html.Td(
                                                    "Ahmed Chakcha – Mohamed Ali Djemal",
                                                    style={
                                                        "color": WHITE,
                                                        "padding": "6px 8px",
                                                        "fontSize": "0.8rem",
                                                        "fontWeight": "700",
                                                    },
                                                ),
                                            ],
                                            style={"borderTop": "1px solid #2A2A3E"},
                                        ),
                                        html.Tr(
                                            [
                                                html.Td(
                                                    "Course",
                                                    style={
                                                        "color": GREY,
                                                        "padding": "6px 8px",
                                                        "fontSize": "0.8rem",
                                                        "whiteSpace": "nowrap",
                                                    },
                                                ),
                                                html.Td(
                                                    "Data Analysis",
                                                    style={
                                                        "color": WHITE,
                                                        "padding": "6px 8px",
                                                        "fontSize": "0.8rem",
                                                        "fontWeight": "700",
                                                    },
                                                ),
                                            ],
                                            style={"borderTop": "1px solid #2A2A3E"},
                                        ),
                                        html.Tr(
                                            [
                                                html.Td(
                                                    "Instructor",
                                                    style={
                                                        "color": GREY,
                                                        "padding": "6px 8px",
                                                        "fontSize": "0.8rem",
                                                        "whiteSpace": "nowrap",
                                                    },
                                                ),
                                                html.Td(
                                                    "Dr. Khalil Masmoudi",
                                                    style={
                                                        "color": WHITE,
                                                        "padding": "6px 8px",
                                                        "fontSize": "0.8rem",
                                                        "fontWeight": "700",
                                                    },
                                                ),
                                            ],
                                            style={"borderTop": "1px solid #2A2A3E"},
                                        ),
                                    ]
                                )
                            ],
                            style={"width": "100%"},
                        ),
                    ]
                )
            ),
            gap="12px",
        ),
        card(
            [
                sec("Introduction"),
                dcc.Markdown(
                    intro_md,
                    link_target="_blank",
                    style={"color": WHITE, "fontFamily": "Barlow, sans-serif", "lineHeight": "1.6"},
                ),
            ]
        ),
        card(
            [
                sec("What’s In The Dashboard"),
                dcc.Markdown(
                    dashboard_md,
                    link_target="_blank",
                    style={"color": WHITE, "fontFamily": "Barlow, sans-serif", "lineHeight": "1.6"},
                ),
            ]
        ),
        card(
            [
                sec("Color Guide"),
                dcc.Markdown(
                    color_md,
                    style={"color": WHITE, "fontFamily": "Barlow, sans-serif", "lineHeight": "1.6"},
                ),
            ]
        ),
    ])

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="sidebar-collapsed", data=False),
    dbc.Button(
        "☰",
        id="sidebar-show",
        n_clicks=0,
        style={
            "position": "fixed",
            "top": "16px",
            "left": "16px",
            "zIndex": 200,
            "display": "none",
            "background": CARD2,
            "border": "1px solid #2A2A3E",
            "color": WHITE,
            "borderRadius": "10px",
            "padding": "8px 11px",
            "fontWeight": "900",
            "lineHeight": "1",
        },
    ),
    sidebar,
    html.Div(id="page-content", style={"marginLeft":"234px","minHeight":"100vh","background":BG,"padding":"32px","fontFamily":"Barlow, sans-serif"})
], style={"background":BG})

POS = {'G':'Goalkeeper','D':'Defender','M':'Midfielder','F':'Forward'}

def get_pstats(p):
    return get_pstats_from(df, p)


def get_pstats_from(data, p):
    d = data[data['player_name']==p]
    if d.empty:
        return dict(
            apps=0,
            goals=0,
            assists=0,
            rating=0,
            minutes=0,
            shots=0,
            passes=0,
            tackles=0,
            kp=0,
            position="—",
            sr=pd.Series([None]*len(SEASONS), index=SEASONS),
        )
    return dict(
        apps=len(d), goals=int(d['goals'].sum()), assists=int(d['assists'].sum()),
        rating=d['rating'].mean(), minutes=d['minutes_played'].mean(),
        shots=d['shots'].mean(), passes=d['total_passes'].mean(),
        tackles=d['tackles_won'].mean(), kp=d['key_passes'].mean(),
        position=d['position'].iloc[0] if len(d) else "—",
        sr=d.groupby('season')['rating'].mean().reindex(SEASONS)
    )

def info_card(p, s, clr):
    return html.Div([
        html.Div(p.split()[-1].upper(), style={"fontSize":"1.9rem","fontWeight":"900","color":clr,"lineHeight":"1"}),
        html.Div(" ".join(p.split()[:-1]), style={"color":GREY,"fontSize":"0.85rem"}),
        html.Div(POS.get(s['position'],'—'), style={"color":GOLD,"fontSize":"0.7rem", "letterSpacing":"2px","marginTop":"4px","textTransform":"uppercase"}),
        html.Hr(style={"borderColor":"#2A2A3E","margin":"10px 0"}),
        html.Div([
            html.Div([html.Div(str(s['apps']), style={"color":clr,"fontWeight":"800","fontSize":"1.3rem"}), html.Div("Apps", style={"color":GREY,"fontSize":"0.68rem"})], style={"textAlign":"center"}),
            html.Div([html.Div(str(s['goals']), style={"color":clr,"fontWeight":"800","fontSize":"1.3rem"}), html.Div("Goals", style={"color":GREY,"fontSize":"0.68rem"})], style={"textAlign":"center"}),
            html.Div([html.Div(str(s['assists']),style={"color":clr,"fontWeight":"800","fontSize":"1.3rem"}), html.Div("Assists", style={"color":GREY,"fontSize":"0.68rem"})], style={"textAlign":"center"}),
            html.Div([html.Div(f"{s['rating']:.2f}", style={"color":clr,"fontWeight":"800","fontSize":"1.3rem"}), html.Div("Rating", style={"color":GREY,"fontSize":"0.68rem"})], style={"textAlign":"center"}),
        ], style={"display":"grid","gridTemplateColumns":"repeat(4,1fr)","gap":"4px"})
    ], style={"flex":"1","minWidth":"160px"})

@app.callback(Output("page-content","children"), Input("url","pathname"))
def route(pathname):
    if pathname == "/player":
        return player_page_content()
    elif pathname == "/season":
        return season_page_content()
    elif pathname == "/project":
        return project_page_content()
    else:
        return team_page_content()


@app.callback(
    Output("sidebar-collapsed", "data"),
    Input("sidebar-hide", "n_clicks"),
    Input("sidebar-show", "n_clicks"),
    State("sidebar-collapsed", "data"),
    prevent_initial_call=True,
)
def cb_sidebar_toggle(hide_clicks, show_clicks, collapsed):
    trigger = dash.callback_context.triggered_id
    if trigger == "sidebar-hide":
        return True
    if trigger == "sidebar-show":
        return False
    return collapsed


@app.callback(
    Output("sidebar", "style"),
    Output("page-content", "style"),
    Output("sidebar-show", "style"),
    Input("sidebar-collapsed", "data"),
)
def cb_sidebar_styles(collapsed):
    sidebar_style = {
        "width": "210px",
        "minHeight": "100vh",
        "background": DARK,
        "position": "fixed",
        "top": 0,
        "left": 0,
        "zIndex": 100,
        "borderRight": "1px solid #2A2A3E",
        "fontFamily": "Barlow, sans-serif",
    }
    content_style = {
        "marginLeft": "234px",
        "minHeight": "100vh",
        "background": BG,
        "padding": "32px",
        "fontFamily": "Barlow, sans-serif",
    }
    show_style = {
        "position": "fixed",
        "top": "16px",
        "left": "16px",
        "zIndex": 200,
        "display": "none",
        "background": CARD2,
        "border": "1px solid #2A2A3E",
        "color": WHITE,
        "borderRadius": "10px",
        "padding": "8px 11px",
        "fontWeight": "900",
        "lineHeight": "1",
    }

    if collapsed:
        sidebar_style["display"] = "none"
        content_style["marginLeft"] = "0px"
        content_style["paddingTop"] = "72px"
        content_style["paddingLeft"] = "72px"
        show_style["display"] = "block"

    return sidebar_style, content_style, show_style

@app.callback(
    [Output("team-kpis","children"), Output("t-results","figure"), Output("t-goals","figure"), Output("t-venue","figure"), Output("t-poss","figure")],
    Input("team-season","value")
)
def cb_team(season):
    d = match if season=="All" else match[match['season']==season]
    tot = len(d); w = int(d['result_win'].sum())
    kpis = [
        kpi_box("Matches", tot), kpi_box("Wins", w, GREEN), kpi_box("Win Rate", f"{w/tot*100:.0f}%", GOLD),
        kpi_box("Avg GF", f"{d['goals_for'].mean():.2f}", RED), kpi_box("Avg GA", f"{d['goals_against'].mean():.2f}", GREY),
        kpi_box("Clean Sheets",int((d['goals_against']==0).sum()), WHITE),
    ]
    res = d.groupby(['season','result']).size().unstack(fill_value=0).reindex(SEASONS)
    f1 = go.Figure()
    for col,clr,lbl in [('W',GREEN,'Win'),('D',GOLD,'Draw'),('L',RED,'Loss')]:
        if col in res.columns:
            f1.add_trace(go.Bar(name=lbl,x=res.index,y=res[col],marker_color=clr,marker_line_width=0))
    f1.update_layout(**CL, barmode='group')
    gg = d.groupby('season').agg(GF=('goals_for','mean'),GA=('goals_against','mean')).reindex(SEASONS)
    f2 = go.Figure([
        go.Scatter(x=gg.index,y=gg['GF'],mode='lines+markers',name='Goals For', line=dict(color=RED,width=3),marker=dict(size=8)),
        go.Scatter(x=gg.index,y=gg['GA'],mode='lines+markers',name='Goals Against', line=dict(color=GREY,width=3,dash='dash'),marker=dict(size=8))
    ])
    f2.update_layout(**CL)
    vn = d.groupby('venue')['result_win'].mean()*100
    f3 = go.Figure(go.Bar(x=vn.index,y=vn.values,marker_color=GREEN,marker_line_width=0, text=[f"{v:.1f}%" for v in vn.values],textposition='outside',textfont=dict(color=WHITE,size=12)))
    f3.update_layout(**CL,yaxis_range=[0,90])
    f4 = go.Figure([
        go.Box(y=d[d['result']==r]['possession'],name=lbl, marker_color=clr,line_color=clr,fillcolor=clr,opacity=0.7,boxmean=True)
        for r,clr,lbl in [('W',GREEN,'Win'),('D',GOLD,'Draw'),('L',RED,'Loss')]
    ])
    f4.update_layout(**CL)
    return kpis, f1, f2, f3, f4


@app.callback(
    Output("p1", "options"),
    Output("p1", "value"),
    Output("p2", "options"),
    Output("p2", "value"),
    Input("p-season", "value"),
    State("p1", "value"),
    State("p2", "value"),
)
def cb_player_dropdowns(season, p1_value, p2_value):
    base = df if season == "All" else df[df["season"] == season]
    players = sorted(base["player_name"].dropna().unique().tolist())

    if not players:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    p1_options = [{"label": p, "value": p} for p in players]
    p2_options = [{"label": "None", "value": "None"}] + p1_options

    if p1_value in players:
        new_p1 = p1_value
    else:
        new_p1 = players[0]

    if p2_value == "None" or p2_value in players:
        new_p2 = p2_value
    else:
        new_p2 = "None"

    return p1_options, new_p1, p2_options, new_p2

@app.callback(
    [Output("p-card-row","children"), Output("p-rating","figure"), Output("p-table","children")],
    Input("p-season","value"), Input("p1","value"), Input("p2","value")
)
def cb_player(season, p1, p2):
    base = df if season == "All" else df[df['season'] == season]
    s1 = get_pstats_from(base, p1)

    RCOLS = ['shots','key_passes','tackles_won','total_passes','goals','assists']
    CATS  = ['Shots','Key Passes','Tackles Won','Passes','Goals','Assists']

    g = (base.groupby('player_name')
         .agg(minutes=('minutes_played','sum'),
              shots=('shots','sum'),
              key_passes=('key_passes','sum'),
              tackles_won=('tackles_won','sum'),
              total_passes=('total_passes','sum'),
              goals=('goals','sum'),
              assists=('assists','sum')))

    mins = g['minutes']
    per90 = g[RCOLS].div(mins.where(mins > 0), axis=0).mul(90).fillna(0)
    pct = per90.rank(pct=True).mul(100).fillna(0)

    def hex_rgba(hex_color, alpha):
        h = hex_color.lstrip('#')
        r = int(h[0:2], 16)
        g_ = int(h[2:4], 16)
        b = int(h[4:6], 16)
        return f"rgba({r},{g_},{b},{alpha})"

    def radar_trace(p, clr, name):
        if p in pct.index:
            pct_vals = pct.loc[p, RCOLS].tolist()
            p90_vals = per90.loc[p, RCOLS].tolist()
        else:
            pct_vals = [0] * len(RCOLS)
            p90_vals = [0] * len(RCOLS)

        return go.Scatterpolar(
            r=pct_vals + [pct_vals[0]],
            theta=CATS + [CATS[0]],
            fill='toself',
            name=name,
            customdata=p90_vals + [p90_vals[0]],
            hovertemplate="%{theta}<br>%{r:.0f}th percentile<br>%{customdata:.2f} per 90<extra></extra>",
            fillcolor=hex_rgba(clr, 0.18),
            line=dict(color=clr, width=2),
        )

    fig_radar = go.Figure([radar_trace(p1, RED, p1.split()[-1])])
    if p2 != "None":
        fig_radar.add_trace(radar_trace(p2, GOLD, p2.split()[-1]))
    fig_radar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=WHITE, family="Barlow, sans-serif"), height=270,
        margin=dict(l=40,r=40,t=30,b=30),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0,100],
                tickvals=[0,20,40,60,80,100],
                gridcolor="#2A2A3E",
                color=GREY,
            ),
            angularaxis=dict(gridcolor="#2A2A3E", color=WHITE),
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    divider = html.Div(style={"width":"1px","background":"#2A2A3E","margin":"0 16px"})
    children = [
        info_card(p1, s1, RED),
        divider,
        col_flex([
            sec("Performance Radar (per 90 · percentile)"),
            dcc.Graph(figure=fig_radar, config={"displayModeBar":False}),
        ], flex=2),
    ]
    if p2 != "None":
        s2 = get_pstats_from(base, p2)
        children += [divider, info_card(p2, s2, GOLD)]
    card_row = card(html.Div(children, style={"display":"flex","alignItems":"flex-start"}))
    fr = go.Figure([go.Scatter(x=SEASONS, y=s1['sr'].values, mode='lines+markers', name=p1.split()[-1], line=dict(color=RED,width=3), marker=dict(size=8))])
    if p2 != "None":
        s2 = get_pstats_from(base, p2)
        fr.add_trace(go.Scatter(x=SEASONS, y=s2['sr'].values, mode='lines+markers', name=p2.split()[-1], line=dict(color=GOLD,width=3,dash='dot'), marker=dict(size=8)))
    fr.update_layout(**CL, yaxis=dict(range=[5.5,8.5],gridcolor="#2A2A3E",zerolinecolor="#2A2A3E"))
    def tbl(p, s, clr):
        rows = [("Appearances",str(s['apps'])),("Goals",str(s['goals'])),("Assists",str(s['assists'])),("Avg Rating",f"{s['rating']:.2f}"),("Avg Minutes",f"{s['minutes']:.0f}"),("Avg Shots",f"{s['shots']:.2f}"),("Avg Key Passes",f"{s['kp']:.2f}"),("Avg Tackles Won",f"{s['tackles']:.2f}")]
        return html.Table([
            html.Thead(html.Tr([html.Th("Stat", style={"color":GREY,"fontSize":"0.72rem","padding":"6px 10px","textAlign":"left"}), html.Th(p.split()[-1], style={"color":clr,"fontSize":"0.72rem","padding":"6px 10px","textAlign":"right","fontWeight":"700"})])),
            html.Tbody([html.Tr([html.Td(r[0], style={"color":GREY,"padding":"5px 10px","fontSize":"0.78rem"}), html.Td(r[1], style={"color":WHITE,"padding":"5px 10px","textAlign":"right","fontWeight":"600","fontSize":"0.78rem"})], style={"borderTop":"1px solid #2A2A3E"}) for r in rows])
        ], style={"width":"100%"})
    tbl_content = tbl(p1, s1, RED)
    if p2 != "None":
        tbl_content = html.Div([tbl(p1,s1,RED), html.Hr(style={"borderColor":"#2A2A3E"}), tbl(p2,get_pstats_from(base, p2),GOLD)])
    return card_row, fr, tbl_content

@app.callback(
    [Output("s-kpis","children"), Output("s-form","figure"), Output("s-goals","figure"), Output("s-top","children"), Output("s-tbl","children")],
    Input("s-sel","value")
)
def cb_season(season):
    sm = match[match['season']==season].sort_values('date')
    sp = df[df['season']==season]
    tot=len(sm); w=int(sm['result_win'].sum()); d_=int((sm['result']=='D').sum()); l=int((sm['result']=='L').sum())
    kpis = card(html.Div([
        kpi_box("Played",tot), kpi_box("Wins",w,GREEN), kpi_box("Draws",d_,GOLD), kpi_box("Losses",l,RED),
        kpi_box("Goals For",int(sm['goals_for'].sum()),RED), kpi_box("Goals Against",int(sm['goals_against'].sum()),GREY),
        kpi_box("Clean Sheets",int((sm['goals_against']==0).sum()),WHITE), kpi_box("Win Rate",f"{w/tot*100:.0f}%",GOLD),
    ], style={"display":"grid","gridTemplateColumns":"repeat(8,1fr)"}))
    sm2 = sm.copy(); sm2['cw'] = sm2['result_win'].cumsum()
    ff = go.Figure(go.Scatter(x=list(range(1,len(sm2)+1)), y=sm2['cw'], mode='lines+markers', fill='tozeroy', fillcolor='rgba(34,197,94,0.12)', line=dict(color=GREEN,width=3), marker=dict(size=7,color=GREEN)))
    ff.update_layout(**CL, xaxis_title="Match", yaxis_title="Cumulative Wins")
    fg = go.Figure([
        go.Bar(x=list(range(1,len(sm)+1)), y=sm['goals_for'], name='Goals For', marker_color=RED, marker_line_width=0),
        go.Bar(x=list(range(1,len(sm)+1)), y=-sm['goals_against'],name='Goals Against', marker_color=DARK, marker_line_width=0),
    ])
    fg.update_layout(**CL, barmode='overlay', xaxis_title="Match", yaxis_title="Goals")
    top = (sp.groupby('player_name').agg(G=('goals','sum'),A=('assists','sum'), R=('rating','mean'),Apps=('match_id','count')).assign(GI=lambda x:x.G+x.A).nlargest(5,'GI').reset_index())
    top_tbl = html.Table([
        html.Thead(html.Tr([html.Th(c, style={"color":GREY,"fontSize":"0.72rem","padding":"7px 12px", "textAlign":"left" if i==0 else "center"}) for i,c in enumerate(["Player","Apps","Goals","Assists","G+A","Avg Rating"])])),
        html.Tbody([html.Tr([
            html.Td(r['player_name'], style={"color":WHITE,"fontWeight":"700","padding":"7px 12px","fontSize":"0.82rem"}),
            html.Td(int(r['Apps']), style={"color":GREY,"textAlign":"center","padding":"7px","fontSize":"0.82rem"}),
            html.Td(int(r['G']), style={"color":RED,"textAlign":"center","fontWeight":"700","padding":"7px","fontSize":"0.82rem"}),
            html.Td(int(r['A']), style={"color":GOLD,"textAlign":"center","fontWeight":"700","padding":"7px","fontSize":"0.82rem"}),
            html.Td(int(r['GI']), style={"color":WHITE,"textAlign":"center","fontWeight":"800","padding":"7px","fontSize":"0.82rem"}),
            html.Td(f"{r['R']:.2f}", style={"color":WHITE,"textAlign":"center","padding":"7px","fontSize":"0.82rem"}),
        ], style={"borderTop":"1px solid #2A2A3E"}) for _,r in top.iterrows()])
    ], style={"width":"100%"})
    tbl_data = sm[['date','venue','competition','goals_for','goals_against','result','possession','total_shots']].copy()
    tbl_data['date'] = tbl_data['date'].dt.strftime('%d %b %Y')
    tbl_data['Score'] = tbl_data['goals_for'].astype(int).astype(str)+" — "+tbl_data['goals_against'].astype(int).astype(str)
    tbl_data = tbl_data[['date','venue','competition','Score','result','possession','total_shots']]
    tbl_data.columns = ['Date','Venue','Competition','Score','Result','Possession %','Shots']
    results_tbl = dash_table.DataTable(
        data=tbl_data.to_dict('records'), columns=[{"name":c,"id":c} for c in tbl_data.columns],
        style_table={"overflowX":"auto"},
        style_header={"backgroundColor":CARD2,"color":GREY,"fontWeight":"600","fontSize":"0.72rem", "border":"none","textTransform":"uppercase","letterSpacing":"1px"},
        style_cell={"backgroundColor":CARD,"color":WHITE,"fontSize":"0.8rem", "border":"1px solid #2A2A3E","padding":"7px 12px","fontFamily":"Barlow, sans-serif"},
        style_data_conditional=[
            {"if":{"filter_query":"{Result} = W"},"color":GREEN,"fontWeight":"700"},
            {"if":{"filter_query":"{Result} = L"},"color":RED,"fontWeight":"700"},
            {"if":{"filter_query":"{Result} = D"},"color":GOLD},
        ],
        page_size=15, sort_action="native"
    )
    return kpis, ff, fg, top_tbl, results_tbl

if __name__ == "__main__":
    app.run(debug=True, port=8050)
