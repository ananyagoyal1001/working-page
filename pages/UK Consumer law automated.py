import requests
import streamlit as st
import numpy as np
from datetime import datetime, date, timedelta
import pandas as pd
from io import BytesIO
from deta import Deta
import altair as alt
import re

st.set_page_config(
    page_title="UK consumer law case tracker",
    page_icon="🇬🇧"
)

day = timedelta(days=1)


username = 'ananya001'
token = '89da193bf6348e04b4709ff2b891fcab85e00fdd'
host = 'eu.pythonanywhere.com'
file_path = 'home/ananya001/consumer_law/total2.xlsx' 
file_path2 = 'home/ananya001/consumer_law/total3.xlsx' 
response = requests.get(
    f'https://{host}/api/v0/user/{username}/files/path/{file_path}',
    headers={'Authorization': f'Token {token}'}
)
excel_data = BytesIO(response.content)
df = pd.read_excel(excel_data)

response2 = requests.get(
    f'https://{host}/api/v0/user/{username}/files/path/{file_path2}',
    headers={'Authorization': f'Token {token}'}
)
excel_data2 = BytesIO(response2.content)
df2 = pd.read_excel(excel_data2)
df2 = df2[['title', 'harm']]
df = pd.merge(df, df2, on='title', how='inner')

last_update_date = df['Last_update'].max()  
formatted_last_update_date = last_update_date.strftime('%d %B %Y')  

st.write(f'''
# UK Consumer Case Tracker

This is an automated overview of ongoing CMA consumer cases and the latest decisions! Stay informed about CMA consumer enforcement developments by exploring the tables below. Click on the case for direct access to the CMA webpage.
 
 
Updated: {formatted_last_update_date} (source: [CMA](https://www.gov.uk/cma-cases?case_type%5B%5D=consumer-enforcement)) | Contact: [Joost Dibbits](mailto:joost.dibbits@linklaters.com) or [Ananya Goyal](mailto:ananya.goyal@linklaters.com)

***
''')

#####
df['Case opened'] = pd.to_datetime(df['Case opened'])
df['case_closed'] = pd.to_datetime(df['case_closed'], errors='coerce')

st.sidebar.caption("Enter keywords or select sectors in search box below. The tables on the main page will filter the cases based on the sector.")
sector_list = pd.concat([df['Sector1'], df['Sector2'], df['Sector3']]).dropna().unique()
sector_list = sorted(sector_list)

# Multiselect widget for sectors
selected_sectors = st.sidebar.multiselect(
    'Sector',
    options=sector_list, 
    default=None,
    placeholder="Enter keywords"
)

# Filter DataFrame based on selected sectors from any of the three columns
if selected_sectors:
    df = df[df['Sector1'].isin(selected_sectors) | df['Sector2'].isin(selected_sectors) | df['Sector3'].isin(selected_sectors)]
else:
    pass

st.sidebar.caption("Select the Theory of Harm.")
harm_list = df['harm'].dropna().unique()
harm_list = sorted(harm_list)
selected_harms = st.sidebar.multiselect(
    'Theory of Harm',
    options=harm_list,
    default=None,
    placeholder="Select harm type"
)
if selected_harms:
    df = df[df['harm'].isin(selected_harms)]
    
# Assert to ensure certain columns are present
assert set(['title', 'public_timestamp']).issubset(df.columns)


######
df['Case opened'] = pd.to_datetime(df['Case opened'])

def get_financial_year(date):
    if date.month > 3:  # From April 1st
        return f"{date.year}-{str(date.year + 1)[2:]}"  # Changes here
    else:  # Until March 31st
        return f"{date.year - 1}-{str(date.year)[2:]}"  # Changes here

df['Financial year'] = df['Case opened'].apply(get_financial_year)
cases_per_year = df.groupby('Financial year').size().reset_index(name='Cases')
st.header('Cases')
categories_list = ["Cases Opened"]
categories_order = categories_list
categories_colors = ["#add8e6"] 

