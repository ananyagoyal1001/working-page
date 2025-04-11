import streamlit as st
import numpy as np

remedies = st.Page("working-page/Remedies.py", title="Remedies")
Consumer = st.Page("working-page/UK Consumer law automated.py", title="Consumer Law")
Legal = st.Page("working-page/legal.py", title="Legal page")

# Organize dibs under the respective categories, including icons
pg = st.navigation(
    {
        "🥐 France": [remedies], "UK": [Consumer, Legal]
    }
)

pg.run()
