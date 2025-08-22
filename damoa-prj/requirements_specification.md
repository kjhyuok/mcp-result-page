# API 문서 크롤링 및 Bedrock Knowledge Base 연동 에이전트 요구사항명세서

## 1. 프로젝트 개요

### 1.1 목적
웹 기반 4단계 워크플로우를 통한 API 연동 자동화 시스템 구축:
- **1단계**: 웹 크롤링 또는 문서 업로드를 통한 데이터 수집
- **2단계**: RAG 기반 API 탐색 및 간단한 연동 테스트
- **3단계**: 확정된 연동 방법에 대한 명세서 작성 및 검토
- **4단계**: 대화형 LLM을 통한 맞춤형 코드 생성 및 실행

### 1.2 대상 API
- **Shopify Admin GraphQL API**: https://shopify.dev/docs/api/admin-graphql/2024-10/queries/orders
- **Amazon Seller Partner API**: https://developer-docs.amazon.com/sp-api

### 1.3 기술 스택
- **프론트엔드**: React 18+, TypeScript, Tailwind CSS, Shadcn/ui
- **백엔드**: FastAPI, Python 3.9+
- **에이전트 프레임워크**: Strands Agents SDK
- **MCP 서버**: AWS Documentation MCP, Strands MCP
- **AI 모델**: Amazon Bedrock Claude 3.7 Sonnet
- **지식 베이스**: Amazon Bedrock Knowledge Base

## 2. 시스템 아키텍처

### 2.1 전체 구조
```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                           │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │   Step 1    │   Step 2    │   Step 3    │   Step 4    │  │
│  │ Data Input  │ API Search  │ Spec Review │ Code Gen    │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ Crawler     │ RAG Search  │ Spec Gen    │ Code Exec   │  │
│  │ Agent       │ Agent       │ Agent       │ Agent       │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 AWS Services                                │
│     Bedrock Knowledge Base + S3 + Bedrock Models           │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 프론트엔드 구조
```
src/
├── components/
│   ├── ui/                    # Shadcn/ui 컴포넌트
│   ├── steps/
│   │   ├── Step1DataInput.tsx
│   │   ├── Step2ApiSearch.tsx
│   │   ├── Step3SpecReview.tsx
│   │   └── Step4CodeGen.tsx
│   ├── common/
│   │   ├── ProgressBar.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── StatusIndicator.tsx
│   └── layout/
│       ├── Header.tsx
│       └── Sidebar.tsx
├── hooks/
│   ├── useWebSocket.ts
│   ├── useStepManager.ts
│   └── useApiClient.ts
├── services/
│   └── api.ts
├── types/
│   └── index.ts
└── App.tsx
```

## 3. 기능 요구사항

### 3.1 Step 1: 데이터 입력 단계

#### 3.1.1 웹 인터페이스
- **URL 입력**: 크롤링할 웹사이트 URL 입력 필드
- **파일 업로드**: 드래그 앤 드롭 문서 업로드 (PDF, MD, HTML)
- **크롤링 옵션**: 깊이, 범위 설정
- **실시간 진행률**: 크롤링 진행 상황 표시

#### 3.1.2 백엔드 처리
- **웹 크롤링 에이전트**: HTTP 요청, HTML 파싱, 콘텐츠 추출
- **문서 처리 에이전트**: 업로드된 파일 파싱 및 구조화
- **Knowledge Base 연동**: S3 업로드 및 동기화
- **WebSocket**: 실시간 진행 상황 전송

### 3.2 Step 2: API 탐색 및 테스트 단계

#### 3.2.1 웹 인터페이스
- **채팅 인터페이스**: RAG 기반 API 검색 대화창
- **API 정보 카드**: 찾은 API의 상세 정보 표시
- **간단 테스트 패널**: 인증 정보 입력 및 기본 호출 테스트
- **테스트 결과**: 응답 데이터 및 상태 표시

#### 3.2.2 백엔드 처리
- **RAG 검색 에이전트**: Knowledge Base 쿼리 및 결과 반환
- **API 테스트 에이전트**: 실제 API 호출 및 검증
- **결과 분석**: 응답 구조 분석 및 정리

### 3.3 Step 3: 명세서 작성 및 검토 단계

#### 3.3.1 웹 인터페이스
- **명세서 에디터**: 마크다운 기반 편집기
- **미리보기**: 실시간 명세서 렌더링
- **템플릿 선택**: 다양한 명세서 템플릿 제공
- **승인 버튼**: 명세서 확정 및 저장

#### 3.3.2 백엔드 처리
- **명세서 생성 에이전트**: Step 2 결과 기반 자동 생성
- **템플릿 엔진**: 표준화된 명세서 형식 적용
- **파일 저장**: 로컬/S3 저장

### 3.4 Step 4: 대화형 코드 생성 및 실행 단계

#### 3.4.1 웹 인터페이스
- **채팅 인터페이스**: LLM과의 대화형 코드 생성
- **코드 에디터**: 생성된 코드 편집 및 확인
- **실행 패널**: 코드 실행 및 결과 표시
- **데이터 뷰어**: API 호출 결과 데이터 시각화

#### 3.4.2 백엔드 처리
- **코드 생성 에이전트**: 명세서 기반 맞춤형 코드 생성
- **코드 실행 엔진**: Python/JavaScript 코드 실행
- **API 호출 관리**: 실제 API 호출 및 데이터 수집

## 4. UI/UX 설계

### 4.1 디자인 시스템
- **컬러 팔레트**: 모던한 다크/라이트 테마
- **타이포그래피**: Inter 폰트 패밀리
- **컴포넌트**: Shadcn/ui 기반 일관된 디자인
- **애니메이션**: Framer Motion을 통한 부드러운 전환

### 4.2 레이아웃
- **헤더**: 로고, 진행 단계 표시, 설정 메뉴
- **사이드바**: 단계별 네비게이션 및 상태 표시
- **메인 콘텐츠**: 각 단계별 전용 인터페이스
- **푸터**: 상태 정보 및 도움말 링크

### 4.3 반응형 디자인
- **데스크톱**: 풀 레이아웃 (1200px+)
- **태블릿**: 적응형 레이아웃 (768px-1199px)
- **모바일**: 스택 레이아웃 (767px 이하)

## 5. API 설계

### 5.1 RESTful API 엔드포인트
```
POST /api/v1/crawl/start          # 크롤링 시작
GET  /api/v1/crawl/status/{id}    # 크롤링 상태 조회
POST /api/v1/search/query         # RAG 검색
POST /api/v1/api/test             # API 테스트 실행
POST /api/v1/spec/generate        # 명세서 생성
PUT  /api/v1/spec/update          # 명세서 수정
POST /api/v1/code/generate        # 코드 생성
POST /api/v1/code/execute         # 코드 실행
```

### 5.2 WebSocket 연결
```
/ws/crawl/{session_id}            # 크롤링 진행 상황
/ws/chat/{session_id}             # 채팅 인터페이스
/ws/code/{session_id}             # 코드 실행 결과
```

## 6. 데이터 모델

### 6.1 세션 관리
```typescript
interface Session {
  id: string;
  currentStep: 1 | 2 | 3 | 4;
  createdAt: Date;
  updatedAt: Date;
  data: {
    step1?: CrawlData;
    step2?: ApiSearchData;
    step3?: SpecificationData;
    step4?: CodeGenerationData;
  };
}
```

### 6.2 각 단계별 데이터 구조
```typescript
interface CrawlData {
  urls: string[];
  files: FileUpload[];
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
}

