import streamlit as st 
import pandas as pd
import sqlite3
import tempfile
import os
import openai
import toml
import re
import graphviz
import base64
import cv2


config = toml.load('/secrets.toml')
openai_key = config['open_ai_key']['OPENAI_API_KEY']

openai.api_key = openai_key

st.set_page_config(
    page_title = "Query SQLite Database",
    layout="wide"
)

def dbinfo(uploaded_file):
        
    uploaded_file.seek(0)
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        db_file_path = tmp.name
        
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, sql
        FROM sqlite_master
        WHERE type = 'table';
    """)
    
    table_definitions = cursor.fetchall()
    
    schema = {}
    foreign_keys = []
    for table in table_definitions:
        table_name = table[0]
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        schema[table_name] = [col[1] for col in columns]
        
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fk_info = cursor.fetchall()
        for fk in fk_info:
            from_table = table_name
            to_table = fk[2]
            column = fk[3]
            foreign_keys.append({"from_table": from_table, "to_table": to_table, "column": column})
   
    conn.close()
    
    # Delete the temporary file
    os.unlink(db_file_path)
    return table_definitions, schema, foreign_keys

def generate_dot_file(schema, foreign_keys):
    dot = ['digraph G {']
    
    # Add entities
    for table, columns in schema.items():
        # Start of entity definition
        dot.append(f'    {table} [shape=plaintext, label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4"><tr><td bgcolor="lightblue">{table}</td></tr>')
        
        # Add columns
        for column in columns:
            dot.append(f'<tr><td align="left">{column}</td></tr>')
        
        # End of entity definition
        dot.append('</table>>];')
    
    # Add relationships (foreign key constraints)
    for foreign_key in foreign_keys:
        dot.append(f'    {foreign_key["from_table"]} -> {foreign_key["to_table"]} [label="{foreign_key["column"]}"];')
    
    dot.append('}')
    return '\n'.join(dot)

# Function to render DOT file to image
def render_dot_to_image(dot):
    # Create a temporary file to save DOT content
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.dot') as f:
        dot_file_path = f.name
        f.write(dot)
    
    # Render DOT file to PNG image
    graph = graphviz.Source(dot, format='png')
    graph.render(filename=os.path.splitext(dot_file_path)[0], cleanup=True)
    image_path = os.path.splitext(dot_file_path)[0] + '.png'
    
    return image_path


def render_img_html(image_b64):
   st.markdown(f"<img style='max-width: 100%;max-height: 100%;' src='data:image/png;base64, {image_b64}'/>", unsafe_allow_html=True)

    
def image_to_base64(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    _, encoded_image = cv2.imencode(".png", image)
    base64_image = base64.b64encode(encoded_image.tobytes()).decode("utf-8")
    return base64_image

def generate_sql(user_query, table_definitions, selected_tables):
    
    prompt = "This is a SQLite database. Please generate SELECT SQL statements based on the following information:\n"
    for table_name, sql_definition in table_definitions:
        prompt += f"\nTable: {table_name}\nSQL Definition:\n{sql_definition}\n"
    prompt += "\nUser Query: " + user_query + "\n"
    prompt += "\nSelected Tables of Interest: " + ', '.join(selected_tables) + "\n"
    prompt += "\nNote: These are the selected tables of interest for the user to query. Focus more on these tables to retrieve the correct answer.\n"


    # Additional information to handle potential issues and ensure correct SQL query generation
    prompt += "\nAdditional Information:\n"
    prompt += "- Ensure that the generated SQL query only performs SELECT operations to retrieve data from the database.\n"
    prompt += "- Ensure that the generated SQL query accurately reflects the user's intent and retrieves the desired data.\n"
    prompt += "- Handle potential misunderstandings or ambiguous queries by providing clear and specific instructions to the language model.\n"
    prompt += "- Verify the generated SQL query to ensure it follows proper SQL syntax and adheres to the database schema.\n"
    prompt += "- If the generated query seems incorrect or unclear, consider refining the user query or providing more context in the prompt.\n"
    prompt += "- Based on the userquery use the appropriate join operation (INNER JOIN, LEFT JOIN, RIGHT JOIN, or FULL JOIN) instead of using the implicit join notation.\n"

    prompt += "\nGenerate SQL statements:"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        max_tokens=200,
        messages=[
            {"role": "user", "content": prompt},
        ] 
    )

    response = completion.choices[0].message['content'].strip()
    return response

def execute_sql(generated_sql, uploaded_file):
    # after you upload the file and read it once, the file cursor might be at the end of the file. When you try to read the file again for the second time without resetting the cursor, it will start reading from the end, resulting in an empty file.
    uploaded_file.seek(0)
    
    # Copy uploaded file data to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as Tmp:
        Tmp.write(uploaded_file.read())
        temp_file_path = Tmp.name

    try:
        # Connect to the temporary SQLite database
        conn_temp = sqlite3.connect(temp_file_path)
        cursor_temp = conn_temp.cursor()
        
        cursor_temp.execute(generated_sql)
        df = pd.DataFrame(cursor_temp.fetchall(), columns=[i[0] for i in cursor_temp.description])
        st.write("Query Result:")
        st.write(df)
        
        cursor_temp.close()
        conn_temp.close()
        
        os.unlink(temp_file_path)

    except Exception as e:
            error_message = str(e)
            st.write(error_message)
    
uploaded_file = st.file_uploader('Upload SQLite .db file', type='db')
    
if uploaded_file is not None:
    # Extract table definitions, schema and foreign key constraints from uploaded file
    table_definition, schema, foreign_keys = dbinfo(uploaded_file)
    
    # Generate DOT file from schema
    dot_content = generate_dot_file(schema, foreign_keys)

    # Render DOT file to image
    image_path = render_dot_to_image(dot_content)
    
    st.write("Database Scehma Diagram:")
    
    # Display the generated ER diagram with resizing
    render_img_html(image_to_base64(image_path))
    
    # Select tables of interest
    st.write("")
    st.write("Select Tables To Query:")
    selected_tables = st.multiselect('x', [table[0] for table in table_definition],label_visibility="collapsed" )
    
    #sqlquery
    st.write("Enter Your Natural Language Query:")
    user_query = st.text_area("1", label_visibility="collapsed")
    
    if st.button("Generate"):

        if user_query:
            generated_sql = generate_sql(user_query, table_definition, selected_tables)
            st.write("Generated SQL Statement:")
            
            # Check if response contains code block (```sql ... ```)
            if "```" in generated_sql:
            # Use regular expression to extract SQL query from code block
                pattern = r'```sql(.*?)```'
                match = re.search(pattern, generated_sql, re.DOTALL)
                if match:
                    generated_sql = match.group(1).strip()
            
            st.code(generated_sql)
                    
            execute_sql(generated_sql, uploaded_file)
            
        else: 
            st.write("Please enter query")
        
   
