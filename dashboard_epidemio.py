import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import webbrowser
import time

# Charger les données
file = "Epidemio2024hemato.xlsx"
df = pd.read_excel(file, header=5)
# df = df.fillna("Non testé")

# Initialiser l'application Dash avec suppress_callback_exceptions=True
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Styles personnalisés
styles = {
    "background": "#F5F5F5",  # Fond sobre (gris clair)
    "text": "#333333",  # Texte principal (gris foncé)
    "primary": "#0055BD",  # Couleur principale 1
    "primary2": "#4BACC6",  # Couleur principale 2
    "primary3": "#31849B",  # Couleur principale 3
    "secondary": "#D14D58",  # Couleur secondaire (accent)
}

# Layout de l'application
app.layout = html.Div(
    style={'fontFamily': 'Helvetica, sans-serif', "backgroundColor": styles["background"], "padding": "20px"},
    children=[
        html.H1(
            "Dashboard d'analyse des germes et antibiotiques",
            style={
                "textAlign": "center",
                "color": styles["primary"],
                "marginBottom": "20px",
            },
        ),
        # Onglets
        dcc.Tabs(
            id="tabs",
            value="tab-1",
            children=[
                dcc.Tab(
                    label="Occurrences des germes",
                    value="tab-1",
                    style={"backgroundColor": styles["primary2"], "color": "white"},
                    selected_style={
                        "backgroundColor": styles["primary"],
                        "color": "white",
                    },
                ),
                dcc.Tab(
                    label="Résultats des antibiotiques",
                    value="tab-2",
                    style={"backgroundColor": styles["primary2"], "color": "white"},
                    selected_style={
                        "backgroundColor": styles["primary"],
                        "color": "white",
                    },
                ),
            ],
        ),
        # Contenu des onglets
        html.Div(id="tabs-content", style={"marginTop": "20px"}),
    ],
)


# Callback pour gérer les onglets
@app.callback(Output("tabs-content", "children"), Input("tabs", "value"))
def render_tabs(tab):
    if tab == "tab-1":
        # Onglet 1 : Barplot des occurrences des germes
        germe_counts = df["Germe (libellé)"].value_counts().reset_index()
        germe_counts.columns = ["Germe", "Nombre d'occurrences"]

        fig1 = px.bar(
            germe_counts,
            x="Germe",
            y="Nombre d'occurrences",
            title="Nombre d'occurrences des germes identifiés",
            color_discrete_sequence=[
                styles["primary"]
            ],  # Couleur principale pour les barres
        )

        return html.Div([dcc.Graph(figure=fig1)])

    elif tab == "tab-2":
        # Onglet 2 : Graphique à barres des résultats des antibiotiques
        return html.Div(
            [
                # Conteneur pour la disposition en deux colonnes
                html.Div(
                    [
                        # Colonne de gauche : Filtres
                        html.Div(
                            [
                                html.Label(
                                    "Filtrer par Type de prélèvement :",
                                    style={"color": styles["text"]},
                                ),
                                dcc.Dropdown(
                                    id="service-dropdown",
                                    options=[
                                        {"label": "Tous", "value": "Tous"}
                                    ]  # Option pour ne pas filtrer
                                    + [
                                        {"label": service, "value": service}
                                        for service in df[
                                            "Service demandeur (libellé)"
                                        ].unique()
                                    ],
                                    value="Tous",  # Valeur par défaut
                                    style={
                                        "backgroundColor": "white",
                                        "color": styles["text"],
                                    },
                                ),
                                html.Label(
                                    "Filtrer par Type de prélèvement :",
                                    style={"color": styles["text"]},
                                ),
                                dcc.Dropdown(
                                    id="type-dropdown",
                                    options=[
                                        {"label": "Tous", "value": "Tous"}
                                    ]  # Option pour ne pas filtrer
                                    + [
                                        {"label": tp, "value": tp}
                                        for tp in df[
                                            "Type de prélèvement (libellé)"
                                        ].unique()
                                    ],
                                    value="Tous",  # Valeur par défaut
                                    style={
                                        "backgroundColor": "white",
                                        "color": styles["text"],
                                    },
                                ),
                                html.Label(
                                    "Filtrer par Germe :",
                                    style={"color": styles["text"]},
                                ),
                                dcc.Dropdown(
                                    id="germe-dropdown",
                                    options=[
                                        {"label": "Tous", "value": "Tous"}
                                    ]  # Option pour ne pas filtrer
                                    + [
                                        {"label": germe, "value": germe}
                                        for germe in df["Germe (libellé)"].unique()
                                    ],
                                    value="Tous",  # Valeur par défaut
                                    style={
                                        "backgroundColor": "white",
                                        "color": styles["text"],
                                    },
                                ),
                                html.Label(
                                    "Mode d'affichage :",
                                    style={"color": styles["text"]},
                                ),
                                dcc.RadioItems(
                                    id="barmode-radio",
                                    options=[
                                        {"label": "Groupé", "value": "group"},
                                        {"label": "Empilé", "value": "stack"},
                                    ],
                                    value="group",  # Valeur par défaut
                                    labelStyle={
                                        "display": "block",
                                        "color": styles["text"],
                                    },
                                ),
                            ],
                            style={
                                "width": "20%",
                                "display": "inline-block",
                                "verticalAlign": "top",
                                "padding": "20px",
                            },
                        ),
                        # Colonne de droite : Graphique
                        html.Div(
                            [dcc.Graph(id="antibio-graph")],
                            style={
                                "width": "75%",
                                "display": "inline-block",
                                "padding": "20px",
                            },
                        ),
                    ]
                )
            ]
        )


