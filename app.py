import streamlit as st
import numpy as np

remedies = st.Page("pages/Remedies.py", title="Remedies")
Consumer = st.Page("pages/UK Consumer law automated.py", title="Consumer Law")

# Organize dibs under the respective categories, including icons
pg = st.navigation(
    {
        "🥐 France": [remedies], "UK": [Consumer]
    }
)

pg.run()
