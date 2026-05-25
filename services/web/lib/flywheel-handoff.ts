export const FLYWHEEL_HANDOFF_STORAGE_KEY = 'ike.flywheelHandoff.v1'

export interface FlywheelHandoffPayload {
  source: 'chat'
  text: string
  topic?: string
  taskIntent?: string
  conversationId?: string | null
  messageId?: string
  role?: 'user' | 'assistant'
  brainRouteId?: string
  primaryBrain?: string
  thinkingFramework?: string
  createdAt: string
}

export function buildChatFlywheelHandoff(params: {
  text: string
  topic?: string
  taskIntent?: string
  conversationId?: string | null
  messageId?: string
  role?: 'user' | 'assistant'
  brainRouteId?: string
  primaryBrain?: string
  thinkingFramework?: string
}): FlywheelHandoffPayload {
  return {
    source: 'chat',
    text: params.text,
    topic: params.topic,
    taskIntent: params.taskIntent,
    conversationId: params.conversationId,
    messageId: params.messageId,
    role: params.role,
    brainRouteId: params.brainRouteId,
    primaryBrain: params.primaryBrain,
    thinkingFramework: params.thinkingFramework,
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
      brainRouteId: typeof parsed.brainRouteId === 'string' ? parsed.brainRouteId : undefined,
      primaryBrain: typeof parsed.primaryBrain === 'string' ? parsed.primaryBrain : undefined,
      thinkingFramework: typeof parsed.thinkingFramework === 'string' ? parsed.thinkingFramework : undefined,
      createdAt: typeof parsed.createdAt === 'string' ? parsed.createdAt : new Date().toISOString(),
    }
  } catch {
    return null
  }
}
