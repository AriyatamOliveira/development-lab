export function TerminalLog({ logs }: { logs: string[] }) {
  return (
    <div className="h-full bg-black text-[#00ff00] dark:bg-black dark:text-[#00ff00] p-4 overflow-y-auto font-mono text-sm selection:bg-[#00ff00] selection:text-black shadow-inner">
      <div className="mb-4 opacity-70 border-b-2 border-[#00ff00] pb-2">
        EduSpark v1.0.0 Terminal
        <br />Type 'help' for more information.
      </div>
      {logs.map((log, i) => (
        <div key={i} className="mb-1 flex gap-2">
          <span className="opacity-50 min-w-[75px]" suppressHydrationWarning>[{new Date().toISOString().split("T")[1].split(".")[0]}]</span> 
          <span className="text-white">{log}</span>
        </div>
      ))}
      <div className="animate-pulse mt-1 flex gap-2">
        <span className="opacity-50 min-w-[75px]" suppressHydrationWarning>[{new Date().toISOString().split("T")[1].split(".")[0]}]</span>
        <span className="bg-[#00ff00] text-black">_</span>
      </div>
    </div>
  );
}
