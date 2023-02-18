import json
from werobot import WeRoBot
import config as cfg
import openai
import itertools
#import re
import prettytable

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

    try:
        output = openai_create(prompt)
        print('raw response: '+ output)
        #cleansing for json load
        output = output.lstrip('\n').replace(' .', '.').strip().replace('\n', '\\n')
        
        if not output.lower().startswith('{"i":'):
            output = '{"i":"na","a":"' + output + '"}'
        outputj = json.loads(output)
        intention = outputj['i']
        answer = outputj['a']
        if intention =='greeting':
            answer=answer or 'Ok, 那聊啥呢？'
        elif intention == 'reset':
            answer=answer
            sessionState = []
            session.pop('state',None)
        elif intention == 'archive':
            answer = "您查询的'往期文章'功能正在建设中🚧预计明天上线"
        elif intention =='relevant':
            answer = "您查询的'相关文章'功能正在建设中🚧预计明天上线"
        elif answer =='':
            answer = '抱歉，这个我不会，试试别的话题。'
            return answer
        else:
            answer = answer.replace('\\n', '')
            sessionState.append([userinput, answer])
            #print("sessionState1:" + sessionState.__str__())
            session['state'] = sessionState

        #convert answer to ascii table if it contains a markdown table, tencent doesn't allow html
        if answer.count('|') >= 2:
            answer = markdown2ascii_table(answer)
        else:
            print("no markdown table")
            
    except Exception as e:
        # handle the exception
        print(f"Opps: {e}")

    print (answer)
    return answer

#conver markdown table to ascii
def markdown2ascii_table(markdown_str:str):
    # markdown_str = "| 国家 | GDP | 人均GDP |\n| :---: | :---: | :---: |\n| 美国 | 21.4万亿美元 | 62,794美元 |\n| 中国 | 14.6万亿美元 | 10,223美元 |\n| 日本 | 5.2万亿美元 | 43,521美元 |"
    print('markdown: ' + markdown_str)

    #Split the Markdown string into rows and columns
    rows = markdown_str.split("\n")[0:]

    header_row_number = None
    for i, row in enumerate(rows):
        if '|' in row:
            header_row_number = i
            break

    # print(rows)
    header_row = rows[header_row_number].strip().split("|")[1:-1]
    print(header_row)
    # Remove any unnecessary whitespace characters from the header row
    headers = [h.strip() for h in header_row]
    # print(headers)

    # Create a new table with the headers
    table = prettytable.PrettyTable(headers)

    alignment_row_number=header_row_number+1
    data_start_row_number = alignment_row_number #assume no alignment row first
    # Check if the alignment_row string has an alignment row
    alignment_row_str= rows[alignment_row_number].strip()
    if '|' in alignment_row_str and '-' in alignment_row_str:
    # Create a list of alignment strings based on the Markdown alignment row
        alignment_row = alignment_row_str.split("|")[1:-1]
        print (alignment_row)
        alignments = [        
            "l" if alignment.startswith(":") and alignment.endswith("-") else
            "r" if alignment.startswith("-") and alignment.endswith(":") else
            "c"
            for alignment in alignment_row
        ]   
        print (alignments)
        data_start_row_number=alignment_row_number+1
        #table.align = alignments

    # Get the number of columns in the table
    num_columns = len(table.field_names)

    # Add the rows to the table
    #print (f"row count: {rows.count}")
    for row in rows[data_start_row_number:]:
        new_data_row = [c.strip() for c in row.split("|")[1:-1]]
        try:
            # Add empty cells to the new row
            if len(new_data_row)<num_columns:
                while len(new_data_row) < num_columns:
                    new_data_row.append("")
            elif len(new_data_row)>num_columns:
                new_data_row = new_data_row[:num_columns]
            table.add_row(new_data_row)
        except Exception as e:
            # handle the exception
            print(f"adding data row: {e}")

    # Set the table style
    table.set_style(prettytable.SINGLE_BORDER)
    table_string = table.get_string()
    print(table_string)
    return table_string

#defining the conversation function
def openai_create(prompt):

    response = openai.Completion.create(
    engine = cfg.deployment_name,
    prompt = prompt,
    
    #lower value means that the generated text will have a low level of randomness and creativity
    temperature = 0.3,
    max_tokens = 350,
    
    # Set the top_p parameter to 0.9 to sample the next token based on the top 90% of likelihoods
    top_p = 0.9,
    # Set the frequency penalty to 0.5 to reduce the relevance score of documents that contain the search terms too frequently
    frequency_penalty = 0.3,
    # Set the presence penalty to 0.5 to reduce the relevance score of documents that do not contain the search terms at all
    presence_penalty = 0.5,
    #stop = '\n' #this will result in missing reply when leading with '\n'
    )

    return response.choices[0].text#.replace('\n', '').replace(' .', '.').strip()
