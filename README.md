# Aplicação de Predição de Preços de Carros FIPE

Esta aplicação utiliza um modelo de Machine Learning (DecisionTreeRegressor) para prever preços de carros baseado na tabela FIPE.

## Funcionalidades

- ✅ Interface web intuitiva com Streamlit
- 🔮 Predição de preços baseada em características do veículo
- 📊 Sistema de avaliação das predições pelos usuários
- 💾 Banco de dados SQLite local para armazenar histórico
- 📈 Visualização de estatísticas e histórico de predições
- 🔄 Correção de valores pelos usuários

## Requisitos

- Python 3.8+
- Bibliotecas listadas em `requirements.txt`

## Como usar

### Opção 1: Execução automática (Windows)
```bash
run_app.bat
```

### Opção 2: Execução manual
```bash
# Instalar dependências
pip install -r requirements.txt

# Treinar modelo (primeira execução)
python model_utils.py

# Executar aplicação
streamlit run app.py
```

## Estrutura do Projeto

```
app/
├── app.py              # Aplicação principal Streamlit
├── model_utils.py      # Utilitários do modelo ML
├── ml.py              # Script original de treinamento
├── requirements.txt   # Dependências Python
├── run_app.bat       # Script de execução automática
├── dataset/
│   └── fipe_cars.csv # Dataset FIPE
└── car_predictions.db # Banco SQLite (criado automaticamente)
```

## Como funciona

1. **Entrada de Dados**: O usuário informa:
   - Ano de referência da tabela FIPE
   - Marca e modelo do veículo
   - Tipo de combustível
   - Tipo de câmbio
   - Tamanho do motor
   - Ano do modelo

2. **Predição**: O modelo treinado retorna o preço estimado

3. **Avaliação**: O usuário pode:
   - Avaliar se a predição foi boa ou não
   - Informar um valor mais acurado (opcional)
   - Deixar comentários

4. **Armazenamento**: Todos os dados são salvos no banco SQLite local

5. **Histórico**: Visualização de todas as predições anteriores com estatísticas

## Banco de Dados

O sistema cria automaticamente um banco SQLite (`car_predictions.db`) com a seguinte estrutura:

- **id**: Identificador único
- **timestamp**: Data/hora da predição
- **year_of_reference**: Ano de referência FIPE
- **brand**: Marca do veículo
- **model**: Modelo do veículo
- **fuel**: Tipo de combustível
- **gear**: Tipo de câmbio
- **engine_size**: Tamanho do motor
- **year_model**: Ano do modelo
- **predicted_price**: Preço previsto pelo modelo
- **is_good_prediction**: Se o usuário considerou a predição boa
- **user_corrected_price**: Valor corrigido pelo usuário (opcional)
- **user_comments**: Comentários do usuário (opcional)

## Melhorias Futuras

- [ ] Gráficos de análise de desempenho do modelo
- [ ] Exportação de dados para Excel/CSV
- [ ] Sistema de retreinamento automático
- [ ] Comparação com preços reais de mercado
- [ ] API REST para integração com outros sistemas
