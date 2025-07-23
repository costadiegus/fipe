import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from model_utils import CarPriceModel
import os

# Configuração da página
st.set_page_config(
    page_title="Predição de Preços de Carros FIPE", page_icon="🚗", layout="wide"
)


# Função para inicializar o banco de dados
def init_database():
    """Inicializa o banco de dados SQLite"""
    conn = sqlite3.connect("car_predictions.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            year_of_reference INTEGER,
            brand TEXT,
            model TEXT,
            fuel TEXT,
            gear TEXT,
            engine_size REAL,
            year_model INTEGER,
            predicted_price REAL,
            is_good_prediction BOOLEAN,
            user_corrected_price REAL,
            user_comments TEXT
        )
    """
    )

    conn.commit()
    conn.close()


# Função para salvar predição no banco
def save_prediction(prediction_data):
    """Salva a predição no banco de dados"""
    conn = sqlite3.connect("car_predictions.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO predictions (
            timestamp, year_of_reference, brand, model, fuel, gear, 
            engine_size, year_model, predicted_price, is_good_prediction, 
            user_corrected_price, user_comments
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        prediction_data,
    )

    conn.commit()
    conn.close()


# Função para carregar histórico de predições
def load_prediction_history():
    """Carrega o histórico de predições"""
    conn = sqlite3.connect("car_predictions.db")
    df = pd.read_sql_query("SELECT * FROM predictions ORDER BY timestamp DESC", conn)
    conn.close()
    return df


# Função para exibir a tela de entrada de dados
def show_input_screen(car_model):
    """Tela principal para entrada de dados do veículo"""
    st.title("🚗 Predição de Preços de Carros FIPE")
    st.markdown("### Informe os dados do veículo para obter a predição de preço")
    st.markdown("---")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.header("📋 Informações do Veículo")

        # Obter valores únicos
        unique_values = car_model.get_unique_values()

        # Campos de entrada
        year_of_reference = st.selectbox(
            "🗓️ Ano de Referência da Tabela FIPE",
            options=[2021, 2022, 2023, 2024],
            index=2,
        )

        brand = st.selectbox("🏭 Marca", options=unique_values["brands"])

        # Atualizar modelos baseado na marca selecionada
        if brand:
            models = car_model.get_models_by_brand(brand)
            model = st.selectbox("🚙 Modelo", options=models)
        else:
            model = None
            st.warning("⚠️ Selecione uma marca para ver os modelos disponíveis")

        col_fuel, col_gear = st.columns(2)

        with col_fuel:
            fuel = st.selectbox("⛽ Combustível", options=unique_values["fuels"])

        with col_gear:
            gear = st.selectbox("⚙️ Câmbio", options=unique_values["gears"])

        col_engine, col_year = st.columns(2)

        with col_engine:
            engine_size = st.number_input(
                "🔧 Tamanho do Motor (L)",
                min_value=unique_values["engine_range"][0],
                max_value=unique_values["engine_range"][1],
                value=1.0,
                step=0.1,
                format="%.1f",
            )

        with col_year:
            year_model = st.number_input(
                "📅 Ano do Modelo",
                min_value=unique_values["year_range"][0],
                max_value=unique_values["year_range"][1],
                value=2020,
                step=1,
            )

        st.markdown("---")

        # Botão de predição
        _, col_btn2, _ = st.columns([1, 2, 1])
        with col_btn2:
            predict_button = st.button(
                "🔮 Fazer Predição",
                type="primary",
                use_container_width=True,
                disabled=not model,
            )

        if predict_button and model:
            with st.spinner("🤖 Processando predição..."):
                predicted_price = car_model.predict_price(
                    year_of_reference, brand, model, fuel, gear, engine_size, year_model
                )

            if predicted_price is not None:
                # Armazenar dados da predição na sessão
                st.session_state.prediction_data = {
                    "timestamp": datetime.now().isoformat(),
                    "year_of_reference": year_of_reference,
                    "brand": brand,
                    "model": model,
                    "fuel": fuel,
                    "gear": gear,
                    "engine_size": engine_size,
                    "year_model": year_model,
                    "predicted_price": predicted_price,
                }

                # Mudar para a tela de resultado
                st.session_state.current_screen = "result"
                st.rerun()
            else:
                st.error("❌ Erro na predição. Verifique os dados inseridos.")

    with col2:
        st.header("📊 Estatísticas Rápidas")

        # Carregar histórico para estatísticas
        history_df = load_prediction_history()

        if len(history_df) > 0:
            st.metric("📈 Total de Predições", len(history_df))

            good_predictions = history_df["is_good_prediction"].sum()
            accuracy_pct = (good_predictions / len(history_df)) * 100
            st.metric("✅ Taxa de Acerto", f"{accuracy_pct:.1f}%")

            avg_predicted = history_df["predicted_price"].mean()
            st.metric("💰 Preço Médio", f"R$ {avg_predicted:,.0f}")

            if st.button("📋 Ver Histórico Completo"):
                st.session_state.current_screen = "history"
                st.rerun()
        else:
            st.info("🚀 Faça sua primeira predição!")


# Função para exibir a tela de resultado
def show_result_screen():
    """Tela de resultado da predição com avaliação"""
    st.title("🎯 Resultado da Predição")
    st.markdown("---")

    prediction_data = st.session_state.prediction_data

    # Exibir dados informados e resultado
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📋 Dados Informados")

        # Card com os dados do veículo
        with st.container():
            st.markdown(
                """
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            """,
                unsafe_allow_html=True,
            )

            col_info1, col_info2 = st.columns(2)

            with col_info1:
                st.markdown(
                    f"**🗓️ Ano de Referência:** {prediction_data['year_of_reference']}"
                )
                st.markdown(f"**🏭 Marca:** {prediction_data['brand']}")
                st.markdown(f"**🚙 Modelo:** {prediction_data['model']}")
                st.markdown(f"**📅 Ano do Modelo:** {prediction_data['year_model']}")

            with col_info2:
                st.markdown(f"**⛽ Combustível:** {prediction_data['fuel']}")
                st.markdown(f"**⚙️ Câmbio:** {prediction_data['gear']}")
                st.markdown(f"**🔧 Motor:** {prediction_data['engine_size']} L")

            st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.header("💰 Preço Previsto")

        # Card com o resultado
        predicted_price = prediction_data["predicted_price"]
        st.markdown(
            f"""
        <div style='background-color: #d4edda; padding: 30px; border-radius: 15px; text-align: center; border: 2px solid #28a745;'>
            <h2 style='color: #155724; margin: 0;'>R$ {predicted_price:,.2f}</h2>
            <p style='color: #155724; margin: 5px 0 0 0;'>Valor estimado FIPE</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Seção de avaliação
    st.header("📊 Avalie a Predição")

    col1, col2 = st.columns(2)

    with col1:
        is_good_prediction = st.radio(
            "🤔 A predição foi boa?",
            options=[True, False],
            format_func=lambda x: (
                "✅ Sim, foi uma boa predição"
                if x
                else "❌ Não, não foi uma boa predição"
            ),
        )

    with col2:
        user_corrected_price = st.number_input(
            "💡 Se desejar, informe um valor mais acurado (R$):",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f",
        )

    user_comments = st.text_area(
        "💬 Comentários adicionais (opcional):",
        placeholder="Deixe aqui suas observações sobre a predição...",
        height=100,
    )

    # Botões de ação
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Salvar Avaliação", type="primary", use_container_width=True):
            # Preparar dados para salvar
            prediction_data_tuple = (
                prediction_data["timestamp"],
                prediction_data["year_of_reference"],
                prediction_data["brand"],
                prediction_data["model"],
                prediction_data["fuel"],
                prediction_data["gear"],
                prediction_data["engine_size"],
                prediction_data["year_model"],
                prediction_data["predicted_price"],
                is_good_prediction,
                user_corrected_price if user_corrected_price > 0 else None,
                user_comments if user_comments.strip() else None,
            )

            save_prediction(prediction_data_tuple)
            st.success("✅ Avaliação salva com sucesso!")
            st.balloons()

    with col2:
        if st.button("🔄 Nova Consulta", type="secondary", use_container_width=True):
            # Limpar dados da sessão e voltar para tela inicial
            if "prediction_data" in st.session_state:
                del st.session_state.prediction_data
            st.session_state.current_screen = "input"
            st.rerun()

    with col3:
        if st.button("📋 Ver Histórico", type="secondary", use_container_width=True):
            st.session_state.current_screen = "history"
            st.rerun()


