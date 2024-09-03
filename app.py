from flask import Flask, request, jsonify
import openai
import os
import json
from dotenv import load_dotenv
import requests
from threading import Thread

# 환경 변수 로드
load_dotenv()  # .env 파일을 로드하여 환경 변수를 설정
openai.api_key = os.getenv('OPENAI_API_KEY')  # 환경 변수에서 OpenAI API 키 가져오기

app = Flask(__name__)

# 세션 데이터를 저장할 파일 경로
session_file_path = 'session_data.json'

# 세션 파일 초기화
if not os.path.exists(session_file_path):
    with open(session_file_path, 'w') as f:
        json.dump({}, f)  # 빈 JSON 객체 저장

def load_session_data():
    """세션 데이터를 파일에서 로드"""
    with open(session_file_path, 'r') as f:
        return json.load(f)

def save_session_data(data):
    """세션 데이터를 파일에 저장"""
    with open(session_file_path, 'w') as f:
        json.dump(data, f)

def analyze_intent(user_input):
    """사용자 입력을 분석하여 의도를 식별"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "다음 사용자 입력의 의도를 다음 중 하나로 식별하세요: 여행지 추천, 추천, 알 수 없음. 관련이 있다면 '음식이 맛있다', '낭만적이다', '별이 많다', '밤하늘이 아름답다'와 같은 특정 키워드도 식별하세요."},
                {"role": "user", "content": f"User input: '{user_input}'"}
            ],
            max_tokens=50,
            temperature=0.2
        )
        
        # GPT 응답을 문자열로 받아오고 로그로 출력합니다.
        intent = response['choices'][0]['message']['content']
        intent_parts = intent.split("\n")
        intent = None
        keywords = []
        
        for part in intent_parts:
            if "의도:" in part:
                intent = part.split("의도:")[-1].strip().lower()
            if "관련 키워드:" in part:
                keyword_str = part.split("관련 키워드:")[-1].strip().lower()
                keywords = [kw.strip() for kw in keyword_str.split(",")]

        if not keywords:  # 키워드가 없다면 None으로 설정
            keywords = None

        return intent, keywords
    except Exception as e:
        print(f"Error in analyze_intent: {e}")
        return "unknown", None

def get_travel_recommendation_from_gpt(keywords):
    """GPT를 사용하여 키워드에 기반한 해외 여행지 추천 (한글 응답)"""
    for attempt in range(3):  # 최대 3번 재시도
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "다음 키워드를 바탕으로 대표적인 해외의 도시 하나만 추천해 주세요. 도시 이름만 반환해주세요"},
                    {"role": "user", "content": f"Keywords: {', '.join(keywords)}"}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            city = response['choices'][0]['message']['content'].strip()
            return city

        except openai.error.RateLimitError as e:
            print(f"Rate limit error: {e}")
            if "please try again in" in str(e).lower():
                delay_time = int(str(e).split("in ")[-1].split("s")[0]) + 1  # 오류 메시지에서 지연 시간 추출
                print(f"Waiting for {delay_time} seconds before retrying...")
                time.sleep(delay_time)  # 지연 후 재시도
            else:
                time.sleep(20)  # 기본 지연 시간
        
        except Exception as e:
            print(f"Error in get_travel_recommendation_from_gpt: {e}")
            return "추천하는 도시에 문제가 발생했습니다."
    
    # 최대 재시도 후 실패 시 메시지
    return "요청이 여러 번 실패했습니다. 나중에 다시 시도해 주세요."
    
def get_response(intent, keywords=None):
    """의도와 키워드에 따른 응답 생성"""
    session_data = load_session_data()
    last_intent = session_data.get('last_intent')

    if intent == "여행지 추천" and last_intent == "awaiting keyword" and not keywords:
        return "어떤 여행지를 추천해드릴까요?", "어떤 여행지를 추천해드릴까요?"

    if last_intent == "awaiting keyword" and keywords:
        city = get_travel_recommendation_from_gpt(keywords)
        session_data['last_intent'] = None  # 상태 초기화
        save_session_data(session_data)
        return f"추천드리는 도시 : {city}", city
    
    if intent == "여행지 추천" and not keywords:
        session_data['last_intent'] = "awaiting keyword"  # 키워드 기다리는 상태로 설정
        save_session_data(session_data)
        return "어떤 여행지를 추천해드릴까요?", "어떤 여행지를 추천해드릴까요?"
    
    if intent == "여행지 추천" and keywords:
        city = get_travel_recommendation_from_gpt(keywords)
        return f"추천드리는 도시 : {city}", city
    
    session_data['last_intent'] = None  # 기타 상황에서 상태 초기화
    save_session_data(session_data)
    return "죄송합니다, 이해하지 못했습니다.", None

@app.route('/process', methods=['POST'])
def process_request():
    """백엔드 서버로부터 데이터를 받아 처리하고 결과를 다시 전송하는 엔드포인트"""
    data = request.json
    user_input = data.get('input')
    callback_url = data.get('callback_url')  # 결과를 전송할 백엔드 서버의 URL

    # 1. 입력을 받았다는 상태를 먼저 백엔드 서버로 전송
    status_update = {'status': 'received', 'message': 'Input received by AI server'}
    try:
        status_response = requests.post(callback_url, json=status_update)
        status_response.raise_for_status()
        print("입력 상태 업데이트를 백엔드 서버로 전송했습니다.")
    except requests.exceptions.RequestException as e:
        print(f"입력 상태 업데이트 전송 중 오류 발생: {e}")
        return jsonify({'status': 'failure', 'message': 'Failed to update status'}), 500

    # 2. AI 서버에서 사용자 입력 처리
    intent, keywords = analyze_intent(user_input)
    message, city = get_response(intent, keywords)

    # 결과를 JSON 파일로 저장
    result_data = {
        'intent': intent,
        'message': message,
        'recommendation': city
    }
    with open('result.json', 'w') as json_file:
        json.dump(result_data, json_file)

    # 3. 처리된 결과를 백엔드 서버로 전송
    try:
        response = requests.post(callback_url, json=result_data)
        response.raise_for_status()
        return jsonify({'status': 'success', 'message': 'Result sent to backend server'}), 200
    except requests.exceptions.RequestException as e:
        print(f"결과 전송 중 오류 발생: {e}")
        return jsonify({'status': 'failure', 'message': 'Failed to send result'}), 500

def run_ai_server():
    """AI 서버 실행"""
    app.run(host='0.0.0.0', port=5000)  # AI 서버는 5000 포트에서 실행

if __name__ == '__main__':
    # AI 서버 실행
    run_ai_server()
