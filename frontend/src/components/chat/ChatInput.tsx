"use client";

import React, { useState } from "react";
import { Paperclip, Send, RotateCw } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (text: string) => void;
  quickPrompts: string[];
  onSelectPrompt: (prompt: string) => void;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  quickPrompts,
  onSelectPrompt,
  disabled = false,
}) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSendMessage(input.trim());
    setInput("");
  };

  return (
    <div className="p-4 bg-white/80 border-t border-slate-200/80 shrink-0">
      <div className="max-w-3xl mx-auto space-y-3">
        {/* Quick Suggested Prompts Pill Container */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
          {quickPrompts.map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onSelectPrompt(prompt)}
              className="px-3 py-1.5 rounded-full bg-slate-100/80 hover:bg-slate-200/80 border border-slate-200/60 text-xs font-medium text-slate-700 transition-colors whitespace-nowrap shrink-0"
            >
              {prompt}
            </button>
          ))}
          <button
            type="button"
            className="p-1.5 rounded-full bg-slate-100/80 hover:bg-slate-200 border border-slate-200/60 text-slate-500 hover:text-slate-800 transition-colors shrink-0"
            title="Refresh suggested prompts"
          >
            <RotateCw className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Input Box Bar */}
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex items-center gap-2 bg-white border border-slate-200 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 rounded-xl px-3 py-2 shadow-xs transition-all">
            <button
              type="button"
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-colors"
              title="Attach document or file"
            >
              <Paperclip className="w-4 h-4" />
            </button>

            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask ParcelPilot AI anything..."
              disabled={disabled}
              className="flex-1 bg-transparent text-sm text-slate-900 placeholder-slate-400 outline-none"
            />

            <button
              type="submit"
              disabled={!input.trim() || disabled}
              className="p-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-all disabled:opacity-40 disabled:hover:bg-blue-600 shadow-sm"
              title="Send message"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>

          <p className="text-center text-[11px] text-slate-400 mt-2">
            ParcelPilot AI can make mistakes. Verify important information.
          </p>
        </form>
      </div>
    </div>
  );
};
