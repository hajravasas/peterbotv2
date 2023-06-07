import os

import pandas as pd
import streamlit as st
import pinecone
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader
from llama_index import download_loader
from llama_index.vector_stores import PineconeVectorStore
from llama_index.storage.storage_context import StorageContext
from matplotlib import pyplot as plt
from pandasai.llm.openai import OpenAI
from streamlit_extras.buy_me_a_coffee import button

documents_folder = "documents"
pinecone_api_key = os.environ.get("PINECONE_API_KEY")


def main():
    print("Hello, PETERBOT!")


if __name__ == "__main__":
    main()

# Load PandasAI loader, Which is a wrapper over PandasAI library
PandasAIReader = download_loader("PandasAIReader")

st.title("Welcome to `PeterBot! 🤖`")
st.header(
    "Interact with your documents using LLMs\nPowered by `LlamaIndex🦙` \n")


def get_csv_result(df, query):
    reader = PandasAIReader(llm=csv_llm)
    csv_response = reader.run_pandas_ai(
        df,
        query,
        is_conversational_answer=False
    )
    return csv_response


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


@st.cache_resource
def create_index():
    index_name = "peterbotindex"
    # Create vectors for the file stored under Document folder.
    # NOTE: You can create vectors for multiple files at once.
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

        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store)
        index = GPTVectorStoreIndex.from_documents(
            documents, storage_context=storage_context)

        return index
    except Exception as e:
        print(e)
        st.error("Failed to read documents")


def query_doc(vector_index, query):
    # Applies Similarity Algo, Finds the nearest match and
    # take the match and user query to OpenAI for rich response
    query_engine = vector_index.as_query_engine()
    response = query_engine.query(query)
    return response


tab1, tab2, tab3 = st.tabs(["Ask PeterBot", "PDFs/Docs", "CSV"])

with tab1:
    st.write("Ask PeterBot any questions about (engineering) management")
    st.divider()
    input_text = st.text_area(
        "Ask any questions about (engineering) management")
    if input_text is not None:
        if st.button("Ask PeterBot"):
            st.info("Your query: \n" + input_text)
            with st.spinner("Processing your query.."):
                index = create_index()
                response = query_doc(index, input_text)
                print(response)

            st.success(response)

            st.divider()
            # Shows the source documents context which
            # has been used to prepare the response
            st.write("Source Documents")
            st.write(response.get_formatted_sources())

with tab2:
    st.write("Chat with PDFs/Docs")
    input_doc = st.file_uploader("Upload your Docs")

    if input_doc is not None:
        st.info("Doc Uploaded Successfully")
        file_name = save_file(input_doc)
        index = create_index()
        remove_file(file_name)

    st.divider()
    input_text = st.text_area("Ask your question")

    if input_text is not None:
        if st.button("Ask"):
            st.info("Your query: \n" + input_text)
            with st.spinner("Processing your query.."):
                index = create_index()
                response = query_doc(index, input_text)
                print(response)

            st.success(response)

            st.divider()
            # Shows the source documents context which
            # has been used to prepare the response
            st.write("Source Documents")
            st.write(response.get_formatted_sources())

with tab3:
    st.write("Chat with CSV files using PandasAI loader with LlamaIndex")
    input_csv = st.file_uploader("Upload your CSV file", type=['csv'])

    if input_csv is not None:
        st.info("CSV Uploaded Successfully")
        df = pd.read_csv(input_csv)
        st.dataframe(df, use_container_width=True)

    st.divider()

    input_text = st.text_area("Ask your query")

    if input_text is not None:
        if st.button("Send"):
            st.info("Your query: " + input_text)
            with st.spinner('Processing your query...'):
                response = get_csv_result(df, input_text)
            if plt.get_fignums():
                st.pyplot(plt.gcf())
            else:
                st.success(response)


st.caption(
    "Thank you for trying out PeterBot! If you want to support the project, would love your contributions!")
button(username="profmanager", floating=False, width=221)