"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";

const API_BASE = "http://localhost:8000";

interface HistoryItem {
  id: string;
  name: string;
  type: "pdf" | "youtube" | "text";
  content: string;
  timestamp: string;
  summary?: any;
  flashcards?: any;
  quiz?: any;
}

// SVG Icons as components (no emojis)
const IconDoc = () => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M4 1h6l4 4v10H4V1z" />
    <path d="M10 1v4h4" />
  </svg>
);
const IconYT = () => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
    <rect x="1" y="3" width="14" height="10" />
    <path d="M6 6l4 2-4 2V6z" fill="currentColor" />
  </svg>
);
const IconText = () => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M3 3h10M3 6h8M3 9h10M3 12h6" />
  </svg>
);
const IconTrash = () => (
  <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M2 4h12M5 4V2h6v2M6 7v5M10 7v5M4 4l1 10h6l1-10" />
  </svg>
);
const IconEdit = () => (
  <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M11 1l4 4-9 9H2v-4l9-9z" />
  </svg>
);
const IconPlus = () => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M8 3v10M3 8h10" />
  </svg>
);
const IconArrow = () => (
  <svg width="10" height="10" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M6 3l5 5-5 5" />
  </svg>
);

const typeIcons: Record<string, React.ReactNode> = {
  pdf: <IconDoc />,
  youtube: <IconYT />,
  text: <IconText />,
};

function getHistory(): HistoryItem[] {
  if (typeof window === "undefined") return [];
  const keys = Object.keys(localStorage).filter((k) => k.startsWith("eduspark_doc_"));
  return keys
    .map((k) => {
      try {
        return JSON.parse(localStorage.getItem(k) || "{}") as HistoryItem;
      } catch {
        return null;
      }
    })
    .filter(Boolean)
    .sort((a, b) => new Date(b!.timestamp).getTime() - new Date(a!.timestamp).getTime()) as HistoryItem[];
}