data = {
    "Financial year": cases_per_year['Financial year'],
    "Cases Opened": cases_per_year['Cases'],
}

df_for_plot = pd.DataFrame(data)

df_for_plot_melted = df_for_plot.melt("Financial year", var_name="Category", value_name="Cases")

max_value = df_for_plot_melted['Cases'].max() + 2
chart = alt.Chart(df_for_plot_melted).mark_bar(size=30).encode(
    x=alt.X('Financial year:N', title=None, axis=alt.Axis(labelAngle=0)),  
    y=alt.Y('Cases:Q', title=" ", 
            scale=alt.Scale(domain=(0, max_value)),
            axis=alt.Axis(tickCount=max_value, format='d')),  
    color=alt.Color('Category:N', scale=alt.Scale(domain=categories_order, range=categories_colors), legend=None),
    tooltip=['Financial year', 'Cases']
).properties(
    height=400
)

st.altair_chart(chart, use_container_width=True)


######
st.caption('Click on the button below to add more columns to the table. Hover over column names in the dataframe for further information.')

df2 = df[['title', 'Case opened', 'last_updated_date_extracted', 'case_closed', 'investigation_launch_date', 'days', 'Launch days', 'link', 'Compliance_review_commencement', 'most_recent_undertaking_link', 'most_recent_undertaking_date', 'undertaking_count', 'days_to_first_undertaking', 'advice', 'most_recent_open_letter_link', 'most_recent_press_release_link', 'harm']]
if df2.empty:
    st.write("There are no cases.")
else:
    df2 = df2.rename(columns={
    'title': 'Case',
    'days': 'Start days',
    'link': 'Case page',
    'Case opened': 'Start',
    'investigation_launch_date': 'Investigation launch',
    'case_closed': 'End',
    'last_updated_date_extracted': 'Last update',
    'most_recent_press_release_link': 'Press',
    'Compliance_review_commencement': 'Compliance', 
    'Launch days': 'Investigation days',
    'most_recent_undertaking_link' : 'Undertakings', 
    'undertaking_count' : 'No. of undertakings', 
    'most_recent_undertaking_date': 'Undertaking date', 
    'days_to_first_undertaking': 'Undertaking days', 
    'advice': 'Guidance', 
    'most_recent_open_letter_link': 'Open letter',
    'harm': 'TOH'
    
    })
    df2['No. of undertakings'] = df2['No. of undertakings'].replace(0, '')
    df2 = df2.sort_values(by='Last update', ascending=False)
    df2['Investigation launch'] = df2['Investigation launch'].dt.strftime('%d/%m/%Y')
    df2['Start'] = df2['Start'].dt.strftime('%d/%m/%Y')
    df2['End'] = df2['End'].dt.strftime('%d/%m/%Y')
    df2['Last update'] = pd.to_datetime(df2['Last update']).dt.strftime('%d/%m/%Y')
    df2['Investigation days'] = df2['Investigation days'].fillna('')
    df2['Investigation launch'] = df2['Investigation launch'].fillna('')
    df2['End'] = df2['End'].fillna('')
    df2['Investigation days'] = df2['Investigation days'].apply(lambda x: int(float(x)) if x != '' else x)
    df2['Start days'] = df2['Start days'].apply(lambda x: int(float(x)) if x != '' else x)
    df2['Undertakings'] = df2['Undertakings'].fillna('')
    df2['Undertaking date'] = df2['Undertaking date'].dt.strftime('%d/%m/%Y')
    df2['Undertaking date'] = df2['Undertaking date'].fillna('')
    df2['Undertaking days'] = df2['Undertaking days'].fillna('')
    df2['Undertaking days'] = df2['Undertaking days'].apply(lambda x: int(float(x)) if x != '' else x)
    df2['Open letter'] = df2['Open letter'].fillna('')
    df2['Compliance'] = df2['Compliance'].fillna('')
    df2['Press'] = df2['Press'].fillna('')
    df2['TOH'] = df2['TOH'].fillna('')
    df2 = df2.set_index('Case page')
    
    
    column_names = df2.columns.tolist() 
    preselected_columns = ['Case', 'Last update', 'Undertakings', 'TOH', 'Open letter', 'Compliance', 'Guidance']
    if 'selected_columns' not in st.session_state:
        st.session_state.selected_columns = preselected_columns

    with st.expander("Select columns"):
        updated_selected_columns = st.session_state.selected_columns.copy()
        for column in column_names:
            if st.checkbox(column, value=column in st.session_state.selected_columns, key=f'checkbox_{column}'):
                if column not in updated_selected_columns:
                    updated_selected_columns.append(column)
            else:
                if column in updated_selected_columns:
                    updated_selected_columns.remove(column)
        st.session_state.selected_columns = updated_selected_columns
    df2_selected = df2[st.session_state.selected_columns]
    st.data_editor(
    pd.DataFrame(df2_selected),
    column_config={
        "Case": st.column_config.Column(width="medium"),
        "Undertaking date": st.column_config.Column(help="The date for the last undertaking accepted by the CMA"),
        "TOH": st.column_config.Column(help="Theories of Harm"),
        "No. of undertakings": st.column_config.Column(help="The number of undertaking accepted by the CMA"),
        "Investigation days": st.column_config.Column(help="Calculated by finding the difference between case opened and launch of investigation date"),
        "Compliance": st.column_config.Column(help="Start date of compliance review"),
        "Guidance": st.column_config.Column(help="Subsequent guidance or advice"),
        "Start days": st.column_config.Column(help="The number of days for which the case has been open for"),
        "Undertaking days": st.column_config.Column(help="Calculated by finding the difference between case opening date and the first undertaking accepted"),
        "Press": st.column_config.LinkColumn(help="Most recent press release link",
            display_text='Yes',
            validate=r'(M.\d+)$'
        ),
        "Undertakings": st.column_config.LinkColumn(help="Most recent undertakings link",
            display_text='Yes',
            validate=r'(M.\d+)$'
        ),
        "Open letter": st.column_config.LinkColumn(
            display_text='Yes',
            validate=r'(M.\d+)$'
        ),
        "Case page": st.column_config.LinkColumn(
            display_text='URL',
            validate=r'(M.\d+)$'
        )
    }
    )
    st.caption('The **day** columns in the dataframe represent calendar days.')
    
