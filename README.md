#wWchatGPT
Flask+Docker部署的微信公众号机器人对接ChatGPT或fine-tuned OpenAI model on Azure
模拟ChatGPT多轮对话中保持上下文

main.py 入口
bot.py 负责对接API

将文件 config template.py 改名为 config.py，并根据自己账号更改里面的key

目前gunicorn 使用sync worker, 欢迎小伙伴贡献代码
