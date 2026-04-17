import { ChatInterface } from '@/components/chat/chat-interface'

export default function ChatPage() {
  return (
    <div className="flex h-full flex-col">
      <header className="border-b p-6">
        <h1 className="text-2xl font-semibold text-foreground">知识大脑</h1>
        <p className="mt-1 text-muted-foreground">
          面向 reviewed knowledge、跨源吸收、多模型判断和对话式综合的工作面。
          它不是孤立聊天入口，而是信息大脑之上的知识沉淀层。
        </p>
      </header>
      <ChatInterface />
    </div>
  )
}
