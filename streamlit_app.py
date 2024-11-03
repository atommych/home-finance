import re, datetime
import pandas as pd
import altair as alt
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from io import BytesIO
from pypdf import PdfReader


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

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

#df_gs = conn.read(
#    worksheet="Depesas",
#    ttl="10m",
#    usecols=[4, 5],
#    nrows=100,
#)
df_gs = conn.query("select distinct DESCRITIVO as description"                   
                    ", Classificação as category, count(1) as c "
                    " from Depesas group by 1,2 order by count(1) desc")

df_gs['row_number'] = df_gs.groupby('description')['c'].rank(method='first', ascending=False).astype(int)
df_gs['description'] = df_gs.description.apply(lambda a: re.sub(r"\s+", " ",re.sub(r"\d\d\d\d\s", "", a) ))
df_gs['row_number'] = df_gs.groupby('description')['c'].rank(method='first', ascending=False).astype(int)
df_gs = df_gs[df_gs.row_number==1][['description','category']]

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def import_pdf(text):
    table = text.split('\n')
    #print('Conta:'+ table[1])
    table[9] = table[8] + ' ' +  table[9]

    transacoes = []

    for row in table[9:]:
        saldo = re.sub(r".*(?<=\d\.\d\d\s)", "", row)
        data = re.sub(r" (?=\d+\.\d\d).*", "", row)
        valores = re.sub(r".*(?<!\d\d\.\d\d)\s", "", row)
        valor = valores.split(' ')[0]

        pattern = r"^\d+\.\d+ \d+\.\d+ (.*?) \d+\.\d+ \d+\.\d+$"
        match = re.search(pattern, row)
        if match:
            descricao = match.group(1)
            descricao = re.sub(r"\d\d\d\d\s", "", descricao)
            descricao = re.sub(r"\s+", " ", descricao)

        tipo_trans = descricao.split(' ')[0]
        descricao = ' '.join(descricao.split(' ')[1:])

        try:
            date_trx = datetime.date(2024, int(data.split('.')[0].strip()), int(data.split('.')[1]))
        except:
            pass
        try:
            trx_val = float(valor)
        except:
            pass
        trans_obj = {'month': date_trx.month,
                     'trx_type': tipo_trans,
                     'description': descricao,
                     'value': trx_val
                     }
        transacoes.append(trans_obj)
        
    return pd.DataFrame.from_dict(transacoes)


uploaded_files = st.file_uploader(
    "Selecione seus extratos em PDF", accept_multiple_files=True, type=['pdf']
)

text = ""
df_trx = pd.DataFrame()
if uploaded_files:
    for uploaded_file in uploaded_files:
        #bytes_data = uploaded_file.read()
        print("filename:" + uploaded_file.name)

        # To convert to a string based IO:
        pdfio = BytesIO(uploaded_file.getvalue())

        reader = PdfReader(pdfio)
        number_of_pages = len(reader.pages)
        for i in range(0,number_of_pages):
            page = reader.pages[i]
            text = text + page.extract_text()

        text = re.sub(r"[\S\s]*CONTA SIMPLES N.", "", text)
        text = re.sub(r"SALDO FINAL[\S\s]*", "", text)

        df_pdf = import_pdf(text)
        df_trx = pd.concat([df_trx, df_pdf], ignore_index=True)

    df_trx = df_trx.merge(df_gs, how='left', on='description')
    st.dataframe(df_trx, use_container_width=True)

    # Grouping data
    df_chart = df_trx.groupby(['category', 'month'])['value'].sum().reset_index()

    # Display the data as an Altair chart using `st.altair_chart`.
    chart = (
        alt.Chart(df_chart)
        .mark_line()
        .encode(
            x=alt.X("month:O", title="Mês"),  # Change to ordinal
            y=alt.Y("value:Q", title="Despesas"),  # Change to quantitative
            color=alt.Color("category:N", title="Categoria", scale=alt.Scale(scheme='category10')),
            #strokeDash=alt.StrokeDash("category:N")  # Optional: Different dash styles for categories
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)

    st.write(df_chart)

    #:chart_with_upwards_trend:
    #:money_with_wings:
    #:moneybag:

# Show a multiselect widget with the genres using `st.multiselect`.
#genres = st.multiselect(
#    "Categorias",
#    df_trx.categoria.unique(),
#    ["Alimentação", "Transporte", "Lazer", "Arrendamento", "Saúde", "Educação"],
#)
#
## Show a slider widget with the years using `st.slider`.
#years = st.slider("Years", 1986, 2006, (2000, 2016))
#
## Filter the dataframe based on the widget input and reshape it.
#df_filtered = df_trx[(df["genre"].isin(genres)) & (df["year"].between(years[0], years[1]))]
#df_reshaped = df_filtered.pivot_table(
#    index="year", columns="genre", values="gross", aggfunc="sum", fill_value=0
#)
#df_reshaped = df_reshaped.sort_values(by="year", ascending=False)
#
#
## Display the data as a table using `st.dataframe`.
#st.dataframe(
#    df_reshaped,
#    use_container_width=True,
#)