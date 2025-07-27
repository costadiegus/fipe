import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import warnings

warnings.filterwarnings("ignore")


class CarPriceModel:
    def __init__(self):
        self.df = None
        self.model = None
        self.le_brand = None
        self.le_model = None
        self.X_columns = None
        self.model_trained = False

    def load_and_preprocess_data(self, csv_path="app/dataset/fipe_cars.csv"):
        """Carrega e preprocessa os dados"""
        try:
            self.df = pd.read_csv(csv_path, encoding="latin1")
            print(f"Dataset carregado com {len(self.df)} registros")
        except FileNotFoundError:
            print(f"Arquivo '{csv_path}' não encontrado.")
            return False

        # Remover duplicatas
        num_duplicates = self.df.duplicated().sum()
        if num_duplicates > 0:
            self.df.drop_duplicates(inplace=True)
            print(f"Removidas {num_duplicates} linhas duplicadas.")

        return True

    def train_model(self):
        """Treina o modelo de previsão"""
        if self.df is None:
            return False

        # Preprocessamento
        df_processed = self.df.copy()

        # One-Hot Encoding para fuel e gear
        df_processed = pd.get_dummies(
            df_processed, columns=["fuel", "gear"], prefix=["fuel", "gear"]
        )

        # Label Encoding para brand
        self.le_brand = LabelEncoder()
        df_processed["brand_encoded"] = self.le_brand.fit_transform(
            df_processed["brand"]
        )
        df_processed = df_processed.drop(["brand"], axis=1)

        # Label Encoding para model
        self.le_model = LabelEncoder()
        df_processed["model_encoded"] = self.le_model.fit_transform(
            df_processed["model"]
        )
        df_processed = df_processed.drop(["model"], axis=1)

        # Remover colunas irrelevantes
        df_processed = df_processed.drop(
            ["fipe_code", "authentication", "month_of_reference"], axis=1
        )

        # Remover valores nulos
        df_processed = df_processed.dropna()

        # Separar features e target
        X = df_processed.drop("avg_price_brl", axis=1)
        y = df_processed["avg_price_brl"]

        # Salvar as colunas para usar na predição
        self.X_columns = X.columns

        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Treinar modelo
        self.model = DecisionTreeRegressor(random_state=42)
        # self.model = RandomForestRegressor(
        #    random_state=42, max_features="sqrt", n_estimators=30
        # )
        self.model.fit(X_train, y_train)

        # Avaliar modelo
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        print(f"Score treino: {train_score:.4f}")
        print(f"Score teste: {test_score:.4f}")

        self.model_trained = True
        return True

    def get_unique_values(self):
        """Retorna valores únicos para os campos de entrada"""
        if self.df is None:
            return {}

        return {
            "brands": sorted(self.df["brand"].unique()),
            "fuels": sorted(self.df["fuel"].unique()),
            "gears": sorted(self.df["gear"].unique()),
            "year_range": (
                int(self.df["year_model"].min()),
                int(self.df["year_model"].max()),
            ),
            "engine_range": (
                float(self.df["engine_size"].min()),
                float(self.df["engine_size"].max()),
            ),
        }

    def get_models_by_brand(self, brand):
        """Retorna modelos disponíveis para uma marca específica"""
        if self.df is None:
            return []
        return sorted(self.df[self.df["brand"] == brand]["model"].unique())

    def predict_price(
        self, year_of_reference, brand, model, fuel, gear, engine_size, year_model
    ):
        """Faz a predição do preço do carro"""
        if not self.model_trained:
            return None

        # Criar DataFrame com os dados de entrada
        car_data = {
            "year_of_reference": [year_of_reference],
            "brand": [brand],
            "model": [model],
            "fuel": [fuel],
            "gear": [gear],
            "engine_size": [engine_size],
            "year_model": [year_model],
        }

        car_df = pd.DataFrame(car_data)

        try:
            # Aplicar transformações
            car_df["brand_encoded"] = self.le_brand.transform(car_df["brand"])
            car_df["model_encoded"] = self.le_model.transform(car_df["model"])

            # One-Hot Encoding
            car_df = pd.get_dummies(
                car_df, columns=["fuel", "gear"], prefix=["fuel", "gear"]
            )
            car_df = car_df.drop(["brand", "model"], axis=1)

            # Alinhar colunas
            final_car_df = car_df.reindex(columns=self.X_columns, fill_value=0)

            # Fazer predição
            predicted_price = self.model.predict(final_car_df)

            return predicted_price[0]

        except ValueError as e:
            print(f"Erro na predição: {e}")
            return None

    def save_model(self, filepath="car_price_model.pkl"):
        """Salva o modelo treinado"""
        if self.model_trained:
            model_data = {
                "model": self.model,
                "le_brand": self.le_brand,
                "le_model": self.le_model,
                "X_columns": self.X_columns,
            }
            with open(filepath, "wb") as f:
                pickle.dump(model_data, f)
            return True
        return False

    def load_model(self, filepath="car_price_model.pkl"):
        """Carrega um modelo salvo"""
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                model_data = pickle.load(f)

            self.model = model_data["model"]
            self.le_brand = model_data["le_brand"]
            self.le_model = model_data["le_model"]
            self.X_columns = model_data["X_columns"]
            self.model_trained = True
            return True
        return False


# Função para treinar e salvar o modelo se necessário
def ensure_model_trained():
    """Garante que o modelo está treinado e salvo"""
    model_path = "car_price_model.pkl"

    if os.path.exists(model_path):
        print("Modelo já existe, carregando...")
        return True

    print("Treinando novo modelo...")
    car_model = CarPriceModel()

    if not car_model.load_and_preprocess_data():
        return False

    if not car_model.train_model():
        return False

    car_model.save_model(model_path)
    print("Modelo treinado e salvo com sucesso!")
    return True


if __name__ == "__main__":
    ensure_model_trained()
