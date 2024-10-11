# %%
import sys
import configparser
import os
# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
class LLMOperation:
    def __init__(self):
        # Config Parser
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.key = config['Gemini']['KEY']
        if self.key is None:
            print("Specify os.getenv('API_KEY') as environment variable.")
            sys.exit(1)

        self.chat = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash-latest", 
                google_api_key=self.key,
                # convert_system_message_to_human=True
                )

    def domath(self,question):
        from langchain.chains import LLMMathChain
        math_chain = LLMMathChain.from_llm(
        llm=self.chat,
        # verbose=True,
        )
        result = math_chain.invoke({"question": question})
        return result

    def translate2eng(self,question):
        template = """
            你是一個翻譯機器人，請幫我把以下中文翻譯成英文,輸出請直接給出翻譯後的英文句子,不需要標頭及有問題及回答等格式:
            問題: {query}

            回答:
            """

        prompt_template = PromptTemplate(
            template=template,
            input_variables=["query"],
        )
        my_prompt = prompt_template.format(query=question)
        return self.chat.invoke(my_prompt).content

    def japan_sappro(self,question):
        template = """
            你是一個日本北海道的專家，請幫我回答以下問題或者規劃相關行程,越詳盡越好,不要輸出特殊字元如'*'及有問題/回答等格式,請以繁體中文回答:
            問題: {query}

            回答:
            """

        prompt_template = PromptTemplate(
            template=template,
            input_variables=["query"],
        )
        my_prompt = prompt_template.format(query=question)
        return self.chat.invoke(my_prompt).content
    
    def normalqry(self,question):
        template = """
            你是一個AI助手，,不要輸出特殊字元如'*'及有問題/回答等格式,請以繁體中文回答:
            問題: {query}

            回答:
            """

        prompt_template = PromptTemplate(
            template=template,
            input_variables=["query"],
        )
        my_prompt = prompt_template.format(query=question)
        return self.chat.invoke(my_prompt).content

if  __name__ == "__main__":
    LLMOperation = LLMOperation()
    #query = "18的平方根？"
    query="請幫我規劃北海道5天自由行"
    # if LLMOperation.ifmath(query):
    try:
        # print('yes')
        print(LLMOperation.domath(query)['answer'].replace('Answer: ',''))
    except:
        # print('no')
        print(LLMOperation.normalqry(query))

