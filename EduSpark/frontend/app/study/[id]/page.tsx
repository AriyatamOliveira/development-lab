"use client";

import { FlashcardView } from "@/components/FlashcardView";
import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter, useParams } from "next/navigation";

const API_BASE = "http://localhost:8000";

interface SummarySection {
  heading: string;
  summary: string;
}

interface SummaryData {
  title: string;
  sections: SummarySection[];
}

interface QuizQuestion {
  question: string;
  options: string[];
  answer: string;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

// SVG Icons
const IconBack = () => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M10 3L5 8l5 5" />
  </svg>
);
const IconSend = () => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M1 8h14M9 2l6 6-6 6" />
  </svg>
);
const IconExpand = () => (
  <svg width="10" height="10" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M4 6l4 4 4-4" />
  </svg>
);
const IconCollapse = () => (
  <svg width="10" height="10" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M4 10l4-4 4 4" />
  </svg>
);
const IconChat = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M2 2h12v9H5l-3 3V2z" />
  </svg>
);

export default function StudyTerminal() {
  const router = useRouter();
  const params = useParams();
  const docId = params.id as string;

  const [activeTab, setActiveTab] = useState<"summary" | "flashcards" | "quiz">("summary");

  const [summaryData, setSummaryData] = useState<SummaryData | null>(null);
  const [expandedSection, setExpandedSection] = useState<number | null>(null);
  const [flashcards, setFlashcards] = useState<{ question: string; answer: string }[]>([]);
  const [quiz, setQuiz] = useState<QuizQuestion[]>([]);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [showResults, setShowResults] = useState(false);

  const [loadingSummary, setLoadingSummary] = useState(false);
  const [loadingFlashcards, setLoadingFlashcards] = useState(false);
  const [loadingQuiz, setLoadingQuiz] = useState(false);

  const [docContent, setDocContent] = useState<string | null>(null);
  const [docName, setDocName] = useState<string>("Untitled");
  const [statusText, setStatusText] = useState("Loading document...");

  // Chat state
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Load document
  const loadedRef = useRef(false);
  useEffect(() => {
    if (loadedRef.current) return;
    loadedRef.current = true;

    const stored = localStorage.getItem(`eduspark_doc_${docId}`);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setDocContent(parsed.content);
        setDocName(parsed.name);
        setSummaryData(parsed.summary || null);
        setFlashcards(parsed.flashcards || []);
        setQuiz(parsed.quiz || []);
        setStatusText(`Loaded: ${parsed.name} (${parsed.content.length} chars)`);
      } catch {
        setStatusText("Error: Failed to parse document.");
      }
    } else {
      setStatusText("Error: Document not found.");
    }
  }, [docId]);

  // Save generated data back to localStorage
  const persistData = useCallback(
    (updates: Partial<{ summary: any; flashcards: any; quiz: any }>) => {
      const stored = localStorage.getItem(`eduspark_doc_${docId}`);
      if (!stored) return;
      const item = JSON.parse(stored);
      Object.assign(item, updates);
      localStorage.setItem(`eduspark_doc_${docId}`, JSON.stringify(item));
    },
    [docId]
  );

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const generateMaterial = async (type: "summary" | "flashcards" | "quiz") => {
    if (!docContent) return;

    const setLoading =
      type === "summary" ? setLoadingSummary : type === "flashcards" ? setLoadingFlashcards : setLoadingQuiz;

    setLoading(true);
    setStatusText(`Generating ${type}...`);

    try {
      const response = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text_content: docContent, material_type: type }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();

      if (type === "summary") {
        setSummaryData(data.data);
        persistData({ summary: data.data });
        setStatusText(`Summary generated: ${data.data?.sections?.length || 0} sections`);
      } else if (type === "flashcards") {
        const cards = Array.isArray(data.data) ? data.data : [];
        setFlashcards(cards);
        persistData({ flashcards: cards });
        setStatusText(`Flashcards generated: ${cards.length} cards`);
      } else if (type === "quiz") {
        const questions = Array.isArray(data.data) ? data.data : [];
        setQuiz(questions);
        setSelectedAnswers({});
        setShowResults(false);
        persistData({ quiz: questions });
        setStatusText(`Quiz generated: ${questions.length} questions`);
      }
    } catch (error: any) {
      setStatusText(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAnswer = (qIndex: number, option: string) => {
    if (showResults) return;
    setSelectedAnswers((prev) => ({ ...prev, [qIndex]: option }));
  };

  const handleSubmitQuiz = () => {
    setShowResults(true);
    const correct = quiz.filter((q, i) => selectedAnswers[i] === q.answer).length;
    setStatusText(`Quiz submitted. Score: ${correct}/${quiz.length}`);
  };

  const handleSendChat = async () => {
    if (!chatInput.trim() || chatLoading || !docContent) return;
    const userMsg: ChatMessage = { role: "user", content: chatInput.trim() };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput("");
    setChatLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text_content: docContent,
          message: userMsg.content,
          history: [...chatMessages, userMsg],
        }),
      });
      if (!response.ok) throw new Error("Chat request failed");
      const data = await response.json();
      setChatMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch {
      setChatMessages((prev) => [...prev, { role: "assistant", content: "Error: Could not reach the API." }]);
    } finally {
      setChatLoading(false);
    }
  };

  const isLoading = loadingSummary || loadingFlashcards || loadingQuiz;

  return (
    <div className="flex flex-1 h-[calc(100vh-52px)]">
      {/* Main area */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="border-b-2 border-[var(--border-color)] px-4 py-2 flex items-center gap-3 bg-[var(--bg-secondary)]">
          <button onClick={() => router.push("/")} className="btn-ghost flex items-center gap-1 text-[11px]">
            <IconBack /> Back
          </button>
          <div className="h-4 w-px bg-[var(--border-light)]" />

          {/* Tabs */}
          <div className="flex gap-0 border border-[var(--border-light)]">
            {(["summary", "flashcards", "quiz"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-1.5 text-[11px] font-bold uppercase tracking-wider transition-colors ${
                  activeTab === tab
                    ? "bg-[var(--fg-primary)] text-[var(--bg-primary)]"
                    : "hover:bg-[var(--bg-tertiary)] text-[var(--fg-secondary)]"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="flex-1" />

          <button
            onClick={() => generateMaterial(activeTab)}
            disabled={!docContent || isLoading}
            className="btn-primary text-[10px] py-1.5"
          >
            {isLoading ? "Processing..." : `Generate ${activeTab}`}
          </button>

          <div className="h-4 w-px bg-[var(--border-light)]" />

          <button
            onClick={() => setChatOpen(!chatOpen)}
            className={`btn-ghost flex items-center gap-1 text-[11px] ${chatOpen ? "bg-[var(--bg-tertiary)]" : ""}`}
          >
            <IconChat /> Chat
          </button>
        </div>

        {/* Document info bar */}
        <div className="px-4 py-2 text-[11px] text-[var(--fg-muted)] border-b border-[var(--border-light)] flex gap-6 bg-[var(--bg-secondary)]">
          <span>
            <span className="font-bold text-[var(--fg-secondary)]">DOC</span> {docName}
          </span>
          <span>
            <span className="font-bold text-[var(--fg-secondary)]">ID</span> {docId}
          </span>
          <span>
            <span className="font-bold text-[var(--fg-secondary)]">SIZE</span> {docContent?.length || 0} chars
          </span>
        </div>

        {/* Content area */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-[800px] mx-auto">
            {/* ---- SUMMARY TAB ---- */}
            {activeTab === "summary" && (
              <div className="space-y-1">
                {loadingSummary && (
                  <div className="space-y-3 py-8">
                    <div className="skeleton w-3/4 h-5" />
                    <div className="skeleton w-full" />
                    <div className="skeleton w-5/6" />
                    <div className="skeleton w-full" />
                    <div className="skeleton w-2/3" />
                  </div>
                )}
                {!loadingSummary && !summaryData && (
                  <div className="text-center py-16 space-y-3">
                    <div className="text-[var(--fg-muted)] text-sm">No summary generated yet.</div>
                    <button onClick={() => generateMaterial("summary")} disabled={!docContent} className="btn-primary">
                      Generate Summary
                    </button>
                  </div>
                )}
                {!loadingSummary && summaryData && (
                  <div className="fade-in">
                    <h1 className="text-lg font-bold mb-6 pb-3 border-b-2 border-[var(--border-color)]">
                      {summaryData.title}
                    </h1>
                    <div className="mb-6">
                      <div className="text-[11px] font-bold uppercase tracking-wider text-[var(--fg-muted)] mb-3">
                        Table of Contents
                      </div>
                      <div className="border-2 border-[var(--border-color)]">
                        {summaryData.sections.map((section, i) => (
                          <button
                            key={i}
                            onClick={() => setExpandedSection(expandedSection === i ? null : i)}
                            className="w-full text-left border-b border-[var(--border-light)] last:border-b-0 hover:bg-[var(--bg-tertiary)] transition-colors"
                          >
                            <div className="px-4 py-3 flex items-center gap-3">
                              <span className="text-[var(--fg-muted)] text-[11px] font-bold w-6">
                                {String(i + 1).padStart(2, "0")}
                              </span>
                              <span className="flex-1 font-semibold text-[13px]">{section.heading}</span>
                              <span className="text-[var(--fg-muted)]">
                                {expandedSection === i ? <IconCollapse /> : <IconExpand />}
                              </span>
                            </div>
                            {expandedSection === i && (
                              <div className="px-4 pb-4 pl-[52px] text-[13px] text-[var(--fg-secondary)] leading-relaxed border-t border-[var(--border-light)] pt-3">
                                {section.summary}
                              </div>
                            )}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ---- FLASHCARDS TAB ---- */}
            {activeTab === "flashcards" && (
              <div>
                {loadingFlashcards && (
                  <div className="space-y-3 py-8">
                    <div className="skeleton w-1/2 h-5" />
                    <div className="skeleton w-full h-32" />
                    <div className="skeleton w-1/3" />
                  </div>
                )}
                {!loadingFlashcards && flashcards.length === 0 && (
                  <div className="text-center py-16 space-y-3">
                    <div className="text-[var(--fg-muted)] text-sm">No flashcards generated yet.</div>
                    <button onClick={() => generateMaterial("flashcards")} disabled={!docContent} className="btn-primary">
                      Generate Flashcards
                    </button>
                  </div>
                )}
                {!loadingFlashcards && flashcards.length > 0 && (
                  <div className="fade-in">
                    <FlashcardView cards={flashcards.map((c) => ({ q: c.question, a: c.answer }))} />
                  </div>
                )}
              </div>
            )}

            {/* ---- QUIZ TAB ---- */}
            {activeTab === "quiz" && (
              <div className="space-y-4">
                {loadingQuiz && (
                  <div className="space-y-3 py-8">
                    <div className="skeleton w-2/3 h-5" />
                    <div className="skeleton w-full h-12" />
                    <div className="skeleton w-full h-12" />
                    <div className="skeleton w-full h-12" />
                  </div>
                )}
                {!loadingQuiz && quiz.length === 0 && (
                  <div className="text-center py-16 space-y-3">
                    <div className="text-[var(--fg-muted)] text-sm">No quiz generated yet.</div>
                    <button onClick={() => generateMaterial("quiz")} disabled={!docContent} className="btn-primary">
                      Generate Quiz
                    </button>
                  </div>
                )}
                {!loadingQuiz &&
                  quiz.map((q, qIndex) => (
                    <div key={qIndex} className="border-2 border-[var(--border-color)] fade-in">
                      <div className="px-4 py-3 border-b border-[var(--border-light)] bg-[var(--bg-tertiary)]">
                        <span className="font-bold text-[11px] text-[var(--fg-muted)]">QUESTION {qIndex + 1}</span>
                      </div>
                      <div className="p-4">
                        <div className="font-semibold mb-4">{q.question}</div>
                        <div className="space-y-2">
                          {q.options.map((opt) => {
                            const isSelected = selectedAnswers[qIndex] === opt;
                            const isCorrect = showResults && opt === q.answer;
                            const isWrong = showResults && isSelected && opt !== q.answer;

                            return (
                              <button
                                key={opt}
                                onClick={() => handleSelectAnswer(qIndex, opt)}
                                className={`block w-full text-left border-2 p-3 text-[13px] transition-colors ${
                                  isCorrect
                                    ? "border-[var(--success)] bg-[var(--success)] text-white font-bold"
                                    : isWrong
                                    ? "border-[var(--danger)] bg-[var(--danger)] text-white font-bold"
                                    : isSelected
                                    ? "border-[var(--fg-primary)] bg-[var(--fg-primary)] text-[var(--bg-primary)]"
                                    : "border-[var(--border-light)] hover:border-[var(--border-color)] hover:bg-[var(--bg-tertiary)]"
                                }`}
                              >
                                {opt}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  ))}
                {!loadingQuiz && quiz.length > 0 && !showResults && (
                  <button
                    onClick={handleSubmitQuiz}
                    disabled={Object.keys(selectedAnswers).length < quiz.length}
                    className="btn-primary w-full"
                  >
                    Submit Quiz ({Object.keys(selectedAnswers).length}/{quiz.length} answered)
                  </button>
                )}
                {showResults && (
                  <div className="border-2 border-[var(--success)] p-4 text-center">
                    <div className="font-bold text-lg">
                      Score: {quiz.filter((q, i) => selectedAnswers[i] === q.answer).length}/{quiz.length}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Status bar */}
        <div className="status-bar border-t border-[var(--border-light)]">
          <span>{statusText}</span>
          <span className="text-[10px]">{activeTab.toUpperCase()}</span>
        </div>
      </div>

      {/* Chat sidebar */}
      {chatOpen && (
        <aside className="w-[350px] border-l-2 border-[var(--border-color)] flex flex-col bg-[var(--bg-secondary)] fade-in">
          <div className="panel-header">
            <span>Chat with AI</span>
            <button className="btn-ghost text-[10px]" onClick={() => setChatOpen(false)}>
              Close
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {chatMessages.length === 0 && (
              <div className="text-center text-[var(--fg-muted)] text-[11px] py-8">
                Ask questions about this document. The AI has full context of the content.
              </div>
            )}
            {chatMessages.map((msg, i) => (
              <div key={i} className={`fade-in ${msg.role === "user" ? "text-right" : ""}`}>
                <div className="text-[10px] font-bold uppercase text-[var(--fg-muted)] mb-1">
                  {msg.role === "user" ? "You" : "EduSpark AI"}
                </div>
                <div
                  className={`inline-block text-left text-[12px] leading-relaxed p-3 max-w-[90%] ${
                    msg.role === "user"
                      ? "bg-[var(--fg-primary)] text-[var(--bg-primary)] border-2 border-[var(--fg-primary)]"
                      : "border-2 border-[var(--border-color)] bg-[var(--bg-tertiary)]"
                  }`}
                >
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="fade-in">
                <div className="text-[10px] font-bold uppercase text-[var(--fg-muted)] mb-1">EduSpark AI</div>
                <div className="border-2 border-[var(--border-color)] bg-[var(--bg-tertiary)] p-3">
                  <div className="skeleton w-3/4" />
                  <div className="skeleton w-1/2" />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="border-t-2 border-[var(--border-color)] p-3 flex gap-2">
            <input
              type="text"
              className="input-field text-[12px] py-2"
              placeholder="Ask about this document..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
              disabled={chatLoading}
            />
            <button
              onClick={handleSendChat}
              disabled={chatLoading || !chatInput.trim()}
              className="btn-primary px-3 py-2"
            >
              <IconSend />
            </button>
          </div>
        </aside>
      )}
    </div>
  );
}
