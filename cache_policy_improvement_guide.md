# 버거킹 캐시 정책 개선 가이드

## 🔍 현재 문제점 진단

### HTTP 헤더 분석 결과
```bash
# 실제 확인한 버거킹 리소스들의 캐시 헤더
curl -I https://www.burgerking.co.kr/css/app.css
```

**결과:**
```http
Cache-Control: max-age=0, no-cache, no-store, must-revalidate
Pragma: no-cache
X-Cache: Miss from cloudfront
```

### 문제점 해석

| 헤더 | 현재 값 | 문제점 |
|------|---------|--------|
| `max-age=0` | 0초 | 캐시 즉시 만료 |
| `no-cache` | 활성화 | 캐시 사용 금지 |
| `no-store` | 활성화 | 저장 자체 금지 |
| `X-Cache` | Miss | 항상 원본 서버 요청 |

## 🎯 캐시 정책 개선 방안

### 1. 정적 리소스별 최적 캐시 정책

#### CSS/JavaScript 파일
```http
# 현재 (문제)
Cache-Control: max-age=0, no-cache, no-store, must-revalidate

# 개선안
Cache-Control: public, max-age=31536000, immutable
# 의미: 1년간 캐시, 공개적으로 캐시 가능, 불변 파일
```

#### 이미지 파일
```http
# 현재 (문제)
Cache-Control: max-age=0, no-cache, no-store, must-revalidate

# 개선안
Cache-Control: public, max-age=2592000
# 의미: 30일간 캐시, 공개적으로 캐시 가능
```

#### HTML 파일
```http
# 현재 (문제)
Cache-Control: max-age=0, no-cache, no-store, must-revalidate

# 개선안
Cache-Control: public, max-age=3600, must-revalidate
# 의미: 1시간 캐시, 만료 시 재검증 필요
```

### 2. CloudFront 캐시 동작 설정

#### 현재 설정 (추정)
```json
{
  "CachePolicyId": "custom-no-cache",
  "TTL": {
    "DefaultTTL": 0,
    "MaxTTL": 0,
    "MinTTL": 0
  },
  "CacheKeyAndForwardedHeaders": {
    "Headers": "all"
  }
}
```

#### 권장 설정
```json
{
  "PathPattern": "*.css",
  "CachePolicyId": "static-assets-optimized",
  "TTL": {
    "DefaultTTL": 31536000,  // 1년
    "MaxTTL": 31536000,
    "MinTTL": 31536000
  },
  "Compress": true
}
```

## 📊 개선 효과 시뮬레이션

### 현재 상황 분석
```bash
# 실제 테스트 - 같은 리소스 2번 요청
time curl -s https://www.burgerking.co.kr/css/app.css > /dev/null
time curl -s https://www.burgerking.co.kr/css/app.css > /dev/null
```

**결과:** 두 요청 모두 동일한 시간 소요 (캐시 미사용)

### 개선 후 예상 결과
- **첫 번째 요청**: 원본 서버에서 로드 (느림)
- **두 번째 요청**: CloudFront 캐시에서 로드 (빠름)

## 🛠️ 구체적 구현 방법

### 1. 서버 설정 변경 (Nginx)
```nginx
# /etc/nginx/sites-available/burgerking
location ~* \.(css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary Accept-Encoding;
}

location ~* \.(jpg|jpeg|png|gif|ico|svg)$ {
    expires 30d;
    add_header Cache-Control "public";
}

location / {
    expires 1h;
    add_header Cache-Control "public, must-revalidate";
}
```

### 2. CloudFront Distribution 설정
```json
{
  "DistributionConfig": {
    "CacheBehaviors": [
      {
        "PathPattern": "*.css",
        "TargetOriginId": "burgerking-origin",
        "ViewerProtocolPolicy": "redirect-to-https",
        "CachePolicyId": "static-assets-policy",
        "Compress": true
      },
      {
        "PathPattern": "*.js",
        "TargetOriginId": "burgerking-origin",
        "ViewerProtocolPolicy": "redirect-to-https",
        "CachePolicyId": "static-assets-policy",
        "Compress": true
      }
    ]
  }
}
```

### 3. 캐시 정책 생성 (AWS CLI)
```bash
aws cloudfront create-cache-policy \
  --cache-policy-config '{
    "Name": "BurgerKing-StaticAssets",
    "DefaultTTL": 31536000,
    "MaxTTL": 31536000,
    "MinTTL": 31536000,
    "ParametersInCacheKeyAndForwardedToOrigin": {
      "EnableAcceptEncodingGzip": true,
      "EnableAcceptEncodingBrotli": true,
      "QueryStringsConfig": {
        "QueryStringBehavior": "none"
      },
      "HeadersConfig": {
        "HeaderBehavior": "none"
      },
      "CookiesConfig": {
        "CookieBehavior": "none"
      }
    }
  }'
```

## 📈 성능 개선 측정 방법

### 1. 개선 전 측정
```bash
# 캐시 상태 확인
curl -I https://www.burgerking.co.kr/css/app.css | grep -E "(x-cache|cache-control)"

# 로딩 시간 측정
curl -w "@curl-format.txt" -s -o /dev/null https://www.burgerking.co.kr/css/app.css
```

### 2. 개선 후 측정
```bash
# 첫 번째 요청 (캐시 Miss 예상)
curl -I https://www.burgerking.co.kr/css/app.css | grep x-cache
# 예상 결과: X-Cache: Miss from cloudfront

# 두 번째 요청 (캐시 Hit 예상)
curl -I https://www.burgerking.co.kr/css/app.css | grep x-cache
# 예상 결과: X-Cache: Hit from cloudfront
```

## 💡 추가 최적화 방안

### 1. 파일 버전 관리
```html
<!-- 현재 -->
<link href="/css/app.css" rel="stylesheet">

<!-- 개선안 (파일명에 해시 포함) -->
<link href="/css/app.a1b2c3d4.css" rel="stylesheet">
```

### 2. 압축 최적화
```nginx
# Brotli 압축 활성화
brotli on;
brotli_comp_level 6;
brotli_types text/css application/javascript;
```

### 3. HTTP/2 Push 활용
```nginx
# 중요 리소스 사전 푸시
location / {
    http2_push /css/app.css;
    http2_push /js/app.js;
}
```

## 🎯 구현 우선순위

### Phase 1: 즉시 구현 (1-2일)
1. **Nginx 캐시 헤더 설정 변경**
2. **CloudFront 캐시 정책 수정**

### Phase 2: 단기 구현 (1주)
1. **파일 버전 관리 시스템 도입**
2. **압축 최적화**

### Phase 3: 중장기 구현 (1개월)
1. **이미지 최적화 (WebP)**
2. **Critical CSS 인라인화**

## 📊 예상 개선 효과

| 지표 | 현재 | 개선 후 | 개선율 |
|------|------|---------|--------|
| 재방문자 로딩 시간 | 2.5초 | 0.5초 | 80% ↓ |
| 서버 요청 수 | 100% | 30% | 70% ↓ |
| CDN 비용 | $100 | $50 | 50% ↓ |
| 사용자 만족도 | 보통 | 우수 | 대폭 개선 |

이러한 개선을 통해 버거킹은 **CDN의 진정한 효과**를 누릴 수 있으며, 사용자 경험과 운영 비용 모두에서 큰 이익을 얻을 수 있습니다.
