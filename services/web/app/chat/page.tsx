import { ChatInterface } from '@/components/chat/chat-interface'

export default function ChatPage() {
  return (
    <div className="h-full flex flex-col">
      <header className="p-6 border-b">
        <h1 className="text-2xl font-semibold text-foreground">智能对话</h1>
        <p className="text-muted-foreground mt-1">基于知识库的智能问答</p>
      </header>
      <ChatInterface />
    </div>
  )
}
