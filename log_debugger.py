import pandas as pd
import sqlite3

# Replace 'your_file.csv' with the path to your CSV file
csv_file_path = f'logs/char_attrs.csv'

# Load the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)
print(f'available columns: {df.columns}')
# Create a connection to a temporary in-memory SQLite database
conn = sqlite3.connect(':memory:')

# Load the DataFrame into SQL table named 'my_table'
df.to_sql('my_table', conn, index=False, if_exists='replace')

# Write your SQL query here
# Example SQL query: SELECT * FROM my_table WHERE ColumnName = 'SomeValue'
sql_query = 'SELECT * FROM my_table WHERE  name = "Lily Johnson"'

# Execute the query and fetch the results
df_result = pd.read_sql_query(sql_query, conn)

# Display the result of the SQL query
__import__('ipdb').set_trace()
print(df_result)

# Don't forget to close the SQLite connection
conn.close()
