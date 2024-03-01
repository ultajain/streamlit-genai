from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

faq_prompt_template = """
Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
Context:\n {context}?\n
Question: \n{question}\n

Answer:
"""


class LLM:
    def index_documents(self, pdf_docs):
        pass


class GeminiLLM(LLM):

    def __init__(self, api_key):
        self.api_key = api_key
        self.vector_store = None

    def _get_conversational_chain(self):
        model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3, google_api_key=self.api_key)
        prompt = PromptTemplate(template=faq_prompt_template, input_variables=["context", "question"])
        return load_qa_chain(model, chain_type="stuff", prompt=prompt)

    def index_documents(self, pdf_docs):
        # extract pdf text
        raw_text = ""
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                raw_text += page.extract_text()
        # chunk the text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        text_chunks = text_splitter.split_text(raw_text)
        # create and save vector store
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=self.api_key)
        self.vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)

    def answer_user_query(self, user_query):
        docs = self.vector_store.similarity_search(user_query)
        chain = self._get_conversational_chain()
        response = chain(
            {"input_documents": docs, "question": user_query}
            , return_only_outputs=True)
        print(response)
        return "Reply: " + response["output_text"]
