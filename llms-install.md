# upnote-lens-mcp — AI 에이전트 설치 가이드

이 문서를 읽는 AI 에이전트(Claude 등)에게: 아래 절차대로 **upnote-lens-mcp**를
사용자의 MCP 클라이언트에 설치·등록하라. 각 단계에서 실패하면 멈추고 사용자에게
무엇이 막혔는지 알리고 지시를 기다려라. 외부 명령 실행이나 설정 파일 수정 전에는
사용자 동의를 받아라.

저장소: `https://github.com/elsboo/upnote-lens-mcp`

---

## 0. 전제 확인 (실패 시 중단)

1. **OS가 macOS인가?** (`uname` → `Darwin`)
   - 아니면 중단: 쓰기 도구가 macOS `open`으로 `upnote://`를 실행하므로 macOS 전용이다.
2. **UpNote 데스크톱 앱이 설치돼 있는가?**
   - 확인: `ls -d "$HOME/Library/Containers/com.getupnote.desktop"`
   - DB 파일: `~/Library/Containers/com.getupnote.desktop/Data/Library/Application Support/UpNote/upnote.sqlite3`
   - 없으면 중단하고 UpNote 설치를 안내하라.

## 1. 실행기(uv) 확보 — 권장 경로

1. `uv --version` 으로 uv 존재 확인.
2. 없으면 사용자 동의를 받고 설치:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   (uv는 파이썬도 알아서 챙기므로 별도 파이썬 설치가 필요 없다.)

> pip을 이미 쓰는 사용자면 uv 대신 `pip install upnote-lens-mcp`(게시 후) 또는
> `pip install git+https://github.com/elsboo/upnote-lens-mcp`(게시 전)도 가능하다.
> 이 경우 등록 시 `command`를 `"upnote-lens-mcp"`로 쓴다.

## 2. MCP 클라이언트 판별

- `claude` CLI가 있으면 → **Claude Code** 경로(3-A).
- 아니면 Claude Desktop 설정 파일 존재를 확인 → **Claude Desktop** 경로(3-B).
  - `~/Library/Application Support/Claude/claude_desktop_config.json`
- 둘 다 아니거나 다른 클라이언트면 사용자에게 어떤 클라이언트인지 물어라.

## 3. 등록

아래는 **PyPI 게시 후** 기준이다. 게시 전이면 `upnote-lens-mcp` 인자를
`--from git+https://github.com/elsboo/upnote-lens-mcp upnote-lens-mcp` 로 바꿔라.

### 3-A. Claude Code

게시 후:
```bash
claude mcp add upnote-lens -- uvx upnote-lens-mcp
```

게시 전(git 소스):
```bash
claude mcp add upnote-lens -- uvx --from git+https://github.com/elsboo/upnote-lens-mcp upnote-lens-mcp
```

### 3-B. Claude Desktop

`claude_desktop_config.json`을 읽어 `mcpServers`에 **병합**하라(기존 항목 보존, 덮어쓰지 말 것).
파일이 없으면 새로 만든다.

게시 후:
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

게시 전(git 소스):
```json
{
  "mcpServers": {
    "upnote-lens": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/elsboo/upnote-lens-mcp", "upnote-lens-mcp"]
    }
  }
}
```

수정 후 Claude Desktop을 재시작하라고 사용자에게 안내하라.

## 4. (선택) DB 경로 재정의

DB가 기본 위치가 아니면 서버 정의의 `env`에 추가:
```json
"env": { "UPNOTE_LENS_DB": "/path/to/upnote.sqlite3" }
```
Claude Code면: `claude mcp add ... -e UPNOTE_LENS_DB=/path/to/upnote.sqlite3`

## 5. 검증

- Claude Code: `claude mcp list` 에 `upnote-lens`가 보이는지 확인.
- 도구가 연결되면 `list_recent(limit=3)` 또는 `search_notes("test", 3)`를 호출해
  실제 노트 텍스트가 돌아오는지 확인하라.
- 도구가 안 보이면: 클라이언트 재시작 여부, `command`/`args` 오타, uv 설치 여부,
  (게시 전이라면) git 소스 형식을 점검하라.

설치가 끝나면 사용자에게 사용 가능한 도구(읽기 7 + 쓰기 3)와 "쓰기는 앱을 띄워
노트를 생성/연다"는 점을 간단히 알려라.
