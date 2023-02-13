from werobot import WeRoBot
import config as cfg
import openai
import itertools

mybot = WeRoBot(token=cfg.token)
mybot.config["APP_ID"] = cfg.appid
mybot.config['ENCODING_AES_KEY'] = cfg.aeskey
openai.api_key = cfg.openai_key


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
    userinput = message.content
    sessionState = []
    if 'state' in session:
        sessionState = session.get('state',[])
        print("sessionState2:" + sessionState.__str__())

    s = list(itertools.chain(*sessionState))
    s.append(userinput)
    prompt = ' '.join(s)

    print (userinput)
    answer=''

    if userinput.strip().lower() in ["hi", "hello", "你好", "您好"]:
        answer = "欢迎来到系统之美，ChatGPT正在为您服务"
    else:
        answer = openai_create(prompt)
        sessionState.append([userinput, answer])
        print("sessionState1:" + sessionState.__str__())
        session['state'] = sessionState

    print (answer)
    return answer


#defining the conversation function
def openai_create(prompt):

    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=prompt,
    temperature=0.9,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0.6,
    stop=[" Human:", " AI:"]
    )

    return response.choices[0].text   
