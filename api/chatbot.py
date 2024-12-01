from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os
import datetime
import simplejson as json
import psycopg2
from psycopg2 import errorcodes, Error
import llmserv

# Creating app
app = Flask(__name__)
# Accept requests from frontend
CORS(app)

load_dotenv()   # Loads .env variables into OS environment

# Allow for POST with Content-Type: application/json
app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key = os.environ['FLASK_SECRET_KEY']

# Initialize OpenAI instance
# client = OpenAI(
#     api_key= os.environ['OPENAI_API_KEY'],
#     base_url=os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1/')
# )

##* Util functions

def insert_log(sid, timestamp, log):
    
    # Random string table name for logs table
    table_name = "z2qk2ldfyfcjw2rv"

    try:
        # Connect to DB
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'db'),
            port='5432', 
            dbname=os.environ['POSTGRES_DB'], 
            user=os.environ['POSTGRES_USER'], 
            password=os.environ['POSTGRES_PASSWORD']
        )
        cursor = conn.cursor()

        # Insert into log table
        cursor.execute(f"INSERT INTO {table_name} (sid, timestamp, log) VALUES (%s, %s, %s);", (sid, timestamp, json.dumps(log)))

        # Commit change
        conn.commit()

        # Close connection
        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        error_code = e.pgcode
        error_message = e.pgerror
        print(f"PostgreSQL error: {error_code} - {error_message}")
        return f"PostgreSQL error: {error_code} - {error_message}"

    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"

    return "Interaction logged"

def update_log_feedback(sid, timestamp, attr, type, content):

    res = None
    # Random string table name for logs table
    table_name = "z2qk2ldfyfcjw2rv"

    try:
        # Connect to DB
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'db'),
            port='5432', 
            dbname=os.environ['POSTGRES_DB'], 
            user=os.environ['POSTGRES_USER'], 
            password=os.environ['POSTGRES_PASSWORD']
        )
        cursor = conn.cursor()

        # Select log from table with corresponding timestamp
        cursor.execute(f"SELECT log FROM {table_name} WHERE sid = %s AND timestamp = %s;", (sid, timestamp,))
        res = cursor.fetchone()[0]

        # Load log back as JSON object
        log = json.loads(res)

        # If attribute not yet in log, add it first
        if attr not in log['feedback']:
            log['feedback'][attr] = {}

        # Add updated feedback value
        log['feedback'][attr][type] = content

        # Update table with new log value
        cursor.execute(f"UPDATE {table_name} SET log = %s WHERE sid = %s AND timestamp = %s", (json.dumps(log), sid, timestamp))

        # Commit change
        conn.commit()

        # Close connection
        cursor.close()
        conn.close()

        print(res)

    except psycopg2.Error as e:
        error_code = e.pgcode
        error_message = e.pgerror
        print(f"PostgreSQL error: {error_code} - {error_message}")
        return f"PostgreSQL error: {error_code} - {error_message}"

    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"

    return "Updated feedback"

def generate_schema_string():
    
    db_schema = None
    schema_string = ""

    log_table_name = "z2qk2ldfyfcjw2rv"

    try:
        # Connect to DB
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'db'),
            port='5432', 
            dbname=os.environ['POSTGRES_DB'], 
            user=os.environ['POSTGRES_USER'], 
            password=os.environ['POSTGRES_PASSWORD']
        )
        cursor = conn.cursor()

        # Retrieve all table names from DB
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()

        # For each table, retrieve column name, data type
        for table in tables:
            # Since name is 0th index in tuple...
            table_name = table[0]

            # If this is the logs table, do not include in schema
            if table_name == log_table_name:
                continue

            # Add to schema string
            schema_string += f"Table: {table_name}, Columns: ["
            # query DB for schema
            cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table_name}';")

            # Collect results as array of (column_name, data_type) tuples
            db_schema = cursor.fetchall()

            # As long as a result was  returned
            if db_schema:
                # Deconstruct tuple into column_name, column_dtype, add to schema string
                for column_name, column_dtype in db_schema:
                    schema_string += f"Column: {column_name}, Data type: {column_dtype}\n"
            
            # Denote end of columns
            schema_string += "];\n"
            
            print(schema_string)

        # Close cursor and connection now that they are no longer being used
        cursor.close()
        conn.close()

    except psycopg2.Error as e:

        error_code = e.pgcode
        error_message = e.pgerror
        print(f"PostgreSQL error: {error_code} - {error_message}")

    except Exception as e:
        print(f"Error: {e}")

    # Return DB schema exists, return string generated; Otherwise, "No SQL Schema"
    return schema_string if len(schema_string) > 0 else "No SQL Schema"

