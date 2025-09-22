# -*- coding: utf-8 -*-
"""
Aplicação principal em Streamlit para demonstrar Persistência Poliglota e Geoprocessamento.
Versão final utilizando Folium para maior compatibilidade de mapas e st.session_state para persistência.
"""
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pymongo.errors import ConnectionFailure

# Importando os módulos
import db_sqlite
import db_mongo
import geoprocessamento

# --- Configuração da Página ---
st.set_page_config(
    page_title="GeoApp | Persistência Poliglota",
    page_icon="🗺️",
    layout="wide"
)


# --- Funções Auxiliares ---
def popular_bancos_se_necessario():
    """Adiciona dados iniciais aos bancos de dados se eles estiverem vazios."""
    if not db_sqlite.listar_paises():
        db_sqlite.inserir_pais("Brasil")
    if not db_sqlite.listar_estados():
        id_brasil = db_sqlite.listar_paises()[0][0]
        db_sqlite.inserir_estado("Paraíba", "PB", id_brasil)
        db_sqlite.inserir_estado("Pernambuco", "PE", id_brasil)
    if not db_sqlite.listar_cidades():
        id_paraiba = db_sqlite.listar_estados()[0][0]
        id_pernambuco = db_sqlite.listar_estados()[1][0]
        db_sqlite.inserir_cidade("João Pessoa", id_paraiba)
        db_sqlite.inserir_cidade("Campina Grande", id_paraiba)
        db_sqlite.inserir_cidade("Recife", id_pernambuco)
    if db_mongo.contar_locais() == 0:
        locais_iniciais = [
            {"nome": "Praça da Independência", "cidade": "João Pessoa", "coords": [-34.8610, -7.1153],
             "desc": "Ponto turístico."},
            {"nome": "Parque Solon de Lucena", "cidade": "João Pessoa", "coords": [-34.8785, -7.1197],
             "desc": "Principal parque."},
            {"nome": "Açude Velho", "cidade": "Campina Grande", "coords": [-35.8810, -7.2220],
             "desc": "Cartão postal."},
            {"nome": "Marco Zero", "cidade": "Recife", "coords": [-34.8708, -8.0628], "desc": "Ponto de fundação."}
        ]
        for local in locais_iniciais:
            db_mongo.inserir_local(local["nome"], local["cidade"], local["coords"][1], local["coords"][0],
                                   local["desc"])


# --- Inicialização ---
MONGO_CONECTADO = False
try:
    db_sqlite.criar_tabelas()
    db_mongo.criar_indice_geoespacial()
    popular_bancos_se_necessario()
    MONGO_CONECTADO = True
except ConnectionFailure as e:
    st.error(str(e))
    st.warning("Funcionalidades do MongoDB estão desativadas.")

# --- Interface (Sidebar) ---
with st.sidebar:
    st.title("🗺️ GeoApp")
    st.info("Demonstração de Persistência Poliglota (SQLite + MongoDB) e Geoprocessamento.")
    paginas = ["Visualização e Consulta", "Cadastro de Dados", "Consulta por Proximidade"]
    if not MONGO_CONECTADO: paginas = []
    pagina_selecionada = st.radio("Navegue pelas seções:", paginas)
    st.markdown("---")
    st.markdown("### Autores\n- **Daniel Warella Pitsch**: 29831695.\n- **Elder de Oliveira Tavares**: 30581818.\n- **Wellington Gadelha de Sousa**: 30517851.")

# --- Página de Visualização ---
if MONGO_CONECTADO and pagina_selecionada == "Visualização e Consulta":
    st.header("📍 Visualização de Pontos de Interesse")
    lista_cidades = [c[1] for c in db_sqlite.listar_cidades()]
    cidade_selecionada = st.selectbox("Selecione uma cidade:", options=lista_cidades)

    if cidade_selecionada:
        locais = db_mongo.buscar_locais_por_cidade(cidade_selecionada)
        if locais:
            dados_mapa = [{"nome": l["nome_local"], "latitude": float(l["coordenadas"]["coordinates"][1]),
                           "longitude": float(l["coordenadas"]["coordinates"][0]), "descricao": l["descricao"]} for l in
                          locais]
            df = pd.DataFrame(dados_mapa)
            st.subheader(f"Locais em {cidade_selecionada}")
            map_center = [df["latitude"].mean(), df["longitude"].mean()]
            m = folium.Map(location=map_center, zoom_start=14)
            for idx, row in df.iterrows():
                folium.Marker(location=[row['latitude'], row['longitude']],
                              popup=f"<b>{row['nome']}</b><br>{row['descricao']}", tooltip=row['nome']).add_to(m)
            st_folium(m, width=725, height=500)
            with st.expander("Ver detalhes em tabela"):
                st.dataframe(df)
        else:
            st.info(f"Nenhum local cadastrado para {cidade_selecionada}.")

