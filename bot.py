import json
from werobot import WeRoBot
import config as cfg
import openai
import itertools

mybot = WeRoBot(token=cfg.token)
mybot.config["APP_ID"] = cfg.appid
mybot.config['ENCODING_AES_KEY'] = cfg.aeskey

openai.api_base = cfg.api_base
openai.api_key = cfg.azure_openai_key #cfg.openai_key
deployment_name= cfg.deployment_name

#only azure api need below two lines
openai.api_type = cfg.api_type
openai.api_version = cfg.api_version

@mybot.image
def image_repeat(message,session):
    return message.img

@mybot.subscribe
def intro(message):
    return "欢迎加入系统之美，ChatGPT上线为您服务"

#@mybot.text
def echo(message,session): #echo back userinput for tests
    # Return message content
    return message.content 


@mybot.text
def text_response(message,session):
    userinput = message.content.strip().lower()
    sessionState = []
    if 'state' in session:
        sessionState = session.get('state',[])
        print("sessionState:" + sessionState.__str__())
    else:
        with open('fewshot.json', 'r', encoding='utf-8') as f:
            # Load the JSON data into a Python object for few-shot greeting pairs training
            sessionState = json.load(f)
    s = list(itertools.chain(*sessionState))
    s.append(userinput+'\n') #add a space to inexplicitly end the user prompt
    prompt = ' '.join(s)
    prompt = 'extract the intention and object from the message and answer based on it. '+ prompt
    print ('prompt: '+ userinput)
    answer=''

    if userinput in ["bye", "quit", "exit", "聊点别的"]:
        answer = "Bye!"
        sessionState = []
        session['state'] = sessionState
    else:
        output = openai_create(prompt)
        outputj = json.loads(output)
        intention = outputj['i']
        answer = outputj['a']
        if intention =='greeting':
            answer=answer
        elif intention == 'archive':
            answer = "您查询的'往期文章'功能正在建设中🚧预计明天上线"
        elif intention =='relevant':
            answer = "您查询的'相关文章'功能正在建设中🚧预计明天上线"
        else:
            sessionState.append([userinput, answer])
            #print("sessionState1:" + sessionState.__str__())
            session['state'] = sessionState


    print ('answer: '+ answer)
    return answer


#defining the conversation function
def openai_create(prompt):

    response = openai.Completion.create(
    engine = cfg.deployment_name,
    prompt = prompt,
    
    #lower value means that the generated text will have a low level of randomness and creativity
    temperature = 0.3,
    max_tokens = 150,
    
    # Set the top_p parameter to 0.9 to sample the next token based on the top 90% of likelihoods
    top_p = 0.9,
    # Set the frequency penalty to 0.5 to reduce the relevance score of documents that contain the search terms too frequently
    frequency_penalty = 0.3,
    # Set the presence penalty to 0.5 to reduce the relevance score of documents that do not contain the search terms at all
    presence_penalty = 0.5,
    #stop = '\n' #this will result in missing reply when leading with '\n'
    )

    return response.choices[0].text.replace('\n', '').replace(' .', '.').strip()
