import altair as alt
import pandas as pd
import streamlit as st
from io import BytesIO
from pypdf import PdfReader
import re


# Show the page title and description.
st.set_page_config(page_title="Home Finances", page_icon=":bar_chart:")
st.title(":bar_chart: Home Finances")
st.write(
    """
    Este aplicativo permite visualizar os dados do seu [Extrato Bancário Digital](#).
    Os gastos são categorizados em: Alimentação, Transporte, Lazer, Arrendamento, Saúde e Educação. 
    Apenas faça o upload do seu extrato bancário e explore a aplicação!
    """
)

uploaded_files = st.file_uploader(
    "Selecione seus extratos em PDF", accept_multiple_files=True, type=['pdf']
)


# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_extrato(text):
    table = text.split('\n')
    #print('Conta:'+ table[1])
    table[9] = table[8] + ' ' +  table[9]

    transacoes = []

    for row in table[9:]:
        saldo = re.sub(r".*(?<=\d\.\d\d\s)", "", row)
        data = re.sub(r" (?=\d+\.\d\d).*", "", row)
        compra_valor =  re.sub(r"(?=\d\.\d\d).*(?<=\s\d\.\d\d\s)", "", row)
        valores = re.sub(r".*(?<!\d\d\.\d\d)\s", "", compra_valor)
        valor = valores.split(' ')[0]
        pattern = r"^\d+\.\d+ \d+\.\d+ (.*?) \d+\.\d+ \d+\.\d+$"
        match = re.search(pattern, row)
        descricao=''
        if match:
            descricao = match.group(1)
        tipo_trans = descricao.split(' ')[0]
        descricao = ' '.join(descricao.split(' ')[1:])

        trans_obj = {'data':data,
                     'tipo_trans': tipo_trans,
                     'descricao': descricao,
                     'valor' : valor }

        transacoes.append(trans_obj)
        
    return pd.DataFrame.from_dict(transacoes)


text = ""
if uploaded_files is not None:
    for uploaded_file in uploaded_files:
        #bytes_data = uploaded_file.read()
        st.write("filename:", uploaded_file.name)

        # To convert to a string based IO:
        pdfio = BytesIO(uploaded_file.getvalue())

        reader = PdfReader(pdfio)
        number_of_pages = len(reader.pages)
        for i in range(0,number_of_pages):
            page = reader.pages[i]
            text = text + page.extract_text()

        text = re.sub(r"[\S\s]*CONTA SIMPLES N.", "", text)
        text = re.sub(r"SALDO FINAL[\S\s]*", "", text)

        df_trx = load_extrato(text)
        st.write(df_trx)
        #st.write(text)



@st.cache_data
def load_data():
    df = pd.read_csv("data/movies_genres_summary.csv")
    return df


df = load_data()

# Show a multiselect widget with the genres using `st.multiselect`.
genres = st.multiselect(
    "Genres",
    df.genre.unique(),
    ["Action", "Adventure", "Biography", "Comedy", "Drama", "Horror"],
)

# Show a slider widget with the years using `st.slider`.
years = st.slider("Years", 1986, 2006, (2000, 2016))

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[(df["genre"].isin(genres)) & (df["year"].between(years[0], years[1]))]
df_reshaped = df_filtered.pivot_table(
    index="year", columns="genre", values="gross", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="year", ascending=False)


# Display the data as a table using `st.dataframe`.
st.dataframe(
    df_reshaped,
    use_container_width=True,
)

# Display the data as an Altair chart using `st.altair_chart`.
df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="year", var_name="genre", value_name="gross"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("year:N", title="Year"),
        y=alt.Y("gross:Q", title="Gross earnings ($)"),
        color="genre:N",
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)
