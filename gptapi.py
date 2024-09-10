import openai
from dotenv import load_dotenv
import os
import json
import re

# OpenAI API 키 설정
load_dotenv(dotenv_path='kakaobootcamp/team/travel/chatbot/chatbot/.env')  # .env 파일을 로드하여 환경 변수를 설정
openai.api_key = os.getenv('OPENAI_API_KEY')  # 환경 변수에서 OpenAI API 키 가져오기

def find_aim(user_input):
    """사용자의 입력을 의도 분류하는 함수"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that classifies user intents in Korean. Your task is to identify the user's intent based on their input and categorize it into predefined intent labels. Possible intent labels include: 여행 추천 요청, 정보 검색, 일반 질문, 도움 요청, 인사, 종료, 기타."
            },
            {
                "role": "user",
                "content": f"{user_input}\n\nPlease classify the intent into one of the following categories: [여행 추천 요청], [정보 검색], [일반 질문], [도움 요청], [인사], [종료], [기타]. Provide only the intent label without additional explanation."
            }
        ],
        max_tokens=100,
        temperature=0  # 의도 분류의 정확성을 높이기 위해 낮은 온도 설정
    )
    return response['choices'][0]['message']['content'].strip()

def travel_recommend(user_input):
    """여행지 추천을 생성하고 결과를 JSON 형식으로 반환하는 함수"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that provides travel recommendations in Korean. Your task is to suggest overseas travel destinations based on the user's preferences and provide detailed information such as key attractions, activities, food, and best visiting seasons."
            },
            {
                "role": "user",
                "content": f"{user_input}\n\nBased on the input, recommend an overseas travel destination. Organize the output into the following sections: [추천 여행지], [주요 명소], [추천 계절], [나라 이름](나라 이름만 출력해줘). Provide detailed and relevant recommendations for the user's preferences."
            }
        ],
        max_tokens=1000,
        temperature=0.7  # 다양하고 흥미로운 추천을 위해 온도를 약간 높게 설정
    )

    # GPT-4 응답 텍스트 추출
    response_text = response['choices'][0]['message']['content'].strip()

    # 응답 파싱하여 JSON 데이터로 변환
    return parse_recommendation_to_json(response_text)

def parse_recommendation_to_json(response_text):
    """
    GPT-4 응답을 파싱하여 JSON 형식으로 변환하는 함수.
    각 섹션을 찾아 데이터를 추출하고 JSON 객체로 반환합니다.
    """
    # 추천 여행지와 이유를 함께 추출
    travel_dest_match = re.search(r'\[추천 여행지\]\n(.+?)(?=\n\[|$)', response_text, re.DOTALL)
    travel_dest_and_reason = travel_dest_match.group(1).strip() if travel_dest_match else ''

    # 도시 이름과 추천 이유 분리
    # 예: "오사카, 일본을 추천드립니다."
    travel_dest_parts = travel_dest_and_reason.split("을 추천드립니다.")
    travel_dest = travel_dest_parts[0].split(',')[0].strip() if len(travel_dest_parts) > 1 else travel_dest_and_reason
    reason = "을 추천드립니다.".join(travel_dest_parts).strip()  # 전체를 이유로 사용

    # 주요 명소 추출 및 리스트로 변환
    landmarks_match = re.search(r'\[주요 명소\]\n(.+?)(?=\n\[|$)', response_text, re.DOTALL)
    landmarks = landmarks_match.group(1).strip() if landmarks_match else ''
    # 줄별로 나누어 주요 명소 리스트 생성
    landmarks_list = [line.strip() for line in landmarks.split('\n') if line.strip() and not line.startswith('[')]

    # 추천 계절 추출
    season_match = re.search(r'\[추천 계절\]\n(.+?)(?=\n\[|$)', response_text, re.DOTALL)
    season = season_match.group(1).strip() if season_match else ''

    # 도시 이름 추출
    city_match = re.search(r'\[나라 이름\]\n(.+?)(?=\n\[|$)', response_text, re.DOTALL)
    city = city_match.group(1).strip() if city_match else ''

    # JSON 데이터 형식으로 변환
    recommendation_data = {
        "추천여행지": city,  # 도시 이름만
        "추천이유": reason,  # 전체 이유
        "주요명소": landmarks_list,
        "추천계절": season
    }

    return recommendation_data

