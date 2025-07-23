import streamlit as st

st.set_page_config(page_title="Consulta FIPE", page_icon="🚗")

st.title("Consulta de Carro - Tabela FIPE")

st.markdown("Preencha os dados do veículo para análise:")

with st.form("car_form"):
    ano_referencia = st.number_input(
        "Ano de Referência da Tabela FIPE",
        min_value=2000,
        max_value=2025,
        value=2023,
        step=1,
    )
    marca = st.selectbox(
        "Marca", ["GM - Chevrolet", "Volkswagen", "Fiat", "Ford", "Toyota"], index=0
    )
    modelo = st.text_input("Modelo")
    combustivel = st.selectbox(
        "Combustível", ["Gasolina", "Álcool", "Flex", "Diesel"], index=0
    )
    cambio = st.selectbox("Câmbio", ["Manual", "Automático"], index=0)
    motor = st.number_input(
        "Motorização (Ex: 1.0)",
        min_value=0.6,
        max_value=8.0,
        value=1.0,
        step=0.1,
        format="%.1f",
    )
    ano_fabricacao = st.number_input(
        "Ano de Fabricação", min_value=1980, max_value=2025, value=2019, step=1
    )

    submit = st.form_submit_button("Analisar")

if submit:
    st.success("Em análise")