def query_db(query):

    res = None
    try:
        # Connect to DB
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'db'),
            port='5432', 
            dbname=os.environ['POSTGRES_DB'], 
            user=os.environ['POSTGRES_USER'], 
            password=os.environ['POSTGRES_PASSWORD']
        )
        cursor = conn.cursor()

        # Execute query
        cursor.execute(query)
        res = cursor.fetchall()

        # Close connection
        cursor.close()
        conn.close()

        print(res)

    except psycopg2.Error as e:

        error_code = e.pgcode
        error_message = e.pgerror
        print(f"PostgreSQL error: {error_code} - {error_message}")

    except Exception as e:
        print(f"Error: {e}")

    # Return response if exists
    return res if res else "No results"

def generate_query(prompt, session_messages):
    # Add user's prompt to log of session messages
    session_messages.append(prompt)

    # Prompt OpenAI API for query response 
    # response = client.chat.completions.create(
    #     model=os.environ.get('LLM_MODEL', 'gpt-4-0125-preview'),
    #     messages=session_messages,
    #     logprobs=True,
    #     top_logprobs=2,
    #     temperature=0,
    # )
    client = llmserv.GPTClient(os.environ['OPENAI_API_KEY'])
    response = client.send_prompt(session_messages, os.environ.get('LLM_MODEL', 'gpt-4-0125-preview'), None)

    # Add assistant's response to log of session messages
    session_messages.append({
        'role': response.choices[0].message.role,
        'content': response.choices[0].message.content
    })

    print(response.choices[0].message.content)

    # Parse response as JSON
    try:
        res = json.loads(response.choices[0].message.content)
    except ValueError as e:
        print(f"Error: {e}")
        res = {"response": response.choices[0].message.content}
    
    return {
        "model": response.model,
        "role": response.choices[0].message.role,
        "content": res
    }

def generate_response(message, result, session_responses):
    # Simple prompt for providing result and question to be answered to GPT
    prompt = f"The answer to the question: '{message}' is {result}."
    
    # Add prompt message to log of responses 
    session_responses.append({
        "role": "user",
        "content": prompt
    })

    # Prompt OpenaAI API for 
    # response = client.chat.completions.create(
    #     model=os.environ.get('LLM_MODEL', 'gpt-3.5-turbo'),
    #     messages=session_responses,
    #     logprobs=True,
    #     top_logprobs=2,
    #     temperature=0
    # )
    client = llmserv.GPTClient(os.environ['OPENAI_API_KEY'])
    response = client.send_prompt(session_responses, os.environ.get('LLM_MODEL', 'gpt-4-0125-preview'), None)

    # Add assistant response to log
    session_responses.append({
        'role': response.choices[0].message.role,
        'content': response.choices[0].message.content
    })

    print(response.choices[0].message.content)

    # Parse response as JSON
    try:
        res = json.loads(response.choices[0].message.content)
    except ValueError as e:
        print(f"Error: {e}")
        res = {"response": response.choices[0].message.content}

    data = []

    # If response included a True 'vis' - Data can be visualized; Format as object in backend for rendering in frontend
    if 'vis' in res and res['vis']:
        # If recommends a pie chart, will provide data itself; Otherwise, create (x,y) pairs for data
        if res['plot'] != 'pie' or 'data' not in res:
            try:
                for (x, y) in result:
                    data.append({"x": x, "y": y})
                res["data"] = data
            # Visualization not valid if there was an error formatting the data
            except Exception as e:
                print(f"Error: {e}")
                res['vis'] = False

        print(res)

    return {
        "model": response.model,
        "role": response.choices[0].message.role,
        "content": res
    }

##* Globals

# Global of schema string
schema_string = generate_schema_string()

# System prompt for start of query generating conversation
session_query_sys = {
    "role": "system",
    "content": f"""
    You are a helpful PostgreSQL expert who can provide queries for a database containing user information.
    Given the PostgreSQL database schema:
    {schema_string}
    You answer questions by providing a JSON object with the key "sql" and a PostgreSQL query.
    If you cannot create an PostgreSQL query to answer the question, provide a JSON object with the key "text" and an apology.
    Remember to ignore NULL values and add explicit type casts when creating PostgreSQL queries.
    Dates are in the form YYYY-MM-DD. Today is {datetime.datetime.now().date()}
    """
}

