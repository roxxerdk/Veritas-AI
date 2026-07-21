# Unified Implementation Plan: React Frontend (Vite + React 18/19 + TS + Tailwind + shadcn/ui)

Build a production-quality, responsive single-page application (SPA) with a three-panel RAG workspace layout, powered by TanStack Query and shadcn/ui.

---

## 1. Directory Structure

```text
frontend/
├── src/
│   ├── app/
│   │   ├── App.tsx
│   │   ├── router.tsx
│   │   └── providers.tsx
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   └── Sidebar.tsx
│   │   │
│   │   ├── chat/
│   │   │   ├── ChatConsole.tsx
│   │   │   ├── ChatThread.tsx
│   │   │   ├── EvidencePanel.tsx
│   │   │   └── TraceChecklist.tsx
│   │   │
│   │   ├── documents/
│   │   │   ├── UploadPanel.tsx
│   │   │   └── ProcessingTable.tsx
│   │   │
│   │   └── ui/              # shadcn UI components
│   │
│   ├── hooks/
│   │   └── useAuth.ts
│   │
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   └── Settings.tsx
│   │
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   ├── documents.ts
│   │   └── chat.ts
│   │
│   └── styles/
│       └── index.css
```

---

## 2. Ingestion Status API Endpoint Addition [NEW]

To support polling ingestion progress, we will add a backend router endpoint in `backend/app/api/documents.py`:

```python
@router.get("/{document_id}/status")
def get_document_status(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verifies document belongs to current user
    # Returns latest ProcessingJob status & error messages
```

---

## 3. UI/UX Three-Panel Layout Design

```text
+-------------------------------------------------------------------------------+
| Sidebar |                 Chat Thread                 |    Evidence Panel    |
| (Nav)   |                                             |  - Citations List    |
|         | User: "What is Veritas AI?"                 |  - Grounding Snippet |
|         |                                             |                      |
|         | Assistant: "Veritas AI is self-correcting   |  - Execution Trace   |
|         |             RAG platform [1]..."            |    QU ✓  Ret ✓  Ref ✓|
+---------+---------------------------------------------+----------------------+
```

* **Left Sidebar**: Controls routing between Ingestion Dashboard, Chat Console, and Settings.
* **Center Chat Pane**: Houses message bubbles with parsed markdown support. Clicking inline citation `[1]` activates the right sidebar and scrolls it to citation 1.
* **Right Evidence Workspace**: Interactive tabs:
  * **Grounding Context**: Displays similarity scores, file source, page numbers, and exact chunk snippets.
  * **System Trace**: Shows the checklist of completed agent operations (Intent, Retrieval, Grading, Reflection, Verification) with execution time stats.

---

## 4. Project Scaffolding Commands

We will execute the following commands in the `frontend` folder:

1. Scaffold Vite app:
   ```bash
   npx create-vite@latest ./ --template react-ts --yes
   ```
2. Install libraries:
   ```bash
   npm install axios react-router-dom @tanstack/react-query lucide-react clsx tailwind-merge react-hook-form zod @hookform/resolvers
   npm install -D tailwindcss postcss autoprefixer
   ```
3. Initialize Tailwind CSS configurations.

---

## 5. Verification Plan

* **Document upload**: Drag & drop -> upload starts -> Status updates dynamically in real-time -> completed state.
* **Chat Grounding**: Input question -> messages populate -> Right-panel citations highlight on click -> trace list animates completion checkmarks.
