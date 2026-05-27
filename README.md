# 🛡️ KISA Security Notice MCP Scraper

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![MCP](https://img.shields.io/badge/Protocol-MCP-orange.svg)
![Status](https://img.shields.io/badge/Status-Automated-success)

KISA(한국인터넷진흥원) 보호나라의 보안 공지를 실시간으로 수집하여, AI 에이전트가 즉시 활용할 수 있는 MCP(Model Context Protocol) 서버 형태로 제공하고 알림을 자동화하는 프로젝트입니다.

## 📌 Project Overview

### 🚀 Background (As-Is)
기존에는 KISA 보안 공지를 확인하기 위해 매번 웹사이트를 직접 방문해야 했으며, 실시간 대응이 어려워 보안 취약점 확인에 공백이 발생할 수 있는 문제점이 있었습니다.

### ✨ Goal (To-Be)
KISA 보안 공지를 자동으로 스크래핑하고, MCP를 통해 AI 에이전트와 연동함으로써 매일 정해진 시간에 공지 내용을 확인하고 카카오톡으로 즉시 알림을 받는 자동화 환경을 구축합니다.

---

## 🛠 Tech Stack

- **Language:** Python 3.10+
- **Framework:** [FastMCP](https://github.com/modelcontextprotocol) (MCP Server Implementation)
- **Scraping:** `httpx`, `BeautifulSoup4`
- **Automation:** TaskFlow (Scheduled Job Management)
- **Integration:** KakaoTalk (via `mcp-gateway`)
- **Environment:** OpenClaw AI Agent (gemma4-26b)

---

## ⚙️ Key Features

1. **Real-time KISA Scraping**: `kisa_scraper.py`를 통해 KISA 보호나라 웹사이트의 최신 보안 공지를 데이터화합니다.
2. **MCP Server Implementation**: FastMCP를 활용하여 스크래핑된 데이터를 AI가 도구(Tool)로서 호출할 수 있도록 표준화된 API로 제공합니다.
3. **Automated Notification**: `mcp-gateway`를 연동하여 수집된 공지 내용을 카카오톡 메시지로 자동 전송합니다.
4. **Intelligent Scheduling**: `TaskFlow`를 사용하여 매일 오전 8시(KST)에 정기적으로 보안 공지를 모니터링하는 워크플로우를 관리합니다.

---

## 📦 Installation & Quick Start

### 1. 환경 설정 및 의존성 설치
본 프로젝트는 Python 3.10 이상을 권장합니다.
```bash
pip install httpx beautifulsoup4 mcp