# System prompt for start of response generating conversation
session_response_sys = {
    "role": "system", 
    "content": """
    You answer questions by providing a JSON object containing the following:
        A JSON object with the key "text" and a summary of the results in a concise manner,
        A JSON Object with the key "vis" and a value True if the provided answer can be summarized well with a plot, or False otherwise
        A JSON Object with the key "plot" and a value of ("line", "bar", or "pie") if the data can be summarized best with a line, bar or pie chart.
            Otherwise, a value with the name of a plot that would work best, or None if the data cannot be visualized well.
        If the data can be summarized best with a pie chart, create a JSON object with the key "data" including the following:
            A list of JSON Objects, each with the key "x" and the name of a category, and the key "y" and the value corresponding to that category.
        Do not include code blocks in your response.
        A sample response may look like:
        {
            "text": "The average age of users who subscribed in each month in 2022 ranged from 25 to 35 years old.",
            "vis": true,
            "plot": "bar"
        }
    """
}

# Global of query messages between user/assistant during conversation
session_messages = []

# Global of assistant responses during conversation
session_responses = []

##! Remove this if using larger dataset; Will confuse context with pgh_weatherdata table
# Add example responses to start of message chain
query_ex = [
    {"role": "user", "content": "How many users subscribed in 2022?"},
    {"role": "assistant", "content": '{"sql": "SELECT COUNT(*) FROM user_data WHERE Join_Date LIKE "2022-%";"}'},
    {"role": "user", "content": "What is the average age of users?"},
    {"role": "assistant", "content": '{"sql": "SELECT AVG(Age) FROM user_data WHERE Age IS NOT NULL;"}'},
]


# Add system messages, examples to start of conversations
session_messages.append(session_query_sys)
session_messages.extend(query_ex)

session_responses.append(session_response_sys)


##* API routes

@app.route('/api/v1/message/', methods=['POST'])
def message():
    # Initialize log JSON object for this interaction
    log = {}

    # Log timestamp at start of this request
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log['timestamp'] = timestamp

    ##* Prompt

    # Get message from request; Return failing error code if 'message' key not found
    data = request.get_json()
    try:
        # Get unique session id from frontend for storing logs
        session_id = data['sid']
        message = data['message']
    except:
        return jsonify({"response": "Invalid message format"})
    
    # Add '?' to end of question if not already present
    if not message.endswith('?'):
        message += '?'

    # Create object for user's prompt
    prompt = {
        'role': 'user',
        'content': message
    }
    # Add user prompt to log
    log['prompt'] = prompt


    ##* Query

    # Prompt assistant for query
    query_response = generate_query(prompt, session_messages)

    # Add query to log
    log['query'] = query_response

    query_response_content = query_response['content']

    # If API returns object with 'response' key, return text response; do not execute SQL
    if 'text' in query_response_content:

        # Message generated from query API call will be response since it is not a query
        log['response'] = query_response

        print(log)
        log['feedback'] = {}

        # Add log to DB
        insert_log(session_id, timestamp, log)

        # Write out log for this message chain
        return jsonify({
            'message': {
                'timestamp': timestamp,
                'role': 'assistant',
                'content': query_response_content
            },
            'log': log
        })
    
    # Otherwise... clean up query and execute
    query = query_response_content['sql']

    query = query.replace('\n', ' ').replace('\t', ' ').replace('  ', ' ')
    # Add ';' to end of query if not already present; Do this after checking for valid SQL
    if not query.endswith(';'):
        query += ';'

    # print(query)
        
    ##* Query DB
    # Query DB with query generated by assistant
    result = query_db(query)

    # Add result to log
    log['result'] = result

    ##* Response
        
    # Generate response in context of question given query results
    response = generate_response(message, result, session_responses)
    
    print(response['content'])

    # Add response to log
    log['response'] = response

    # Add empty feedback array to log
    log['feedback'] = {}

    print(json.dumps(log))

    # Add log to DB
    insert_log(session_id, timestamp, log)


    # Return response to client
    return jsonify({
        'message': {
            'timestamp': timestamp,
            'role': 'assistant',
            'content': response['content'],
        },
        'log': log
    })

# Clear conversation
@app.route('/api/v1/clear/', methods=['GET'])
def clear():

    # Empty messages and responses for this session
    session_messages.clear()
    session_responses.clear()


    # Add system messages, examples to start of conversations
    session_messages.append(session_query_sys)
    session_messages.extend(query_ex)

    session_responses.append(session_response_sys)

    return jsonify({"response": "Messages cleared"})

# Update feedback for message with specified sid, timestamp
@app.route('/api/v1/feedback/update', methods=['PATCH'])
def update_feedback():
        
        data = request.get_json()
        try:
            # Destructure data from request
            session_id = data['sid']
            timestamp = data['timestamp']
            attribute = data['attribute']
            feedback_type = data['type']
            feedback_content = data['content']
        except:
            return jsonify({"response": "Invalid message format"})
        
        res = update_log_feedback(session_id, timestamp, attribute, feedback_type, feedback_content)

        return jsonify({"response": res})

