# upnote-lens-mcp

UpNote 노트를 "들여다보는 렌즈" 역할을 하는 하이브리드 MCP 서버.

- **읽기** — 로컬 UpNote SQLite DB를 **읽기 전용**으로 직접 조회해서 노트 본문/검색 결과를 실제 텍스트로 돌려준다.
- **쓰기** — 노트 생성/열기는 `upnote://` URL 스킴(x-callback-url)으로 처리한다. DB에는 절대 쓰지 않는다.

> 쓰기(URL scheme) 부분은 [chadthornton/upnote-mcp](https://github.com/chadthornton/upnote-mcp) (MIT) 기반.

## 왜 둘을 합쳤나

기존 upnote-mcp는 URL 스킴만 써서 노트 생성/검색은 되지만 "노트 내용을 읽어 돌려주는 것"이 설계상 불가능하다(검색해도 앱에 결과만 띄울 뿐 텍스트가 안 돌아옴). UpNote는 로컬 SQLite에 본문을 평문 저장하므로, 읽기는 DB 직접 조회로 해결하고 쓰기는 안전하게 URL 스킴에 맡긴다.

## 요구사항

- macOS (쓰기 도구가 `open`으로 `upnote://` URL을 실행)
- Python 3.10+
- UpNote 데스크톱 앱 설치 (`com.getupnote.desktop`)

## 설치 & 등록

> **🤖 AI에게 맡기기**: MCP 클라이언트(Claude 등)에 [`llms-install.md`](llms-install.md)
> 링크를 주면 아래 절차를 알아서 실행해 설치까지 해 준다.

> 아래 예시는 PyPI 게시를 전제로 한다. **게시 전**에는 `upnote-lens-mcp` 자리에
> git 소스를 쓴다 — uvx는 `--from git+https://github.com/elsboo/upnote-lens-mcp`,
> pip은 `git+https://github.com/elsboo/upnote-lens-mcp`.

### 방법 1 — uvx (권장, 사전 설치 불필요)

[uv](https://docs.astral.sh/uv/)만 있으면 별도 설치 단계 없이 바로 실행된다.

Claude Desktop — `~/Library/Application Support/Claude/claude_desktop_config.json`
(복붙용 예시: [`examples/mcp-config.json`](examples/mcp-config.json)):

```json
{
  "mcpServers": {
    "upnote-lens": {
      "command": "uvx",
      "args": ["upnote-lens-mcp"]
    }
  }
}
```

Claude Code:

```bash
claude mcp add upnote-lens -- uvx upnote-lens-mcp
```

### 방법 2 — pip

```bash
pip install upnote-lens-mcp
```

설치하면 `upnote-lens-mcp`(별칭 `upnote-lens`) 명령이 생긴다.

```json
{
  "mcpServers": {
    "upnote-lens": {
      "command": "upnote-lens-mcp"
    }
  }
}
```

Claude Code: `claude mcp add upnote-lens -- upnote-lens-mcp`

> venv에 설치했다면 `command`에 venv의 절대경로(`/path/.venv/bin/upnote-lens-mcp`)를 쓴다.

### 파이썬/pip이 없다면

- 파이썬은 있는데 `pip`이 없으면: `python -m ensurepip --upgrade`
- 파이썬 자체가 없으면: uv를 설치하고 **방법 1**을 쓴다(파이썬도 uv가 알아서 챙긴다).
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## 제공 도구

### 읽기 (로컬 DB 조회 → 실제 텍스트 반환)

| 도구 | 설명 |
|---|---|
| `search_notes(query, limit=20)` | 제목/본문 부분일치 검색. id·제목·수정시각·스니펫 반환 |
| `get_note(note_id, include_html=False)` | 특정 노트의 제목 + 본문 전문 (옵션: 원본 HTML) |
| `list_recent(limit=20)` | 최근 수정된 노트 목록 |
| `list_notebooks()` | 노트북 목록 + 노트 개수 + 부모 |
| `list_notes_in_notebook(notebook_id, limit=50)` | 노트북 안의 노트 |
| `list_tags()` | 태그 목록 + 노트 개수 |
| `list_notes_by_tag(tag_title, limit=50)` | 태그가 달린 노트 |

### 쓰기 (`upnote://` URL 스킴)

| 도구 | 설명 |
|---|---|
| `create_note(title, content, notebook?, markdown=True, new_window=False)` | 노트 생성. `content`는 기본 Markdown. `notebook`은 이름으로 매칭. **태그는 설정 불가**(아래 참고) |
| `open_note(note_id, new_window=False)` | 기존 노트를 앱에서 열기 |
| `open_notebook(notebook_id)` | 노트북을 앱에서 열기 |

> **태그 제약**: UpNote의 `note/new` URL 스킴에는 태그 파라미터가 없고, 본문에 `#해시태그`를 넣어도 진짜 태그가 아니라 일반 텍스트로 들어간다(에디터에서 직접 입력할 때만 태그로 변환됨). 노트 생성 후 태그가 필요하면 앱에서 직접 달아야 한다.

## DB 경로 재정의

DB가 기본 위치가 아니면 환경변수로 지정한다.

```
UPNOTE_LENS_DB=/path/to/upnote.sqlite3
```

기본 경로:
`~/Library/Containers/com.getupnote.desktop/Data/Library/Application Support/UpNote/upnote.sqlite3`

## 안전 제약 (설계 원칙)

- **읽기는 절대 원본을 수정하지 않는다.** `mode=ro&immutable=1`로 읽기 전용 연결만 연다(락/WAL 충돌 없음).
- **DB에 INSERT/UPDATE/DELETE를 하지 않는다.** UpNote는 클라우드 sync를 하므로 DB 직접 쓰기는 sync 손상 위험이 있다. 노트 생성/수정은 전부 URL 스킴 경유.

## 구현 메모 (검증된 사실)

- 유효 노트 필터: `trashed=0 AND deleted=0 AND COALESCE(isTemplate,0)=0`
  (`isTemplate`은 0이 아니라 NULL이라 `isTemplate=0`으로 거르면 전부 탈락)
- 타임스탬프는 밀리초 epoch: `datetime(updatedAt/1000,'unixepoch','localtime')`
- 노트↔노트북 관계는 `notebooks.notes`(노트 id JSON 배열)가 source of truth.
  `notes.notebookLinks`는 비어 있다.

## 라이선스

MIT. 자세한 내용은 [LICENSE](LICENSE) 참고.
쓰기 부분의 URL 스킴 포맷·실행 방식은 chadthornton/upnote-mcp(MIT)에서 차용했다.
