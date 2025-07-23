import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import LabelEncoder

import warnings

warnings.filterwarnings("ignore")

"""## Carga de Dados"""

# Carregando o dataset
csv_path = "dataset/fipe_cars.csv"
try:
    df = pd.read_csv(csv_path, encoding="latin1")
except FileNotFoundError:
    print(f"Arquivo '{csv_path}' não encontrado.")
    exit()


"""## Tratamento dos dados"""

# --- Verificação e Remoção de Linhas Duplicadas ---
print(f"Número de linhas antes de remover duplicatas: {len(df)}")

num_duplicates = df.duplicated().sum()
if num_duplicates > 0:
    print(f"Encontradas e removidas {num_duplicates} linhas duplicadas.")
    df.drop_duplicates(inplace=True)
else:
    print("Nenhuma linha duplicada encontrada.")

print(f"Número de linhas após remover duplicatas: {len(df)}")
print("-" * 30)

# Fuel e Gear
df_processed = df.copy()
df_processed = pd.get_dummies(
    df_processed, columns=["fuel", "gear"], prefix=["fuel", "gear"]
)

# Brand
le_brand = LabelEncoder()
df_processed["brand_encoded"] = le_brand.fit_transform(df_processed["brand"])
df_processed = df_processed.drop(["brand"], axis=1)

# Model
le_model = LabelEncoder()
df_processed["model_encoded"] = le_model.fit_transform(df_processed["model"])
df_processed = df_processed.drop(["model"], axis=1)

# Retirar colunas irrelevantes pro modelo
df_processed = df_processed.drop(
    ["fipe_code", "authentication", "month_of_reference"], axis=1
)

# Deletar colunas nulas caso existam
df_processed = df_processed.dropna()

print(df_processed)

"""## Modelagem"""

# --- Preparação dos Dados para o Modelo ---
X = df_processed.drop("avg_price_brl", axis=1)
y = df_processed["avg_price_brl"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Treinamento e Avaliação do Modelo usando DecisionTreeRegressor
dt_regressor = DecisionTreeRegressor(random_state=42)
dt_regressor.fit(X_train, y_train)
y_pred_dt_regressor = dt_regressor.predict(X_test)


# --- Criar um exemplo de carro para fazer a previsão ---
# Você pode alterar os valores neste dicionário para testar outros carros
car_example_data = {
    "year_of_reference": [2023],  # Ano de referência da tabela FIPE
    "brand": ["GM - Chevrolet"],
    "model": ["ONIX HATCH 1.0 12V Flex 5p Mec."],
    "fuel": ["Gasoline"],
    "gear": ["manual"],
    "engine_size": [1.0],
    "year_model": [2019],  # Ano de fabricação do carro
}

car_df = pd.DataFrame(car_example_data)

print("Dados do carro para previsão:")
print(car_df)
print("-" * 30)

# --- Aplicar as mesmas transformações dos dados de treino ---
# É CRUCIAL usar os encoders já treinados (.transform) e não treinar de novo (.fit_transform)
car_df["brand_encoded"] = le_brand.transform(car_df["brand"])
car_df["model_encoded"] = le_model.transform(car_df["model"])

# Aplicar One-Hot Encoding
car_df = pd.get_dummies(car_df, columns=["fuel", "gear"], prefix=["fuel", "gear"])
car_df = car_df.drop(["brand", "model"], axis=1)

# Alinhar as colunas do nosso exemplo com as colunas do modelo
# Isso garante que teremos todas as colunas do one-hot encoding, preenchendo com 0 as que não existem no exemplo
final_car_df = car_df.reindex(columns=X.columns, fill_value=0)


# --- Fazer a previsão ---
predicted_price = dt_regressor.predict(final_car_df)

print(f"Preço PREVISTO para o carro: R$ {predicted_price[0]:,.2f}")
