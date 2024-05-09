# 📰 Project: Sparta News
스파르타 AI-6기 9조 : DRF를 활용하여, 레퍼런스용 게시글을 만들 수 있는 API 뉴스 사이트를 구현

<br>

## 🆕 Project Introduction
사용자가 원하는 내용으로 기사의 제목과 내용을 기입하고 사이트 이용자에게 공유할 수 있는 뉴스형 레퍼런스 사이트

<br>

## ⏲️ Development time
- 2024.05.03(금) 13:00 ~ 2023.05.10(금) 13:00


<br>

## 💻 Development Environment
- **Programming Language** : Python 3.9, 3.10
- **Web Framework** : DJANGO DRF
- **Database** : SQLite (for development and testing)
- **IDE** : Pycharm, Vscode
- **Version Control** : Git, GitHub
- **Communication Tool** : Slack, Zep
  
<br>

## Project Result_ API
- https://www.notion.so/teamsparta/API-4ad9d38718154630b8a8791f81087527
  
<br>


## 📌 Key Features

### 1. Auth
   - 회원가입, 로그인, 로그아웃, 프로필 조회(작성자,가입일,소개 노출), 회원정보 수정, 회원탈퇴 기능
   - 회원 가입 시 입력한 username 및 password 정보 일치 시 회원 로그인 가능, 정보 불일치 시 로그인 불가
   - 로그인 사용자에 한해 로그아웃 및 회원정보 수정 및 회원탈퇴 가능


### 2. Product_Post CRUD
  - 게시글 작성자가 아니더라도 목록조회 가능 
  - 로그인 사용자는 게시글 생성, 목록조회, 게시글 수정 및 삭제 가능
  - 로그인 사용자의 게시글에 한해서만 수정 및 삭제가 가능
  - 게시글 생성일자, 좋아요 개수, 댓글 개수를 통해 내부적으로 연산한 point가 높은 순으로 게시글을 정렬하여 조회화면에 출력
  - title, content, url 공백일 시 게시글 작성 불가


### 3. Comment CRD
   - 로그인 하지 않은 사용자도 댓글 열람 가능
   - 로그인 사용자에 한해 댓글 생성 가능
   - 게시물이 작성되어 있어야 댓글 생성 가능
   - 게시글 작성자에 한해 댓글에 대한 수정,삭제가 가능
   - title, content에 포함된 단어와 username을 keyword로 게시글 검색 가능
   - 로그인 사용자에 한해 특정 게시글을, 사용자 계정에 등록된 이메일로 전송 가능
     
     
### 4. LIKE
   - 로그인 사용자에 한해 특정 게시글을 관심 글로 등록하거나 해제 가능
   - 댓글 수, 관심 수, 등록 일자에 따른 Article 점수 부여하고, 부여된 점수에 따라 내림차순으로 결과를 반환
 
     

<hr>



### 1. Auth
  - Member registration, login, logout, profile viewing (author, registration date, introduction display),
    user information modification, and account withdrawal functionalities.
  - Upon registration, users can login if the provided username and password match; otherwise, login is not permitted.
  - Only logged-in users can perform actions such as logout, modifying user information, and deleting accounts.


### 2. Product_Post CRUD:
  - Even non-logged-in users can browse the list of posts.
  - Logged-in users can create posts, browse the list of posts, and edit or delete their own posts.
  - Only the author of a post can edit or delete it.
  - Posts can be sorted in descending order of interest levels of logged-in users.
  - Posts cannot be created if the title, content, or URL fields are left empty.


### 3. Comment CRD:
  - Comments can be viewed by non-logged-in users.
  - Logged-in users can create comments.
  - Comments can only be created if there is an existing post.
  - Post authors can edit or delete comments on their posts.
  - Posts can be searched using keywords found in titles or content.
  - Logged-in users can send specific posts to their registered email addresses.


### 4. LIKE:
  - Logged-in users can register or unregister specific posts as favorites.
  - Articles are scored based on the number of comments, likes,
    and registration date, and the results are returned in descending order based on the scores.

     

## 📄 ERD:
<img width="565" alt="스크린샷 2024-05-09 오후 12 26 44" src="https://github.com/luna-negra/sparta_news_group_9/assets/161671057/574742da-e0e9-49f9-a40e-a3735b68bd6f">

