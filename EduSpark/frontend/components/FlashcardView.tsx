"use client";

import { useState } from "react";

export function FlashcardView({ cards }: { cards: { q: string; a: string }[] }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);

  if (cards.length === 0) return <div className="text-[var(--fg-muted)]">No flashcards available.</div>;

  const card = cards[currentIndex];

  return (
    <div className="flex flex-col gap-4">
      {/* Progress bar */}
      <div className="flex items-center gap-3 text-[11px]">
        <span className="font-bold text-[var(--fg-muted)]">CARD {currentIndex + 1} / {cards.length}</span>
        <div className="flex-1 h-[2px] bg-[var(--border-light)]">
          <div
            className="h-full bg-[var(--fg-primary)] transition-all duration-300"
            style={{ width: `${((currentIndex + 1) / cards.length) * 100}%` }}
          />
        </div>
        <span className="font-bold text-[11px] text-[var(--fg-muted)]">
          {flipped ? "ANSWER" : "QUESTION"}
        </span>
      </div>

      {/* Card */}
      <div
        className="border-2 border-[var(--border-color)] p-8 min-h-[200px] flex items-center justify-center text-center cursor-pointer hover:bg-[var(--bg-tertiary)] transition-colors select-none"
        onClick={() => setFlipped(!flipped)}
      >
        <div className="space-y-3">
          <div className="text-[10px] uppercase font-bold text-[var(--fg-muted)] tracking-wider">
            {flipped ? "Answer" : "Question"} -- Click to flip
          </div>
          <div className="text-[15px] leading-relaxed font-medium">
            {flipped ? card.a : card.q}
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex gap-2">
        <button
          disabled={currentIndex === 0}
          onClick={() => { setCurrentIndex((i) => i - 1); setFlipped(false); }}
          className="btn-primary flex-1"
        >
          Previous
        </button>
        <button
          disabled={currentIndex === cards.length - 1}
          onClick={() => { setCurrentIndex((i) => i + 1); setFlipped(false); }}
          className="btn-primary flex-1"
        >
          Next
        </button>
      </div>
    </div>
  );
}
