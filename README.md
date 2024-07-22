# 한바퀴  - 당신의 여행 이야기를 나누는 공간

한바퀴는 사용자들이 자신의 여행 경험을 공유하고, 다른 사용자들과 소통하며 여행 정보를 얻을 수 있는 커뮤니티 기반 서비스입니다.

## 주요 기능:

- **게시글 작성 및 공유**: 사진, 동영상, 글 등 다양한 형태의 게시물을 작성하고 공유할 수 있습니다.
- **지역 기반 정보**: 여행 지역에 대한 상세 정보 (날씨, 인기 명소, 추천 여행 코스 등)를 제공합니다.
- **맞춤형 추천**: 사용자의 관심 지역 및 활동 기반으로 맞춤형 여행 정보와 게시물을 추천합니다.
- **소셜 로그인**: 간편하게 구글, 카카오, 네이버 계정으로 로그인할 수 있습니다.
- **댓글 및 좋아요**: 게시글에 댓글을 달고 좋아요를 표시하여 다른 사용자와 소통할 수 있습니다.
- **검색 기능**: 원하는 지역이나 키워드로 게시글을 검색할 수 있습니다.

## 앱별 기능 설명:

| 앱 이름  | 기능 설명                           |
| -------- | ----------------------------------- |
| users    | 회원 관리: 회원가입, 로그인, 프로필 관리, 소셜 로그인 연동 등 |
| posts    | 게시글 관리: 게시글 작성, 수정, 삭제, 조회, 이미지 업로드 등 |
| locations| 지역 정보 관리: 지역 정보 조회, 지역별 게시글 필터링, 날씨 정보 연동 등 |
| weather  | 날씨 정보 관리: 기상청 API를 통해 날씨 정보 수집 및 제공 |
| search   | 검색 기능: Elasticsearch 기반 게시글 검색 기능 제공 |

## 아키텍처:

- **클라이언트**: React (또는 다른 프론트엔드 프레임워크)
- **백엔드**: Django, Django REST Framework
- **데이터베이스**: PostgreSQL (RDS)
- **검색 엔진**: Elasticsearch
- **캐시**: Redis
- **이미지 저장소**: AWS S3
- **배포**: Docker, AWS EC2

## 기술 스택:

- **언어**: Python
- **웹 프레임워크**: Django
- **REST API 프레임워크**: Django REST Framework
- **데이터베이스**: PostgreSQL
- **ORM**: Django ORM
- **검색 엔진**: Elasticsearch
- **캐시**: Redis
- **클라우드 서비스**: AWS (EC2, RDS, S3)
- **인증**: OAuth 2.0 (Google, Kakao, Naver), JWT
- **API 문서**: Swagger
- **스크래핑**: BeautifulSoup4, requests
- **비동기 작업**: Celery
- **기타**: djangorestframework-simplejwt, django-cors-headers, django-environ, django-storages, boto3, python-decouple
