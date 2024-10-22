import pandas as pd
import streamlit as st

st.set_page_config(
    page_title = "TabularQA"
)

st.sidebar.success("Select a page above.")

st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)

st.markdown("<h1>🎉<em>Welcome to TabularQA!</em></h1>", unsafe_allow_html=True)
st.markdown("")
st.markdown("""
<style>
.text {
    text-align: justify;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="text">
TabularQA is your go-to solution for effortlessly exploring and 
analyzing your data, regardless of your technical background. 
With our intuitive interface and lightning-fast response times, 
you'll be uncovering insights within seconds, making data analysis a breeze for everyone.
</div>
""", unsafe_allow_html=True)

st.markdown("")
st.markdown("**Query CSV Data:**")

st.markdown("""
<div class="text" style="margin-top: -10px;">
Upload your CSV files and instantly unlock the power of natural language queries. 
Whether you're a data scientist, business analyst, or simply curious, 
TabularQA allows you to explore your data intuitively. From simple inquiries to complex visualizations, 
TabularQA transforms your data exploration experience.
</div>
""", unsafe_allow_html=True)

st.markdown("")
st.markdown("**Query Database:**")

st.markdown("""
<div class="text" style="margin-top: -10px;">
Have a database in .db format? TabularQA makes querying a breeze. 
Simply upload your .db file, select the tables you're interested in, 
and start asking questions in natural language. Say goodbye to complex SQL queries and 
hello to a more intuitive way of interacting with your data.
</div>
""", unsafe_allow_html=True)

st.markdown('')
st.markdown("")
st.markdown("**Key Features:**")
st.write("""
- **Natural Language Interface:** Communicate with your data using everyday language.
- **Visualizations:** Gain insights through interactive visualizations generated from your queries.
- **CSV and Database Support:** Whether your data is in CSV files or databases, TabularQA has you covered.
- **User-Friendly:** No coding required. TabularQA is designed with ease of use in mind, allowing anyone to harness the power of their data.
""")
st.markdown('')

st.markdown("""
<div class="text">
At TabularQA, we understand the importance of seamless data analysis. 
That's why we assume your uploaded files are *error-free*, 
allowing you to focus on exploring your data without worrying about potential issues.
</div>
""", unsafe_allow_html=True)

st.markdown('')
st.markdown("""
<div class="text">
Unlock the potential of your data with TabularQA today and start making informed decisions with confidence!
</div>
""", unsafe_allow_html=True)