if 'days_to_first_undertaking' in df.columns and pd.api.types.is_numeric_dtype(df['days_to_first_undertaking']):
    df2 = df[df['days_to_first_undertaking'] != 0]

    if df2.empty:
        st.write("There are no cases.")
    else:
        # Safe conversion and rounding
        mean_days = df2['days_to_first_undertaking'].mean()
        median_days = df2['days_to_first_undertaking'].median()
        
        if pd.notna(mean_days) and pd.notna(median_days):
            mean_days_to_first_undertaking = round(mean_days, 1)
            median_days_to_first_undertaking = round(median_days, 1)

            num_cases = df2['days_to_first_undertaking'].count()
        
            df_table = pd.DataFrame({
                'Metric': ['Average', 'Median'],
                'Calendar days': [str(mean_days_to_first_undertaking), str(median_days_to_first_undertaking)]
            })
            df_table.set_index('Metric', inplace=True)
            
            st.write('(b) Length of undertaking days in practice:')
            st.dataframe(df_table)
            
            st.caption(f"The average and median values in this table are based on **{num_cases}** cases. The undertaking days are calculated from the case opening date to the first undertakings accepted date.")

            st.caption(f"""
            
            Understanding the difference:
            
            - **Average duration**: This is the arithmetic mean of all {num_cases} cases in the dataset. It helps to set a realistic expectation.
            - **Median duration**: The median is the middle value when the undertaking days of all {num_cases} cases are sorted. It provides a 'middle' value, which can be especially valuable to avoid extreme outliers.
            
               
             """, unsafe_allow_html=True)
        else:
            st.write("Error in calculating mean or median.")
else:
    st.error("Error: 'days_to_first_undertaking' column is missing or not numeric.")
