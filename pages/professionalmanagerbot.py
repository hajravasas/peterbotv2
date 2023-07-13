import onedocbot
import streamlit as st

st.markdown("<h2 style='text-align: center;'>Welcome to the<br>🤖ProfessionalManagerBot🤖</h2>",
            unsafe_allow_html=True)

st.write("You can ask any questions about (engineering) management and the ProfessionalManagerBot will try to answer it for you. Ask a question like *Is engineering management hard? Write a haiku* or *What are the foundations of engineering management, say it like a pirate.*")

input_text = st.text_area(
    "Enter your your question for the ProfessionalManagerBot", placeholder="Enter your question here.")

if st.button("Ask ProfessionalManagerBot"):
    if input_text is None or input_text == '':
        st.warning("Enter your question you want to ask.")
    else:
        st.info("Your query: \n" + input_text)
        with st.spinner("Processing your query.."):
            index = onedocbot.create_index_from_mongo()
            response = onedocbot.query_doc(index, input_text, True)
            print(response)
        st.success(response)

        # Shows the source documents context which
        # has been used to prepare the response
        # st.write("Source Documents")
        # st.write(response.get_formatted_sources())
