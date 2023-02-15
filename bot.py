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

    s = list(itertools.chain(*sessionState))
    s.append(userinput)
    prompt = ' '.join(s)

    print ('prompt: '+ userinput)
    answer=''

    if userinput in ["hi", "hello", "你好", "您好"]:
        answer = "欢迎来到系统之美，ChatGPT正在为您服务"
    elif userinput in ["bye", "quit", "exit", "聊点别的"]:
        answer = "Bye!"
        sessionState = []
    else:
        answer = openai_create(prompt)
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
