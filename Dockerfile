# Python 3.10.11을 베이스 이미지로 사용합니다.
FROM python:3.10.11

# 작업 디렉토리를 설정합니다.
WORKDIR /app

# requirements.txt 파일과 Python 소스 파일들을 컨테이너로 복사합니다.
COPY . .


# 필요한 Python 패키지들을 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# Flask 서버가 외부에서 접근 가능하도록 포트를 엽니다.
EXPOSE 5000

# Flask 서버를 실행합니다.
CMD ["python", "app.py"]