interface ApiSearchData {
  queries: ChatMessage[];
  selectedApi: ApiInfo;
  testResults: TestResult[];
}

interface SpecificationData {
  content: string;
  template: string;
  approved: boolean;
}

interface CodeGenerationData {
  conversations: ChatMessage[];
  generatedCode: CodeBlock[];
  executionResults: ExecutionResult[];
}
```

## 7. 구현 계획

### 7.1 Phase 1: 기본 인프라 구축 (2주)
- React 프론트엔드 기본 구조 설정
- FastAPI 백엔드 기본 구조 설정
- Strands Agents 통합
- Step 1 구현 (데이터 입력)

### 7.2 Phase 2: 핵심 기능 개발 (3주)
- Step 2 구현 (API 탐색 및 테스트)
- Knowledge Base 연동
- RAG 검색 기능
- 실시간 통신 (WebSocket)

### 7.3 Phase 3: 명세서 및 코드 생성 (2주)
- Step 3 구현 (명세서 작성)
- Step 4 구현 (코드 생성)
- 코드 실행 엔진

### 7.4 Phase 4: UI/UX 완성 및 테스트 (1주)
- 디자인 시스템 적용
- 반응형 레이아웃
- 통합 테스트

## 8. 성공 기준

### 8.1 기능적 성공 기준
- [ ] 4단계 워크플로우 완전 구현
- [ ] 웹 크롤링 및 문서 업로드 기능
- [ ] RAG 기반 API 검색 및 테스트
- [ ] 명세서 자동 생성 및 편집
- [ ] 대화형 코드 생성 및 실행

### 8.2 사용성 기준
- [ ] 직관적인 UI/UX
- [ ] 단계별 진행 상황 명확 표시
- [ ] 실시간 피드백 제공
- [ ] 모바일 반응형 지원

### 8.3 성능 기준
- [ ] 페이지 로딩 시간 3초 이내
- [ ] API 응답 시간 5초 이내
- [ ] 실시간 업데이트 지연 1초 이내

## 9. 기술 스택 상세

### 9.1 프론트엔드
```json
{
  "react": "^18.0.0",
  "typescript": "^5.0.0",
  "tailwindcss": "^3.0.0",
  "@radix-ui/react-*": "latest",
  "framer-motion": "^10.0.0",
  "react-query": "^4.0.0",
  "zustand": "^4.0.0"
}
```

### 9.2 백엔드
```txt
fastapi>=0.104.0
strands-agents>=0.1.0
strands-agents-tools>=0.1.0
websockets>=11.0.0
boto3>=1.34.0
```

**총 예상 기간**: 8주
