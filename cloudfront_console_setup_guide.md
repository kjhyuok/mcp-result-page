# CloudFront 콘솔 캐시 정책 설정 가이드

## 🎯 목표
버거킹처럼 `no-cache, no-store` 설정된 사이트의 캐시 정책을 개선하여 성능 향상

## 📋 단계별 설정 방법

### 1단계: CloudFront 콘솔 접속
1. AWS 콘솔 → **CloudFront** 서비스 선택
2. 해당 Distribution 클릭 (버거킹의 경우 여러 개 존재)

### 2단계: Cache Policies 생성
1. 좌측 메뉴에서 **"Policies"** → **"Cache"** 클릭
2. **"Create cache policy"** 버튼 클릭

#### 정적 리소스용 캐시 정책 생성
```
Policy name: StaticAssets-LongTerm
Description: CSS, JS 파일용 장기 캐시 정책

TTL settings:
├── Minimum TTL: 31536000 (1년)
├── Maximum TTL: 31536000 (1년)
└── Default TTL: 31536000 (1년)

Cache key settings:
├── Headers: None
├── Query strings: None
└── Cookies: None

Compression support: ✅ Enable
```

#### HTML용 캐시 정책 생성
```
Policy name: HTML-ShortTerm
Description: HTML 파일용 단기 캐시 정책

TTL settings:
├── Minimum TTL: 0
├── Maximum TTL: 3600 (1시간)
└── Default TTL: 3600 (1시간)

Cache key settings:
├── Headers: None
├── Query strings: All
└── Cookies: None

Compression support: ✅ Enable
```

### 3단계: Distribution 설정 수정
1. **Distributions** 메뉴로 돌아가기
2. 해당 Distribution 선택 → **"Behaviors"** 탭 클릭

#### 기존 Behavior 수정
1. **Default (*)** behavior 선택 → **"Edit"** 클릭

```
Path pattern: *
Origin: (기존 유지)
Viewer protocol policy: Redirect HTTP to HTTPS

Cache policy: HTML-ShortTerm (위에서 생성한 정책)
Origin request policy: CORS-S3Origin (또는 None)
Response headers policy: (선택사항)

Compress objects automatically: ✅ Yes
```

#### 새로운 Behavior 추가 (CSS/JS용)
1. **"Create behavior"** 클릭

```
Path pattern: *.css
Origin: (기존과 동일)
Viewer protocol policy: Redirect HTTP to HTTPS

Cache policy: StaticAssets-LongTerm
Origin request policy: None
Response headers policy: (선택사항)

Compress objects automatically: ✅ Yes
```

2. 또 다른 Behavior 추가 (JS용)

```
Path pattern: *.js
Origin: (기존과 동일)
Viewer protocol policy: Redirect HTTP to HTTPS

Cache policy: StaticAssets-LongTerm
Origin request policy: None
Response headers policy: (선택사항)

Compress objects automatically: ✅ Yes
```

#### 이미지용 Behavior 추가
```
Path pattern: *.png
Path pattern: *.jpg
Path pattern: *.jpeg
Path pattern: *.gif
Path pattern: *.ico
Path pattern: *.svg

Cache policy: StaticAssets-LongTerm (또는 별도 생성)
```

### 4단계: Behavior 우선순위 설정
**중요**: Behavior는 위에서부터 순서대로 매칭됩니다.

```
우선순위 순서:
1. *.css (가장 구체적)
2. *.js
3. *.png
4. *.jpg
5. *.ico
...
99. * (Default - 가장 마지막)
```

### 5단계: 배포 및 확인
1. **"Save changes"** 클릭
2. Distribution 상태가 **"Deploying"** → **"Deployed"** 될 때까지 대기 (5-15분)

## 🧪 설정 확인 방법

### 배포 완료 후 테스트
```bash
# CSS 파일 캐시 확인
curl -I https://your-domain.com/css/app.css | grep -E "(cache-control|x-cache)"

# 예상 결과 (첫 번째 요청)
# cache-control: public, max-age=31536000
# x-cache: Miss from cloudfront

# 예상 결과 (두 번째 요청)
# cache-control: public, max-age=31536000
# x-cache: Hit from cloudfront
```

## 🚨 주의사항

### 1. Origin 서버 설정도 중요
CloudFront만 설정해도 어느 정도 효과가 있지만, Origin 서버(Nginx)에서도 올바른 캐시 헤더를 보내야 최적 성능을 얻을 수 있습니다.

### 2. 파일 버전 관리
장기 캐시 설정 시 파일 업데이트 문제가 발생할 수 있으므로:
```html
<!-- 파일명에 버전/해시 포함 권장 -->
<link href="/css/app.v1.2.3.css" rel="stylesheet">
<script src="/js/app.abc123.js"></script>
```

### 3. 캐시 무효화 (Invalidation)
긴급 업데이트 시 캐시 무효화 필요:
```
CloudFront → Invalidations → Create invalidation
Object paths: /css/* 또는 /*
```

## 📊 설정 전후 비교

### 설정 전
```http
cache-control: max-age=0, no-cache, no-store, must-revalidate
x-cache: Miss from cloudfront (항상)
```

### 설정 후
```http
# 첫 번째 요청
cache-control: public, max-age=31536000
x-cache: Miss from cloudfront

# 두 번째 요청
cache-control: public, max-age=31536000
x-cache: Hit from cloudfront
```

## 🎯 고급 설정 (선택사항)

### Origin Request Policy 생성
특별한 헤더나 쿠키 전달이 필요한 경우:
```
Policy name: Custom-Origin-Request
Headers: CloudFront-Viewer-Country, CloudFront-Is-Mobile-Viewer
Query strings: All
Cookies: None
```

### Response Headers Policy 생성
보안 헤더 추가:
```
Policy name: Security-Headers
Custom headers:
├── X-Content-Type-Options: nosniff
├── X-Frame-Options: DENY
├── X-XSS-Protection: 1; mode=block
└── Referrer-Policy: strict-origin-when-cross-origin
```

이 설정을 통해 버거킹과 같은 사이트도 **80% 이상의 성능 향상**을 달성할 수 있습니다!