# Função para exibir o histórico
def show_history_screen():
    """Tela de histórico de predições"""
    st.title("📈 Histórico de Predições")
    st.markdown("---")

    # Botões de navegação
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("🔙 Voltar", use_container_width=True):
            st.session_state.current_screen = "input"
            st.rerun()

    with col2:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.rerun()

    # Carregar e exibir histórico
    history_df = load_prediction_history()

    if len(history_df) > 0:
        # Estatísticas detalhadas
        st.header("📊 Estatísticas Gerais")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📈 Total de Predições", len(history_df))

        with col2:
            good_predictions = history_df["is_good_prediction"].sum()
            accuracy_pct = (good_predictions / len(history_df)) * 100
            st.metric("✅ Taxa de Acerto", f"{accuracy_pct:.1f}%")

        with col3:
            avg_predicted = history_df["predicted_price"].mean()
            st.metric("💰 Preço Médio Previsto", f"R$ {avg_predicted:,.0f}")

        with col4:
            corrected_count = history_df["user_corrected_price"].notna().sum()
            st.metric("💡 Correções de Usuário", corrected_count)

        st.markdown("---")
        st.header("📋 Histórico Detalhado")

        # Tabela de histórico
        st.dataframe(
            history_df[
                [
                    "timestamp",
                    "brand",
                    "model",
                    "year_model",
                    "predicted_price",
                    "is_good_prediction",
                    "user_corrected_price",
                    "user_comments",
                ]
            ],
            use_container_width=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn(
                    "📅 Data/Hora", format="DD/MM/YYYY HH:mm"
                ),
                "brand": "🏭 Marca",
                "model": "🚙 Modelo",
                "year_model": "📅 Ano",
                "predicted_price": st.column_config.NumberColumn(
                    "💰 Preço Previsto", format="R$ %.0f"
                ),
                "is_good_prediction": st.column_config.CheckboxColumn(
                    "✅ Boa Predição"
                ),
                "user_corrected_price": st.column_config.NumberColumn(
                    "💡 Correção do Usuário", format="R$ %.0f"
                ),
                "user_comments": "💬 Comentários",
            },
        )
    else:
        st.info("📭 Nenhuma predição foi feita ainda.")

        if st.button("🚀 Fazer Primeira Predição", type="primary"):
            st.session_state.current_screen = "input"
            st.rerun()


# Função principal
def main():
    # Inicializar banco de dados
    init_database()

    # Inicializar estado da sessão
    if "current_screen" not in st.session_state:
        st.session_state.current_screen = "input"

    # Verificar se o modelo existe, se não, treinar
    model_path = "car_price_model.pkl"
    if not os.path.exists(model_path):
        with st.spinner("🤖 Treinando modelo... Isso pode demorar alguns minutos."):
            from model_utils import ensure_model_trained

            if not ensure_model_trained():
                st.error("❌ Erro ao treinar o modelo. Verifique se o dataset existe.")
                return

    # Carregar modelo
    @st.cache_resource
    def load_model():
        car_model = CarPriceModel()
        if car_model.load_and_preprocess_data():
            car_model.load_model(model_path)
            return car_model
        return None

    car_model = load_model()

    if car_model is None:
        st.error("❌ Erro ao carregar o modelo ou dataset.")
        return

    # Roteamento de telas
    if st.session_state.current_screen == "input":
        show_input_screen(car_model)
    elif st.session_state.current_screen == "result":
        show_result_screen()
    elif st.session_state.current_screen == "history":
        show_history_screen()


if __name__ == "__main__":
    main()