export default function Dashboard() {
  const router = useRouter();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [urlInput, setUrlInput] = useState("");
  const [rawTextInput, setRawTextInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [statusText, setStatusText] = useState("Ready");
  const [activeInputMode, setActiveInputMode] = useState<"url" | "file" | "text">("url");
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setHistory(getHistory());
  }, []);

  const setStatus = (msg: string) => setStatusText(msg);

  const handleUploadSuccess = (content: string, name: string, type: "pdf" | "youtube" | "text") => {
    const id = `doc-${Date.now()}`;
    const item: HistoryItem = { id, name, type, content, timestamp: new Date().toISOString() };
    localStorage.setItem(`eduspark_doc_${id}`, JSON.stringify(item));
    setHistory(getHistory());
    setStatus(`Stored: ${id}`);
    router.push(`/study/${id}`);
  };

  const handleProcessUrl = async () => {
    if (!urlInput.trim() || isProcessing) return;
    setIsProcessing(true);
    setStatus("Connecting to backend...");
    try {
      const formData = new FormData();
      formData.append("youtube_url", urlInput);
      setStatus("Extracting transcript...");
      const response = await fetch(`${API_BASE}/upload`, { method: "POST", body: formData });
      if (!response.ok) { const err = await response.json(); throw new Error(err.detail || `HTTP ${response.status}`); }
      const data = await response.json();
      setStatus("Transcript extracted.");
      handleUploadSuccess(data.content, urlInput, "youtube");
    } catch (error: any) {
      setStatus(`Error: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = async () => {
    const file = fileInputRef.current?.files?.[0];
    if (!file || isProcessing) return;
    setIsProcessing(true);
    setStatus(`Uploading ${file.name}...`);
    try {
      const formData = new FormData();
      formData.append("file", file);
      setStatus("Parsing PDF...");
      const response = await fetch(`${API_BASE}/upload`, { method: "POST", body: formData });
      if (!response.ok) { const err = await response.json(); throw new Error(err.detail || `HTTP ${response.status}`); }
      const data = await response.json();
      setStatus("PDF parsed.");
      handleUploadSuccess(data.content, file.name, "pdf");
    } catch (error: any) {
      setStatus(`Error: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRawText = async () => {
    if (!rawTextInput.trim() || isProcessing) return;
    setIsProcessing(true);
    setStatus("Ingesting text...");
    try {
      const formData = new FormData();
      formData.append("raw_text", rawTextInput);
      const response = await fetch(`${API_BASE}/upload`, { method: "POST", body: formData });
      if (!response.ok) { const err = await response.json(); throw new Error(err.detail || `HTTP ${response.status}`); }
      const data = await response.json();
      const name = rawTextInput.slice(0, 40).replace(/\s+/g, " ").trim();
      handleUploadSuccess(data.content, name, "text");
    } catch (error: any) {
      setStatus(`Error: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDelete = (id: string) => {
    localStorage.removeItem(`eduspark_doc_${id}`);
    setHistory(getHistory());
    setStatus("Document deleted.");
  };

  const handleRename = (id: string) => {
    const stored = localStorage.getItem(`eduspark_doc_${id}`);
    if (!stored) return;
    const item = JSON.parse(stored);
    item.name = renameValue;
    localStorage.setItem(`eduspark_doc_${id}`, JSON.stringify(item));
    setRenamingId(null);
    setRenameValue("");
    setHistory(getHistory());
    setStatus("Renamed.");
  };

  const formatDate = (ts: string) => {
    const d = new Date(ts);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return "Just now";
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffH = Math.floor(diffMin / 60);
    if (diffH < 24) return `${diffH}h ago`;
    return d.toLocaleDateString();
  };

  return (
    <div className="flex flex-1 h-[calc(100vh-52px)]">
      {/* Sidebar: History */}
      <aside className="w-[300px] border-r-2 border-[var(--border-color)] flex flex-col bg-[var(--bg-secondary)]">
        <div className="panel-header">
          <span>History</span>
          <span className="text-[var(--fg-muted)]">{history.length}</span>
        </div>
        <div className="flex-1 overflow-y-auto">
          {history.length === 0 && (
            <div className="p-6 text-center text-[var(--fg-muted)] text-[11px]">
              No documents yet. Upload content to get started.
            </div>
          )}
          {history.map((item) => (
            <div
              key={item.id}
              className="border-b border-[var(--border-light)] hover:bg-[var(--bg-tertiary)] transition-colors group"
            >
              {renamingId === item.id ? (
                <div className="p-3 flex gap-2">
                  <input
                    className="input-field text-[11px] py-1 px-2"
                    value={renameValue}
                    onChange={(e) => setRenameValue(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleRename(item.id)}
                    autoFocus
                  />
                  <button className="btn-ghost text-[10px]" onClick={() => handleRename(item.id)}>OK</button>
                  <button className="btn-ghost text-[10px]" onClick={() => setRenamingId(null)}>X</button>
                </div>
              ) : (
                <div className="p-3 cursor-pointer" onClick={() => router.push(`/study/${item.id}`)}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[var(--fg-muted)]">{typeIcons[item.type]}</span>
                    <span className="font-semibold text-[12px] truncate flex-1">{item.name}</span>
                    <span className="text-[10px] text-[var(--fg-muted)]">{formatDate(item.timestamp)}</span>
                  </div>
                  <div className="flex items-center gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      className="btn-ghost text-[10px] flex items-center gap-1"
                      onClick={(e) => { e.stopPropagation(); setRenamingId(item.id); setRenameValue(item.name); }}
                    >
                      <IconEdit /> Rename
                    </button>
                    <button
                      className="btn-ghost text-[10px] flex items-center gap-1 text-[var(--danger)]"
                      onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }}
                    >
                      <IconTrash /> Delete
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </aside>

      {/* Main content: Input area */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="w-full max-w-[640px] space-y-6">
            {/* Title */}
            <div className="text-center space-y-2">
              <h1 className="text-2xl font-bold tracking-tight">New Study Session</h1>
              <p className="text-[var(--fg-muted)] text-[12px]">
                Upload a PDF, paste a YouTube URL, or enter raw text to generate study materials.
              </p>
            </div>

            {/* Input mode tabs */}
            <div className="flex border-2 border-[var(--border-color)]">
              {(["url", "file", "text"] as const).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setActiveInputMode(mode)}
                  className={`flex-1 py-2.5 font-bold text-[11px] uppercase tracking-wider transition-colors ${
                    activeInputMode === mode
                      ? "bg-[var(--fg-primary)] text-[var(--bg-primary)]"
                      : "hover:bg-[var(--bg-tertiary)]"
                  }`}
                >
                  {mode === "url" ? "YouTube URL" : mode === "file" ? "PDF Upload" : "Raw Text"}
                </button>
              ))}
            </div>

            {/* URL input */}
            {activeInputMode === "url" && (
              <div className="space-y-3 fade-in">
                <input
                  type="text"
                  className="input-field"
                  placeholder="https://www.youtube.com/watch?v=..."
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleProcessUrl()}
                  disabled={isProcessing}
                />
                <button
                  onClick={handleProcessUrl}
                  disabled={isProcessing || !urlInput.trim()}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {isProcessing ? "Extracting Transcript..." : "Process URL"}
                  {!isProcessing && <IconArrow />}
                </button>
              </div>
            )}

            {/* File input */}
            {activeInputMode === "file" && (
              <div className="space-y-3 fade-in">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  className="input-field file:mr-4 file:border-0 file:bg-transparent file:font-bold file:uppercase file:text-[11px] file:cursor-pointer"
                  disabled={isProcessing}
                />
                <button
                  onClick={handleFileUpload}
                  disabled={isProcessing}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {isProcessing ? "Parsing PDF..." : "Upload & Process"}
                  {!isProcessing && <IconArrow />}
                </button>
              </div>
            )}

            {/* Raw text input */}
            {activeInputMode === "text" && (
              <div className="space-y-3 fade-in">
                <textarea
                  className="input-field resize-none h-32"
                  placeholder="Paste your study material here..."
                  value={rawTextInput}
                  onChange={(e) => setRawTextInput(e.target.value)}
                  disabled={isProcessing}
                />
                <button
                  onClick={handleRawText}
                  disabled={isProcessing || !rawTextInput.trim()}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {isProcessing ? "Processing..." : "Ingest & Analyze"}
                  {!isProcessing && <IconArrow />}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Status bar */}
        <div className="status-bar">
          <span>{statusText}</span>
          <span>{new Date().toLocaleDateString()}</span>
        </div>
      </div>
    </div>
  );
}
