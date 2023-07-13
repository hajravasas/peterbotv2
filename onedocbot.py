import os

import pandas as pd
import streamlit as st
import pinecone
from auth0_component import login_button
from llama_index import GPTListIndex, GPTVectorStoreIndex, SimpleDirectoryReader
from llama_index import download_loader
from llama_index.vector_stores import PineconeVectorStore
from llama_index.storage.storage_context import StorageContext
from matplotlib import pyplot as plt
from pandasai.llm.openai import OpenAI
from typing import Optional, Union
from llama_index.node_parser import SimpleNodeParser
from llama_index.storage.docstore import MongoDocumentStore
from llama_index.storage.index_store.mongo_index_store import MongoIndexStore
from llama_index.indices.loading import load_index_from_storage
from streamlit_extras.buy_me_a_coffee import button

documents_folder = "documents"
pinecone_api_key = os.environ.get("PINECONE_API_KEY")
csv_llm = OpenAI(api_token=os.environ['OPENAI_API_KEY'])
MONGO_URI = os.environ["MONGO_URI"]
document_uploaded = False
clientId = os.getenv("AUTH0_CLIENT_ID")
domain = "dev-takuxm4bkqc2jayl.us.auth0.com"
redirect_uri = 'http://localhost:8501/component/auth0_component.login_button/index.html'
user_info = None

user_info = login_button(clientId, domain=domain)
st.write(user_info)


def main():
    print("Hello, PETERBOT!")


if __name__ == "__main__":
    main()

# Load PandasAI loader, Which is a wrapper over PandasAI library
PandasAIReader = download_loader("PandasAIReader")


def get_csv_result(df, query):
    try:
        reader = PandasAIReader(llm=csv_llm)
        csv_response = reader.run_pandas_ai(
            df,
            query,
            is_conversational_answer=False
        )
        return csv_response
    except Exception as e:
        print(e)
        st.error("Failed to read documents")


def save_file(doc):
    fn = os.path.basename(doc.name)
    # check if documents_folder exists in the directory
    if not os.path.exists(documents_folder):
        # if documents_folder does not exist then making the directory
        os.makedirs(documents_folder)
    # open read and write the file into the server
    open(documents_folder + '/' + fn, 'wb').write(doc.read())
    # Check for the current filename, If new filename
    # clear the previous cached vectors and update the filename
    # with current name
    if st.session_state.get('file_name'):
        if st.session_state.file_name != fn:
            st.cache_resource.clear()
            st.session_state['file_name'] = fn
    else:
        st.session_state['file_name'] = fn

    return fn


def remove_file(file_path):
    # Remove the file from the Document folder once
    # vectors are created
    if os.path.isfile(documents_folder + '/' + file_path):
        os.remove(documents_folder + '/' + file_path)


def create_index():
    # index_name = "will put logic here to look up index per user"

    if document_uploaded:
        try:
            documents = SimpleDirectoryReader(documents_folder).load_data()

            if user_info is not None and user_info['sub'] is not None:
                nodes = SimpleNodeParser().get_nodes_from_documents(documents)
                storage_context = StorageContext.from_defaults(
                    docstore=MongoDocumentStore.from_uri(uri=MONGO_URI),
                    index_store=MongoIndexStore.from_uri(uri=MONGO_URI),
                )

                storage_context.docstore.add_documents(nodes)

                # if index_name in pinecone.list_indexes():
                #     print("Index already exists!!!")
                #     pinecone_index = pinecone.Index(index_name)
                # else:
                #     pinecone.create_index(index_name, dimension=1536)
                #     pinecone_index = pinecone.Index(index_name=index_name)

                index = GPTVectorStoreIndex.from_documents(
                    documents, storage_context=storage_context)
            else:
                index = GPTVectorStoreIndex.from_documents(documents)

            return index
        except Exception as e:
            print(e)
            st.error("Failed to read documents")
    else:
        st.warning("Upload a document you want to query.")


def lookup_index():
    query_params = st.experimental_get_query_params()
    username_list = query_params.get("user_name", [None])
    username: Optional[Union[str, None]
                       ] = username_list[0] if username_list else None

    nickname = None
    if user_info is not False:
        nickname = user_info['nickname']

    if nickname is not None:
        return nickname + "-index"
    else:
        return "peterbotindex"
    return None


@st.cache_resource
def create_index_from_pinecone(is_document_uploaded=False):
    index_name = lookup_index()

    if document_uploaded or is_document_uploaded:
        try:
            documents = SimpleDirectoryReader(documents_folder).load_data()
            pinecone.init(api_key=pinecone_api_key,
                          environment="us-west4-gcp-free")

            if index_name in pinecone.list_indexes():
                print("Index already exists!!!")
                pinecone_index = pinecone.Index(index_name)
            else:
                pinecone.create_index(index_name, dimension=1536)
                pinecone_index = pinecone.Index(index_name=index_name)

            vector_store = PineconeVectorStore(
                pinecone_index=pinecone_index)
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store)
            index = GPTVectorStoreIndex.from_documents(
                documents, storage_context=storage_context)

            return index
        except Exception as e:
            print(e)
            st.error("Failed to read documents")
    else:
        st.warning("Upload a document you want to query.")


def create_index_from_mongo(is_document_uploaded=False):
    storage_context = StorageContext.from_defaults(
        docstore=MongoDocumentStore.from_uri(uri=MONGO_URI),
        index_store=MongoIndexStore.from_uri(uri=MONGO_URI),
    )

    docstore = MongoDocumentStore.from_uri(
        uri=MONGO_URI, db_name="db_docstore")
    nodes = list(docstore.docs.values())
    list_index = GPTListIndex(nodes, storage_context=storage_context)
    return GPTVectorStoreIndex(nodes, storage_context=storage_context)


def query_doc(vector_index, query, is_document_uploaded=False):
    # Applies Similarity Algo, Finds the nearest match and
    # take the match and user query to OpenAI for rich response
    if document_uploaded or is_document_uploaded:
        query_engine = vector_index.as_query_engine()
        response = query_engine.query(query)
        return response


st.title("🤖`OneDocBot!`🤖 welcomes you")

st.write(
    "Upload a .pdf or .txt file and ask it any questions. Make sure to try out features like *summarize this doc in a few sentences*, *say it like a haiku*, etc...")
input_doc = st.file_uploader("Upload your Documents")

if input_doc is not None:
    st.info("Doc Uploaded Successfully")
    file_name = save_file(input_doc)
    document_uploaded = True
    index = create_index()
    remove_file(file_name)

st.divider()
input_text = st.text_area("Ask your question")

if input_text is not None:
    if st.button("Ask"):
        if document_uploaded:
            st.info("Your query: \n" + input_text)
            with st.spinner("Processing your query.."):
                # index = create_index()
                response = query_doc(index, input_text)
                print(response)

            st.success(response)

            st.divider()
            # Shows the source documents context which
            # has been used to prepare the response
            if response is not None:
                st.write("Source Documents")
                st.write(response.get_formatted_sources())
        else:
            st.error("Upload a document you want to query! 📰")

st.caption(
    "Thank you for trying out PeterBot! If you want to support the project, would love your contributions!")
button(username="profmanager", floating=False, width=221)
