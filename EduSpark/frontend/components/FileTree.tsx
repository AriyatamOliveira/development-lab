interface UploadedItem {
  id: string;
  name: string;
  type: "pdf" | "youtube" | "text";
  content: string;
  timestamp: string;
}

interface FileTreeProps {
  items: UploadedItem[];
  onSelect: (item: UploadedItem) => void;
}

const typeLabel: Record<string, string> = {
  pdf: "PDF",
  youtube: "YT",
  text: "TXT",
};

export function FileTree({ items, onSelect }: FileTreeProps) {
  return (
    <div className="font-mono text-sm space-y-1 h-full">
      {/* Root */}
      <div className="flex items-center gap-2 p-1 font-bold">
        <span>[-]</span> <span>/workspace</span>
      </div>

      {/* Documents folder */}
      <div className="flex items-center gap-2 p-1 pl-6 font-bold">
        <span>{items.length > 0 ? "[-]" : "[+]"}</span> <span>documents/</span>
        <span className="ml-auto text-xs opacity-50">{items.length} items</span>
      </div>

      {/* Dynamic items */}
      {items.length === 0 && (
        <div className="pl-12 p-1 opacity-40 text-xs italic">
          (empty -- upload content to populate)
        </div>
      )}
      {items.map((item) => (
        <div
          key={item.id}
          onClick={() => onSelect(item)}
          className="flex items-center gap-2 cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-800 p-1 pl-12 group"
        >
          <span className="opacity-50">|--</span>
          <span className="flex-1 truncate group-hover:underline">{item.name}</span>
          <span className="text-xs opacity-50 border border-black dark:border-white px-1">
            {typeLabel[item.type] || "?"}
          </span>
        </div>
      ))}

      {/* Static folders */}
      <div className="flex items-center gap-2 p-1 pl-6 font-bold opacity-40">
        <span>[+]</span> <span>generated/</span>
      </div>
      <div className="flex items-center gap-2 p-1 pl-6 font-bold opacity-40">
        <span>[+]</span> <span>exports/</span>
      </div>
    </div>
  );
}
