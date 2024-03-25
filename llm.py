import streamlit as st
import os, asyncio
import weave
import sqlite3
from openai import OpenAI


# do wandb login in the command line
weave.init('garfield2')

class Text2SQLModel(weave.Model):
    system_prompt: str
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.0
    
    @weave.op()
    def predict(self, question):
        client = OpenAI()
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question}
        ]
        response = client.chat.completions.create(model=self.model, messages=messages, temperature=self.temperature)
        return response.choices[0].message.content.rstrip(';')

@weave.op()
def matchy_matchy(expected_response: str, prediction: str) -> dict:
    ''' Brute force approach'''
    return {'correct': expected_response == prediction}

# @weave.op()
# def similarity(expected_response: str, prediction: str) -> dict:
#     return {'correct': expected_response == prediction}

def eval_sql(expected_response: str, prediction: str) -> dict:
    answer = run_sql_query(prediction, "billboard.db")
    return {'correct': expected_response == answer}

data = [{'question': 'How many weeks did Taylor Swift place at position 1?', 'expected_response': 271},
       {'question': 'What is the capital of Denmark?', 'expected_response': 'NULL'},
       {'question': 'How is Beyonce doing?', 'expected_response': 'NULL'},
       {'question': 'How many weeks was Heat Waves in the top position?', 'expected_response': 91},
       {'question': 'What is top song in the third week of March?', 'expected_response': 'Carnival'}]

@weave.op()
def run_sql_query(sql: str,db):
    if sql== 'NULL':
        return 'NULL'
    conn=sqlite3.connect(db)
    cur=conn.cursor()
    cur.execute(sql)
    rows=cur.fetchall()
    conn.close()  # Removed conn.commit() for SELECT queries
    for row in rows:
        print(f"Rows: {row}")
    # SHOW tuple error
    # return rows
    return rows[0][0]

# Define Your Prompt as a single string, not a list
system_prompt_old = """
Your task is to generate SQL queries, given a question by the user.

The SQL database has the name BILLBOARD and has the following columns - chart_week, current_week, title, performer, last_week, peak_pos, wks_on_chart

For example:
Question: How many entries of records are present?, 
SQL: SELECT COUNT(*) FROM BILLBOARD ;

Question: Tell me all the songs by the artist Beyonce?, 
SQL: SELECT * FROM BILLBOARD WHERE PERFORMER="Beyonce"; 

Output only the SQL query.
"""

system_prompt = """
Your task is to generate SQL queries, given a question by the user.

The SQL database has the name BILLBOARD and has the following columns - chart_week, current_week, title, performer, last_week, peak_pos, wks_on_chart

For example:
Question: How many entries of records are present?, 
SQL: SELECT COUNT(*) FROM BILLBOARD ;

Question: Tell me all the songs by the artist Beyonce?, 
SQL: SELECT * FROM BILLBOARD WHERE PERFORMER="Beyonce"; 

Output only the SQL query. If the question is not related to our database, return "NULL"
"""

evaluation = weave.Evaluation(name='Text2SQL', dataset=data, scorers=[matchy_matchy, eval_sql])
model = Text2SQLModel(system_prompt=system_prompt)
# res = evaluation.evaluate(model)
print(asyncio.run(evaluation.evaluate(model)))


## Streamlit App
st.set_page_config(page_title="Garfield")
st.header("Text2SQL")

question = st.text_input("Question: ", key="input", value="How many weeks did Taylor Swift place at position 1?")

submit = st.button("Ask the question")

# if submit is clicked
if submit:
    # call the model
    response = model.predict(question)
    st.subheader("SQL")
    print(response)
    st.write(response)
    answer = run_sql_query(response, "billboard.db")
    st.subheader("Answer")
    st.write(answer)