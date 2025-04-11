import requests
import streamlit as st
import numpy as np
from datetime import datetime, date, timedelta
import pandas as pd
from io import BytesIO
from deta import Deta
import altair as alt
import re
#st.set_page_config(
    #page_title="FSR case tracker",
    #page_icon="🇪🇺"
#)

st.balloons()


day = timedelta(days=1)


username = 'ananya001'
token = '89da193bf6348e04b4709ff2b891fcab85e00fdd'
host = 'eu.pythonanywhere.com'
file_path = 'home/ananya001/Legal_data/2025-02-21T13-54_export.csv' 
response = requests.get(
    f'https://{host}/api/v0/user/{username}/files/path/{file_path}',
    headers={'Authorization': f'Token {token}'}
)
csv_data = BytesIO(response.content)
df = pd.read_csv(csv_data)


st.write(f'''
# Remedies
This is an automated overview of remedy cases! Stay informed about case developments by exploring the tables below. Click on the URL for direct access to EUMR's webpage.
 
 
Last updated:  (source: [EU](https://competition-cases.ec.europa.eu/search)) | Contact: [Joost Dibbits](mailto:joost.dibbits@linklaters.com) or [Ananya Goyal](mailto:ananya.goyal@linklaters.com)
***
''')
#####

st.sidebar.header('User input features')
st.sidebar.header('NACE')
st.sidebar.caption("Enter keywords or NACE codes in search box below. The tables on the main page will show all cases of which the NACE codes contain any of the entered search terms.")
nace_categories = df['Nace'].dropna().unique().tolist()
search_term_nace = st.sidebar.text_input('Search NACE codes', placeholder='Enter keywords')
if search_term_nace:
    search_terms = search_term_nace.split()  # Split the search_term by spaces
    search_regex = '|'.join(search_terms)  # Join terms with regex OR
    df = df[df['Nace'].str.contains(search_regex, case=False, na=False)]


st.sidebar.markdown('For an overview of NACE codes, click here.', unsafe_allow_html=True)
st.sidebar.header('Parties')
st.sidebar.caption("Enter party names in search box below. The tables on the main page will show all cases pertaining to the party.")
nace_categories = df['Parties'].dropna().unique().tolist()
search_term_parties = st.sidebar.text_input('Search party names', placeholder='Enter party names')
if search_term_parties:
    search_terms = search_term_parties.split()  # Split the search_term by spaces
    search_regex = '|'.join(search_terms)  # Join terms with regex OR
    df = df[df['Parties'].str.contains(search_regex, case=False, na=False)]

#####
options = ["Phase 1", "Phase 2"]

# Segmented control with multi-selection
selected_procedures = st.segmented_control(
    "Select Phase:", 
    options, 
    selection_mode="multi",
    default=options
    
)

options2 = ["Structural", "Behavioural", "Hybrid"]

# Segmented control with multi-selection
selected_procedure = st.segmented_control(
    "Select Type:", 
    options2, 
    selection_mode="multi",
    default=options2
    
)

# Ensure selected_procedures is not empty before filtering
df2 = df[
    (df['Procedure_type'].isin(selected_procedures)) &
    (df['Structural_behavioral'].isin(selected_procedure))
]

if df2.empty:
    st.write("There are no remedy cases, please change the search criteria")
else:
    df2 = df2.rename(columns={'Case_link': 'Case', 'End_date': 'Decision', 'Structural_behavioral': 'Type', 'Remedy_type': 'Remedy', 'Buyer_approval': 'Buyer', 'Procedure_type': 'Phase'})
    df2['Decision'] = pd.to_datetime(df2['Decision'])
    df2 = df2.sort_values(by='Decision', ascending=False)
    df2['Decision'] = df2['Decision'].dt.strftime('%d/%m/%Y')
    df2 = df2[['Case', 'Parties', 'Phase', 'Decision', 'Type', 'Remedy', 'Buyer']] 
    df2 = df2.set_index('Case')     
    st.data_editor(
        pd.DataFrame(df2),
        column_config={
            "Parties": st.column_config.Column(width="medium"),
            "Case": st.column_config.LinkColumn(
                display_text=r'(M.\d+)$',
                validate=r'(M.\d+)$',
            )  
        },
        disabled=True 
    )
