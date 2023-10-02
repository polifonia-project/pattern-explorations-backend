
# Python Flask Server for Pattern Explorations using the Blazegraph KG

A Python Flask server providing APIs for searching musical tunes and retrieving similarity measures. It can be connected to a SPARQL endpoint but currently uses a mock response.

## Prerequisites

Ensure you have Python and pip installed on your machine. I'd recommend using a environment manager like miniconda to keep everything sane.

## Installing Dependencies

Clone the repository, navigate to the project folder and install the dependencies from `requirements.txt`.

```
git clone <repository-url>
cd <project-folder>
pip install -r requirements.txt
```

Replace `<repository-url>` and `<project-folder>` with your actual repository URL and project folder name.

## Application Code

The main application code is in `app.py`, and the SPARQL queries are generated using a query factory in `query_factory.py`.

## Running the Server

Start the Flask server with:

```
python app.py
```

The server runs on `localhost` port `5000` by default.

## API Endpoints

### 1. Search for Tunes

Search for tunes with a GET request to `/api/search`, passing the search query as a parameter.

Example:

```
curl http://localhost:5000/api/search?query=Vivaldi
```

### 2. Retrieve Similarity Measures

Get a list of similarity measures with a GET request to `/api/similarity-measures`.  

Example:

```
curl http://localhost:5000/api/similarity-measures
```
would return all of the available similarity measures.

## `query_factory.py` Example

The `query_factory.py` contains functions to generate SPARQL queries. Here is a usage example:

```python
import requests
from query_factory import get_tune_given_name

# Generate the SPARQL query
sparql_query = get_tune_given_name("Yankee Doodle")

# Execute the SPARQL query
response = requests.post(
    BLAZEGRAPH_URL,
    data={
        'query': sparql_query,
        'format': 'json'
    }
)

# Print the JSON data
print(response.json())
```

## `requirements.txt`

The required libraries are listed in `requirements.txt`:

```
Flask==2.3.2
Flask_Cors==3.0.10
Requests==2.31.0
```

