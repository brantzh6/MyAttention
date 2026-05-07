export const FLYWHEEL_HANDOFF_STORAGE_KEY = 'ike.flywheelHandoff.v1'

export interface FlywheelHandoffPayload {
  source: 'chat'
  text: string
  topic?: string
  taskIntent?: string
  conversationId?: string | null
  messageId?: string
  role?: 'user' | 'assistant'
  createdAt: string
}

export function buildChatFlywheelHandoff(params: {
  text: string
  topic?: string
  taskIntent?: string
  conversationId?: string | null
  messageId?: string
  role?: 'user' | 'assistant'
}): FlywheelHandoffPayload {
  return {
    source: 'chat',
    text: params.text,
    topic: params.topic,
    taskIntent: params.taskIntent,
    conversationId: params.conversationId,
    messageId: params.messageId,
    role: params.role,
    createdAt: new Date().toISOString(),
  }
}

export function parseFlywheelHandoffPayload(raw: string | null): FlywheelHandoffPayload | null {
  if (!raw) return null

  try {
    const parsed = JSON.parse(raw) as Partial<FlywheelHandoffPayload>
    if (parsed.source !== 'chat' || typeof parsed.text !== 'string' || !parsed.text.trim()) {
      return null
    }
    return {
      source: 'chat',
      text: parsed.text,
      topic: typeof parsed.topic === 'string' ? parsed.topic : undefined,
      taskIntent: typeof parsed.taskIntent === 'string' ? parsed.taskIntent : undefined,
      conversationId: typeof parsed.conversationId === 'string' ? parsed.conversationId : null,
      messageId: typeof parsed.messageId === 'string' ? parsed.messageId : undefined,
      role: parsed.role === 'user' || parsed.role === 'assistant' ? parsed.role : undefined,
      createdAt: typeof parsed.createdAt === 'string' ? parsed.createdAt : new Date().toISOString(),
    }
  } catch {
    return null
  }
}
