#sql data base 파일 
#database 스키마는 총 세개의 테이블로 구성되어 있음
#1. user : 사용자 정보를 저장하는 테이블
#2. post : 사용자가 작성한 게시글 정보를 저장하는 테이블
#3. comment : 사용자가 작성한 댓글 정보를 저장하는 테이블

import sqlite3 #  sqlite3 모듈을 import

# 데이터베이스 초기화 하는 함수 정의
def init_database(db_path):
    #데이터 베이스 연결 생성
    conn = sqlite3.connect(db_path)
    #커서 생성
    cursor = conn.cursor()
      # issues 테이블 생성 쿼리 실행
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            assignee TEXT,
            status TEXT,
            created_at DATETIME DEFAULT CURRENT_DATE,
            updated_at DATETIME DEFAULT CURRENT_DATE
        )
    ''')
    
    # comments 테이블 생성 쿼리 실행
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            issue_id INTEGER,
            comment_text TEXT,
            author TEXT,
            created_at DATETIME DEFAULT CURRENT_DATE,
            FOREIGN KEY (issue_id) REFERENCES issues(id)
        )
    ''')
    
    # team_members 테이블 생성 쿼리 실행
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            name TEXT PRIMARY KEY,
            email TEXT NOT NULL
        )
    ''')
    # 변경사항 커밋
    conn.commit()
    # 데이터베이스 연결 종료
    conn.close()

    # 이슈 추가 함수 정의
def add_issue(title, description, assignee, status, db_path):
    # 데이터베이스 연결 생성
    conn = sqlite3.connect(db_path)
    # 커서 객체 생성
    cursor = conn.cursor()
    
    # 이슈 추가 쿼리 실행
    cursor.execute('''
        INSERT INTO issues (title, description, assignee, status)
        VALUES (?, ?, ?, ?)
    ''', (title, description, assignee, status))
    
    # 마지막으로 추가된 이슈의 ID 가져오기
    issue_id = cursor.lastrowid
    # 변경사항 커밋
    conn.commit()
    # 데이터베이스 연결 종료
    conn.close()
    
    # 추가된 이슈의 ID 반환
    return issue_id