# --- Página de Cadastro ---
elif MONGO_CONECTADO and pagina_selecionada == "Cadastro de Dados":
    st.header("📝 Cadastro de Novos Dados")
    # (O código desta página não precisa de alterações)
    tab1, tab2 = st.tabs(["Cadastrar Cidade/Estado", "Cadastrar Local de Interesse"])
    with tab1:
        st.subheader("Cadastrar Nova Cidade")
        with st.form("form_cidade", clear_on_submit=True):
            nome_cidade = st.text_input("Nome da Cidade")
            estados = db_sqlite.listar_estados()
            mapa_estados = {f"{e[1]} - {e[2]}": e[0] for e in estados}
            estado_selecionado_str = st.selectbox("Selecione o Estado", options=mapa_estados.keys())
            submit_cidade = st.form_submit_button("Salvar Cidade")
            if submit_cidade and nome_cidade and estado_selecionado_str:
                id_estado = mapa_estados[estado_selecionado_str]
                db_sqlite.inserir_cidade(nome_cidade, id_estado)
                st.success(f"Cidade '{nome_cidade}' cadastrada com sucesso!")
            elif submit_cidade:
                st.error("Por favor, preencha todos os campos.")
    with tab2:
        st.subheader("Cadastrar Novo Local de Interesse")
        with st.form("form_local", clear_on_submit=True):
            nome_local = st.text_input("Nome do Local")
            cidades = db_sqlite.listar_cidades()
            cidade_local = st.selectbox("Selecione a Cidade", options=[c[1] for c in cidades])
            descricao_local = st.text_area("Descrição do Local")
            st.markdown("##### Coordenadas Geográficas")
            col_lat, col_lon = st.columns(2)
            lat_local = col_lat.number_input("Latitude", format="%.6f", value=0.0)
            lon_local = col_lon.number_input("Longitude", format="%.6f", value=0.0)
            submit_local = st.form_submit_button("Salvar Local")
            if submit_local:
                if nome_local and cidade_local and lat_local != 0.0 and lon_local != 0.0:
                    db_mongo.inserir_local(nome_local, cidade_local, lat_local, lon_local, descricao_local)
                    st.success(f"Local '{nome_local}' cadastrado com sucesso!")
                else:
                    st.error("Preencha o nome do local, cidade e coordenadas.")

# --- Página de Proximidade ---
elif MONGO_CONECTADO and pagina_selecionada == "Consulta por Proximidade":
    st.header("🔍 Consulta por Proximidade")

    # Inicializa o estado da sessão para guardar os resultados da busca
    if 'resultado_proximidade' not in st.session_state:
        st.session_state.resultado_proximidade = None
    if 'parametros_busca' not in st.session_state:
        st.session_state.parametros_busca = {}

    with st.form("form_proximidade"):
        lat_central = st.number_input("Latitude do ponto central", format="%.6f", value=-7.1197)
        lon_central = st.number_input("Longitude do ponto central", format="%.6f", value=-34.8785)
        raio_km = st.slider("Raio de busca (em Km)", min_value=1, max_value=100, value=10)
        submit_proximidade = st.form_submit_button("Buscar Locais Próximos")

        if submit_proximidade:
            # Ao submeter o formulário, busca os dados e guarda no st.session_state
            locais_proximos = geoprocessamento.encontrar_locais_proximos(lat_central, lon_central, raio_km * 1000)
            st.session_state.parametros_busca = {'lat': lat_central, 'lon': lon_central, 'raio': raio_km}

            if locais_proximos:
                dados_prox = [{"nome": l["nome_local"], "cidade": l["cidade"],
                               "latitude": float(l['coordenadas']['coordinates'][1]),
                               "longitude": float(l['coordenadas']['coordinates'][0])} for l in locais_proximos]
                st.session_state.resultado_proximidade = pd.DataFrame(dados_prox)
            else:
                st.session_state.resultado_proximidade = pd.DataFrame()  # Guarda um DataFrame vazio se nada for encontrado

    # --- LÓGICA DE EXIBIÇÃO (FORA DO FORMULÁRIO) ---
    # Esta parte do código lê os resultados do st.session_state e exibe o mapa.
    # Como está fora do formulário, o mapa não some ao recarregar a página.
    if st.session_state.resultado_proximidade is not None:
        df_resultado = st.session_state.resultado_proximidade
        params = st.session_state.parametros_busca

        if not df_resultado.empty:
            st.info(f"Encontrados {len(df_resultado)} locais em um raio de {params['raio']} Km.")

            # Cria o mapa com base nos resultados guardados
            m_prox = folium.Map(location=[params['lat'], params['lon']], zoom_start=12)
            folium.Circle(
                location=[params['lat'], params['lon']],
                radius=params['raio'] * 1000,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.15
            ).add_to(m_prox)

            for idx, row in df_resultado.iterrows():
                folium.Marker(location=[row['latitude'], row['longitude']], popup=row['nome'],
                              tooltip=row['nome']).add_to(m_prox)

            st_folium(m_prox, width=725, height=500, key="mapa_proximidade")
            with st.expander("Ver detalhes da busca"):
                st.dataframe(df_resultado)
        else:
            # Mostra o aviso apenas se uma busca foi realmente feita (params não está vazio)
            if params:
                st.warning("Nenhum local encontrado no raio de busca especificado.")

elif not MONGO_CONECTADO:
    st.header("Bem-vindo ao GeoApp")
    st.info("A aplicação não pôde se conectar ao banco de dados MongoDB.")

