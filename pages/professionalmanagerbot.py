import peterbot
import streamlit as st

st.markdown("<h2 style='text-align: center;'>Welcome to the<br>🤖ProfessionalManagerBot🤖</h2>",
            unsafe_allow_html=True)

input_text = st.text_area(
    "You can ask any questions about (engineering) management and the ProfessionalManagerBot will try to answer it for you. Ask a question like *Is engineering management hard? Write a haiku* or *What are the foundations of engineering management, say it like a pirate.*", placeholder="Enter your question here.")
if input_text is not None:
    if st.markdown(
        """
    <div style="display: flex; justify-content: center;">
        <button style="padding: 10px 20px;">Ask ProfessionalManagerBot</button>
    </div>
    """,
        unsafe_allow_html=True
    ):
        document_uploaded = True
        st.info("Your query: \n" + input_text)
        with st.spinner("Processing your query.."):
            index = peterbot.create_index_from_pinecone()
            response = peterbot.query_doc(index, input_text)
            print(response)

        st.success(response)

        st.divider()
