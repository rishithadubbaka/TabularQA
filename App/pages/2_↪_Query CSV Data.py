import streamlit as st 
import pandas as pd
import numpy as np
import openai
import re
import toml


config = toml.load('/secrets.toml')
openai_key = config['open_ai_key']['OPENAI_API_KEY']

openai.api_key = openai_key

def generate_code(dtypes, user_query):
    
    prompt = "As a Python expert, you're tasked with providing Python code based on the user query. Assume the existence of a DataFrame stored in the variable `df`. This DataFrame contains the following columns and data types:\n\n"
    prompt += "\n".join([f"{col}: {dtype}" for col, dtype in dtypes.items()])
    prompt += "\nGiven this DataFrame structure, write Python code snippets to perform various operations requested by the user, such as filtering data, calculating statistics, or transforming the DataFrame.\n\nUser Query: " + user_query + "\n\nPython Code:"
    
    prompt += "\nAdditional Information:\n"
    prompt += "- Always refer to the DataFrame variable as `df` to ensure consistency and avoid errors.\n"
    prompt += "- Ensure that operations are appropriate for the data types of df columns to prevent type errors.\n"
    prompt += "- Write code that is efficient both in terms of time and memory usage. Avoid unnecessary iterations and leverage built-in DataFrame methods or vectorized operations whenever possible.\n"
    prompt += "- Write code that is easy to understand and maintain by using descriptive variable names, comments, and consistent formatting.\n"
    prompt += "- Consider the scalability of the code for larger datasets, avoiding operations that may become inefficient as the dataset size increases.\n"
    prompt += "- Do not import any external packages or libraries other than pandas or numpy.\n"
    prompt += "- Import pandas as pd and numpy as np.\n"
    prompt += "- Always display the output to the uesr query.\n"
    prompt += "- Do not use print function to display the output instead use st.write() function."
    
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=1500,
        temperature=0,
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    
    response = completion.choices[0].message['content'].strip()
    if "```" in response:
        pattern = r'```(.*?)```'
        code = re.search(pattern, response, re.DOTALL)
        extracted_code = code.group(1)
        extracted_code = extracted_code.replace('python', '')
        return extracted_code
    else:
        return response


def create_plot(user_input,cols):
    
    prompt = 'Write code in Python using Plotly to address the following request: {} ' \
            'Use df that has the following columns: {}.' \
            'Do not use column names which are not present in the df.'\
            'Do not use animation_group argument.' \
            'only code with no import statements and the data ' \
            'has been already loaded in a df variable. ' \
            'Name the figure object as fig.'\
            'Ensure that you do not call the `show()` method on the figure object.'.format(user_input, cols)


    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=1500,
        temperature=0,
        messages=[
            {"role": "user", "content": prompt},
        ]
    )

    response = completion.choices[0].message['content'].strip()
    if "```" in response:
        pattern = r'```(.*?)```'
        code = re.search(pattern, response, re.DOTALL)
        response = code.group(1)
        response = response.replace('python', '')
    
    response = response.replace('fig.show()', '')
    
    exec(response, globals())
    return fig, response

uploaded_file = st.file_uploader("Upload a CSV file", type=['csv'])

if uploaded_file is not None:
    
    data = pd.read_csv(uploaded_file)
    df = data.reset_index(drop=True)#reset index
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(' ', '_')#replace spaces in the columns
    
    object_cols = [col for col, dtype in df.dtypes.items() if dtype == 'object']
    
    def is_numeric(value):
        try:
            pd.to_numeric(value)
            return True
        except ValueError:
            return False
        
    for col in object_cols:
        all_numeric = df[col].apply(is_numeric).all()
        if all_numeric:
                df[col] = pd.to_numeric(df[col])
    
    
    def is_datetime(value, date_formats):
        try:
            pd.to_datetime(value, format=date_formats)
            return True
        except (ValueError, TypeError):
            return False 

    def parse_date_column(df, col, date_formats):
        try:
            df[col] = pd.to_datetime(df[col], format=date_formats)
        except (ValueError, TypeError):
            pass

    def detect_and_parse_datetime_columns(df, object_cols, date_formats):
        for col in object_cols:
            if is_datetime(df[col], date_formats):
                parse_date_column(df, col, date_formats)
                
    date_formats = [
    '%Y-%m-%d',
    '%d-%m-%Y',
    '%m-%d-%Y',
    '%Y/%m/%d',
    '%d/%m/%Y',
    '%m/%d/%Y',
    '%Y.%m.%d',
    '%d.%m.%Y',
    '%m.%d.%Y',
    '%Y%m%d',
    '%d%m%Y',
    '%m%d%Y',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M',
    '%Y-%m-%d %I:%M %p',
    '%Y-%m-%d %I:%M%p',
    '%Y-%m-%d %H:%M:%S.%f'
    ]    
           
    detect_and_parse_datetime_columns(df, object_cols, date_formats)
    
    st.write(df)
    
    dtypes = df.dtypes
    # Generate query output
    st.markdown("#### Enter your query:")
    user_query1 = st.text_area("1",label_visibility="collapsed")
    show_code1 = st.checkbox("Show Python Code")

    if st.button("Generate"):
        if user_query1:
            with st.spinner("Generating response..."):
                _code = generate_code(dtypes, user_query1)
                exec(_code)
            
            if show_code1:
                with st.expander("Python Code"):
                    _code = _code.replace('st.write(', 'print(')
                    st.code(_code, language='python')
        else:
            st.warning("Please enter a query.")
    
    st.write("\n")
    
    cols = list(df.columns)
    
    # Generate plot
    st.markdown("#### Describe the plot you want to see:")
    user_query2 = st.text_area("2", label_visibility="collapsed")
    show_code2 = st.checkbox("Show Python Code ")
    
    if st.button("Generate Plot"):
        if user_query2:
            figure, code_ = create_plot(user_query2, cols)
            with st.spinner("Generating plot..."):
                st.plotly_chart(figure, theme="streamlit")
                st.write("\n")
            
            if show_code2:
                with st.expander("Python Code"):
                    st.code(code_, language='python')
    
    
    
