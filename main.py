'''
def deco(fn):
    def deco_hello():
        print("=" * 20)
        fn()
        print("=" * 20)
    return deco_hello

@deco
def hello():
    print("hello batman")

hello()
'''

import discord  # 디스코드 API를 사용하기 위한 메인 라이브러리를 불러옵니다.
from discord import app_commands  # 슬래시 명령어(예: /인사)를 관리하기 위한 모듈을 불러옵니다.
from datetime import datetime, timedelta
import requests

def getYesterday():
        
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    return yesterday.strftime('%Y-%m-%d')

def getJson(url):

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        data = {"error":"ERROR: " + str(response.status_code) + " 오류 발생"}
    
    return data

# 봇의 고유 식별 키(Token)입니다. (주의: 절대로 외부에 노출되면 안 됩니다!)
token = "MTQ2NzUwNjk0ODU3NTMzNDUyMQ.GuV5Zu.XDSKffeI9ykFYST1VwwDNiKaJoXvUTc3hlXuMA"
# 특정 채널의 ID입니다. (현재 코드 내에서는 정의만 되어 있고 실제 사용되지는 않고 있습니다.)
channel_id = "1467522920891814048"

# 봇의 권한(Intents)을 설정합니다. 기본 설정(default)을 사용합니다.
intents = discord.Intents.default()
# 설정한 권한을 가지고 디스코드 서버와 통신할 '클라이언트(봇 객체)'를 생성합니다.
client = discord.Client(intents=intents)

# 슬래시 명령어를 봇에 연결해 주는 '명령어 트리'를 생성합니다.
tree = app_commands.CommandTree(client)

# '/인사'라는 이름의 슬래시 명령어를 정의합니다.
@tree.command(name="인사", description="인사 하기")
async def hello(interaction: discord.Interaction):
    # 사용자가 명령어를 입력하면 "안녕"이라는 메시지로 응답(response)합니다.
    await interaction.response.send_message("안녕")

# Wordle 전날 정답 가져오는 함수
@tree.command(name="워들정답", description="전날 워들 정답을 가져옵니다.")
async def wordleAnswer(interaction: discord.Interaction):
    
    answer_date = getYesterday()
    wordle_json_url = "https://www.nytimes.com/svc/wordle/v2/" + answer_date + ".json"
    wordle_json = getJson(wordle_json_url)
    
    wordle_answer = ""
    final_message = ""
    try:
        wordle_answer = wordle_json['solution'].upper()
        final_message = f"**{answer_date}**의 워들 정답은 _{wordle_answer}_입니다."
    except:
        final_message = wordle_json['error']

    await interaction.response.send_message(final_message)
    

# 봇이 켜졌을 때(준비되었을 때) 실행되는 이벤트 함수입니다.
@client.event
async def on_ready():
    # 작성한 슬래시 명령어들을 디스코드 서버에 동기화(업데이트)합니다.
    # 이 과정이 있어야 디스코드 채팅창에 /인사 가 나타납니다.
    await tree.sync()
    print(f"봇이 {client.user} 상태로 로그인되었습니다.") # 로그 출력을 추가하면 확인이 쉽습니다.

# 설정한 토큰을 사용하여 봇을 실제로 실행합니다.
client.run(token)