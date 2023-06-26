# peterbotv2
Chat with your Docs and gain better insights. Powered by `LlamaIndex` and `Streamlit` is used for UI. 
Handles `CSV/PDFs/Txt/Doc`. CSV file is catered via [PandasAI](https://llamahub.ai/l/pandas_ai) loader and rest of the docs are handled via 
`GPTVectorStoreIndex`.

Clone the repo or copy the `.py ` file in your local machine. 

## Install required Dependencies
```
pip install -r requirements.txt
```

## Create a folder in the root dir and name it as `documents`

## Run the application
`streamlit run peterbot.py`