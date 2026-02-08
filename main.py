'''
이거 지울건가요
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

import os
from dotenv import load_dotenv

import aiohttp
from aiohttp import web


#initialize

# 헬스체크
async def health_check(request):
  return web.Response(text="OK", status=200)

async def start_web_server():
  app = web.Application()
  app.router.add_get('/health', health_check) # Health Check API 추가
  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, '0.0.0.0', 8000)
  await site.start()

# 환경변수 호출 및 토큰 등록
load_dotenv()
token = os.environ['DISCORD_TOKEN']


# 봇의 권한(Intents)을 설정합니다. 기본 설정(default)을 사용합니다.
intents = discord.Intents.default()
# 설정한 권한을 가지고 디스코드 서버와 통신할 '클라이언트(봇 객체)'를 생성합니다.
client = discord.Client(intents=intents)

# 슬래시 명령어를 봇에 연결해 주는 '명령어 트리'를 생성합니다.
tree = app_commands.CommandTree(client)



#functions
def getYesterday():
    today = datetime.now() # today로 썼는데 나중에 12시 자동으로 뿌리게 하기 위해서 time_now 같은 변수명으로 바꾸는게 좋을듯
    yesterday = today - timedelta(days=1)
    
    return yesterday.strftime('%Y-%m-%d')

def getJson(url):
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        data = {"error":"ERROR: " + str(response.status_code) + " 오류 발생"}
    
    return data




#functions and initialize for kordle
#------------------------------------

kordle_start_date = datetime(2022, 1, 1) #꼬들 단어리스트 첫 정답 날짜

#open kordle_answers.txt
with open('./resources/answers/kordle_answers.txt', 'r', encoding='utf-8') as f:
    kordle_answers = [line.strip() for line in f.readlines() if line.strip()] #list comprehension이라는 방식이라네요 잘은 모르겠음

#calculate yesterday kordle index
def calculateKordleAnswer():
    yesterday_datetime = datetime.strptime(getYesterday(),'%Y-%m-%d') #datetime을 문자열로 변환했다 다시 datetime객체로 변환중..... 위에서 수정해야 할듯 
    kordleAnswer_index = (yesterday_datetime - kordle_start_date).days #시작 날짜 - 어제날짜 = 꼬들 답 인덱스(줄 번호)
    
    kordle_finalAnswer = kordle_answers[kordleAnswer_index] 
    return kordle_finalAnswer

#------------------------------------



# Commands 
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
    
    
# Wordle 특정 날짜 정답
@tree.command(name="워들정답날짜", description="특정 날짜의 워들 정답을 가져옵니다.")
@app_commands.describe(target_date = "MM-DD 형식으로 입력 (예: 01-12)")
@app_commands.rename(target_date = "날짜")
async def dateWordleAnswer(interaction: discord.Interaction, target_date: str): #typehint
    
    current_year = datetime.today().strftime('%Y') #해당 연도 문자열 반환
    
    wordle_answer = ""
    final_message = ""
    
    #입력 target_date의 유효성 검사
    try:
        target_date = datetime.strptime(f"{current_year}-{target_date}", '%Y-%m-%d') #current_year + '-' + targetdate 를 datetime으로 변환
    except ValueError:
        final_message = "오류: 올바르지 않은 형식입니다. (올바른 예: 01-12)"
        await interaction.response.send_message(final_message)
        return # 함수 종료

    target_date = datetime.strftime(target_date, '%Y-%m-%d')
    
    wordle_json_url = "https://www.nytimes.com/svc/wordle/v2/" + target_date + ".json"
    wordle_json = getJson(wordle_json_url)
    

    try:
        wordle_answer = wordle_json['solution'].upper()
        final_message = f"**{target_date}**의 워들 정답은 _{wordle_answer}_입니다."
    except:
        final_message = wordle_json['error']

    await interaction.response.send_message(final_message)

# Kordle 정답 가져오는 명령어
@tree.command(name="꼬들정답", description="전날 꼬들 정답을 가져옵니다.")
async def sendYesterdaykordleAnswer(interaction: discord.Interaction):

    answer_date = getYesterday()

    kordle_answer = ""
    final_message = ""
    
    try:
        kordle_answer = calculateKordleAnswer()
        final_message = f"**{answer_date}**의 꼬들 정답은 _{kordle_answer}_입니다."
    except:
        final_message = 'error'

    await interaction.response.send_message(final_message)



#bot startup
# 봇이 켜졌을 때(준비되었을 때) 실행되는 이벤트 함수입니다.
@client.event
async def on_ready():
    # 작성한 슬래시 명령어들을 디스코드 서버에 동기화(업데이트)합니다.
    # 이 과정이 있어야 디스코드 채팅창에 /인사 가 나타납니다.
    await tree.sync()
    print(f"봇이 {client.user} 상태로 로그인되었습니다.") # 로그 출력을 추가하면 확인이 쉽습니다.

# 설정한 토큰을 사용하여 봇을 실제로 실행합니다.
client.run(token)