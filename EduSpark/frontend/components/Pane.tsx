import { ReactNode } from "react";

interface PaneProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export function Pane({ title, children, className = "" }: PaneProps) {
  return (
    <div className={`border-2 border-black dark:border-white flex flex-col bg-white dark:bg-black ${className}`}>
      <div className="border-b-2 border-black dark:border-white p-2 font-bold uppercase tracking-widest text-xs bg-black text-white dark:bg-white dark:text-black flex justify-between">
        <span>[{title}]</span>
        <span className="animate-pulse">_</span>
      </div>
      <div className="flex-1 p-4 overflow-auto">
        {children}
      </div>
    </div>
  );
}
