import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EduSpark Engine",
  description: "AI-Powered Study Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen flex flex-col font-mono text-[13px]">
        <header className="border-b-2 border-[var(--border-color)] px-6 py-3 flex justify-between items-center bg-[var(--bg-secondary)]">
          <div className="flex items-center gap-3">
            <div className="font-bold text-sm tracking-wide">EDUSPARK</div>
            <div className="text-[10px] text-[var(--fg-muted)] border-l border-[var(--border-light)] pl-3">ENGINE v2.0</div>
          </div>
          <div className="flex items-center gap-4 text-[11px] text-[var(--fg-muted)]">
            <span>BACKEND: CONNECTED</span>
            <span className="w-2 h-2 bg-[var(--success)] inline-block"></span>
          </div>
        </header>
        <main className="flex-grow flex flex-col">
          {children}
        </main>
      </body>
    </html>
  );
}
