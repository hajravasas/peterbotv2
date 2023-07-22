import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pkg_resources
import streamlit as st

uri = os.environ["MONGO_URI"]


def mongotest():
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)


def display_dependency_versions():
    dependencies = [
        'streamlit',
        'numpy',
        'pandas',
        'llama_index'  # Add other dependencies here
    ]
    versions = [(d, pkg_resources.get_distribution(d).version)
                for d in dependencies]

    st.subheader("Dependency Versions")
    for package, version in versions:
        st.write(f"{package}: {version}")
