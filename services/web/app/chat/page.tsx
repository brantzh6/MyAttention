import { ChatInterface } from '@/components/chat/chat-interface'

export default function ChatPage() {
  return (
    <div className="flex h-full flex-col">
      <header className="border-b p-6">
        <h1 className="text-2xl font-semibold text-foreground">智能对话</h1>
        <p className="mt-1 text-muted-foreground">基于知识库、多模型投票和联网能力的智能问答。</p>
      </header>
      <ChatInterface />
    </div>
  )
}
