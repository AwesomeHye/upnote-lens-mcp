# upnote-lens-mcp

UpNote 노트를 "들여다보는 렌즈" 역할을 하는 하이브리드 MCP 서버.

- **읽기** — 로컬 UpNote SQLite DB를 **읽기 전용**으로 직접 조회해서 노트 본문/검색 결과를 실제 텍스트로 돌려준다.
- **쓰기** — 노트 생성/열기는 `upnote://` URL 스킴(x-callback-url)으로 처리한다. DB에는 절대 쓰지 않는다.

> 쓰기(URL scheme) 부분은 [chadthornton/upnote-mcp](https://github.com/chadthornton/upnote-mcp) (MIT) 기반.

## 왜 둘을 합쳤나

기존 upnote-mcp는 URL 스킴만 써서 노트 생성/검색은 되지만 "노트 내용을 읽어 돌려주는 것"이 설계상 불가능하다(검색해도 앱에 결과만 띄울 뿐 텍스트가 안 돌아옴). UpNote는 로컬 SQLite에 본문을 평문 저장하므로, 읽기는 DB 직접 조회로 해결하고 쓰기는 안전하게 URL 스킴에 맡긴다.

## 상태

🚧 개발 중. 자세한 사용법/설치/등록 방법은 추후 문서화.

## 라이선스

MIT. 자세한 내용은 [LICENSE](LICENSE) 참고.
