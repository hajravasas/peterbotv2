import onedocbot
import streamlit as st

st.markdown("<h2 style='text-align: center;'>Welcome to <br>🤖Lee Bot🤖</h2>",
            unsafe_allow_html=True)

st.write("Ask me anything. If Lee taught me about the matter, I'll respond!")

input_text = st.text_area(
    "Enter your your question for Lee Bot", placeholder="Enter your question here.")

if st.button("Ask LeeBot"):
    if input_text is None or input_text == '':
        st.warning("Enter your question you want to ask.")
    else:
        st.info("Your query: \n" + input_text)
        with st.spinner("Processing your query.."):
            index = onedocbot.create_index_from_mongo(True)
            response = onedocbot.query_doc(index, input_text, True)
            print(response)
        st.success(response)

        # Shows the source documents context which
        # has been used to prepare the response
        # st.write("Source Documents")
        # st.write(response.get_formatted_sources())
