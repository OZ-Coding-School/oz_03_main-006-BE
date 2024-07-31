# 한바퀴  - 당신의 여행 이야기를 나누는 공간

한바퀴는 사용자들이 자신의 여행 경험을 공유하고, 다른 사용자들과 소통하며 여행 정보를 얻을 수 있는 커뮤니티 기반 서비스입니다.

## 주요 기능:

- **게시글 작성 및 공유**: 사진, 동영상, 글 등 다양한 형태의 게시물을 작성하고 공유할 수 있습니다.
- **지역 기반 정보**: 여행 지역에 대한 상세 정보 (날씨, 인기 명소, 추천 여행 코스 등)를 제공합니다.
- **사용자 맞춤 기능**: 사용자의 관심 지역 및 좋아요한 게시물 보기를 통해 나의 여행의 계획에 필요한 정보를 수집할 수 있습니다. 
- **댓글 및 좋아요**: 게시글에 댓글을 달고 좋아요를 표시하여 다른 사용자와 소통할 수 있습니다.
- **검색 기능**: 원하는 지역이나 키워드로 게시글을 검색할 수 있습니다.
- **프로필 커스텀기능**: 여러분의 개성에 맞게 프로필을 수정해보세요!

## 앱별 기능 설명:

| 앱 이름  | 기능 설명                           |
| -------- | ----------------------------------- |
| users    | 회원 관리: 회원가입, 로그인, 프로필 관리 등 |
| boards   | 게시글 관리: 게시글 작성, 수정, 삭제, 조회, 이미지 업로드 등 |
| locations| 지역 정보 관리: 지역 정보 조회, 지역별 게시글 필터링, 날씨 정보 연동 등 |
| profiles | 회원가입한 사용자의 닉네임, 사진 수정 및 좋아요한 컨텐츠 보기  |
| weather  | 날씨 정보 관리: 기상청 API를 통해 날씨 정보 수집 및 제공 |
| search   | 검색 기능: Elasticsearch 기반 게시글 검색 기능 제공 |

## 아키텍처:

- **클라이언트**: React (또는 다른 프론트엔드 프레임워크)
- **백엔드**: Django, Django REST Framework
- **데이터베이스**: PostgreSQL (RDS)
- **검색 엔진**: Elasticsearch
- **이미지 저장소**: AWS S3
- **배포**: Docker, AWS EC2

## 기술 스택:

- **언어**: Python
- **웹 프레임워크**: Django
- **REST API 프레임워크**: Django REST Framework
- **데이터베이스**: PostgreSQL
- **ORM**: Django ORM
- **검색 엔진**: Elasticsearch
- **클라우드 서비스**: AWS (EC2, RDS, S3)
- **인증**: JWT
- **API 문서**: Swagger
- **스크래핑**: BeautifulSoup4, requests
- **동기 작업**: Selenium
- **기타**: djangorestframework-simplejwt, django-cors-headers, django-environ, django-storages, boto3, python-decouple, crontab


## 테스트 고려사항(기능 구현 완료하고 정상작동하는지 한번씩 해보기!)

- 1. 유닛테스트 : 

  pytest와 같은 테스트 프레임워크를 사용하여 모델, 뷰, 시리얼라이저의 유닛 테스트를 실행합니다.

- 2. 통합테스트 :

  API 엔드포인트에 대한 통합 테스트를 통해 전체 기능의 흐름이 정상적인지 확인합니다.

- 3. CSRF 보호 테스트:

  인증이 필요한 API 엔드포인트에서 CSRF 토큰이 제대로 처리되는지 확인합니다.
	
- 4. 보안 테스트:
 
   HTTPS 설정 및 JWT 인증을 통해 보안이 제대로 적용되었는지 검증합니다.
	
- 5. 부하 테스트:

   Docker 환경에서 locust와 같은 도구를 사용하여 애플리케이션의 부하를 테스트합니다.
