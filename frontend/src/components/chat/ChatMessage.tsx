"use client";

import React from "react";
import { Bot, User } from "lucide-react";
import { Message } from "@/types/chat";
import { AgentActivity } from "./AgentActivity";
import { Sources } from "./Sources";

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.sender === "user";

  if (isUser) {
    return (
      <div className="flex gap-3 justify-end my-4">
        <div className="flex flex-col items-end">
          <div className="bg-slate-100/90 border border-slate-200/80 text-slate-900 px-4 py-3 rounded-2xl rounded-tr-none text-sm max-w-xl shadow-xs">
            <p className="leading-relaxed whitespace-pre-wrap font-medium">{message.content}</p>
          </div>
          <span className="text-[10px] text-slate-400 font-mono mt-1 pr-1">{message.timestamp}</span>
        </div>
        <div className="w-8 h-8 rounded-full bg-slate-200 text-slate-700 text-xs font-semibold flex items-center justify-center shrink-0">
          LK
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3 justify-start my-5">
      <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-sm">
        <Bot className="w-4.5 h-4.5" />
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none p-4 text-sm max-w-2xl shadow-xs text-slate-800">
        {message.isThinking ? (
          <div className="flex items-center gap-2 text-slate-500 py-1">
            <div className="w-4 h-4 rounded-full border-2 border-slate-300 border-t-blue-600 animate-spin" />
            <span className="text-xs font-medium">ParcelPilot AI is investigating...</span>
          </div>
        ) : (
          <>
            <div className="prose prose-slate max-w-none text-sm leading-relaxed whitespace-pre-wrap space-y-2">
              {message.content}
            </div>

            {message.agentSteps && <AgentActivity steps={message.agentSteps} />}
            {message.sources && <Sources sources={message.sources} />}
          </>
        )}
      </div>
    </div>
  );
};
