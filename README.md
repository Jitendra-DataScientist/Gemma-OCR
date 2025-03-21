- install the required dependencies in the requirements.txt file (preferrably in a virtual environment).
- API and streamlit app are independent of each other.
- API endpoint is of post request type that takes a form data with key name "file" that takes an image file of type .jpg, .jpeg or .png.
- API could be run with the command:

**uvicorn app:app --reload --host 0.0.0.0 --port 8003**

(reload, host and port flags aren't mandatory)
- streamlit app could be run with the command:

**streamlit run streamlit_app.py  --server.port 8004 --server.address 0.0.0.0**

(server.port and server.address flags aren't mandatory)
- **credits:** https://github.com/patchy631/ai-engineering-hub/tree/main/gemma3-ocr