# Callback pour mettre à jour le graphique des antibiotiques
@app.callback(
    Output("antibio-graph", "figure"),
    [
        Input("service-dropdown", "value"),
        Input("type-dropdown", "value"),
        Input("germe-dropdown", "value"),
        Input("barmode-radio", "value"),
    ],
)
def update_antibio_graph(selected_service, selected_type, selected_germe, barmode):
    # Filtrer les données en fonction des sélections
    filtered_df = df.copy()

    # Filtrer par Service demandeur
    if selected_service != "Tous":
        filtered_df = filtered_df[
            filtered_df["Service demandeur (libellé)"] == selected_service
        ]

    # Filtrer par Type de prélèvement
    if selected_type != "Tous":
        filtered_df = filtered_df[
            filtered_df["Type de prélèvement (libellé)"] == selected_type
        ]

    # Filtrer par Germe
    if selected_germe != "Tous":
        filtered_df = filtered_df[filtered_df["Germe (libellé)"] == selected_germe]

    # Préparer les données pour le graphique
    antibio_columns = df.columns[10:]  # Colonnes des antibiotiques
    antibio_data = filtered_df[antibio_columns].melt(
        var_name="Antibiotique", value_name="Résultat"
    )

    # Agréger les données pour éviter les barres segmentées
    antibio_agg = (
        antibio_data.groupby(["Antibiotique", "Résultat"])
        .size()
        .reset_index(name="Count")
    )

    # Créer un graphique à barres avec les valeurs affichées à l'intérieur des barres
    fig2 = px.bar(
        antibio_agg,
        x="Antibiotique",
        y="Count",
        color="Résultat",
        title=f"Résultats des tests pour {selected_germe} (Type : {selected_type}, Service : {selected_service})",
        barmode=barmode,  # Utiliser le mode sélectionné
        text="Count",  # Afficher les valeurs des barres
        category_orders={
            "Résultat": ["NL", "S", "I", "R"]
        },  # Imposer l'ordre des résultats
        color_discrete_map={
            "NL": styles["secondary"],
            "S": styles["primary3"],
            "I": styles["primary2"],
            "R": styles["primary"],
        },  # Couleurs personnalisées
    )

    # Personnaliser l'affichage des valeurs
    fig2.update_traces(textposition="inside", textfont_size=12, textfont_color="white")

    # Ajuster la mise en page pour éviter que les textes ne se chevauchent
    fig2.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        plot_bgcolor=styles["background"],  # Fond du graphique
        paper_bgcolor=styles["background"],  # Fond de la zone du graphique
        font_color=styles["text"],  # Couleur du texte
    )

    return fig2


# Callback pour gérer la sélection "Tous" lors du clic sur la croix
@app.callback(
    [
        Output("type-dropdown", "value"),
        Output("germe-dropdown", "value"),
        Output("service-dropdown", "value"),
    ],
    [
        Input("type-dropdown", "value"),
        Input("germe-dropdown", "value"),
        Input("service-dropdown", "value"),
    ],
)

def handle_clearable(type_value, germe_value, service_value):
    # Si la valeur est None (croix cliquée), la remplacer par "Tous"
    if type_value is None:
        type_value = "Tous"
    if germe_value is None:
        germe_value = "Tous"
    if service_value is None:
        service_value = "Tous"

    return type_value, germe_value, service_value

# Ouvrir la page web au démarrage
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")  # Ouvre l'URL du dashboard

# Lancer l'application
if __name__ == '__main__':
    try:
        open_browser()  # Ouvre le navigateur avant de lancer le serveur
        app.run_server(debug=False)
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
    finally:
        print("Serveur arrêté.")
