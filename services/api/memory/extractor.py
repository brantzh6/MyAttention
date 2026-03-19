"""
Memory Extractor - AI-powered memory extraction from conversations
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
from dataclasses import dataclass

from llm.adapter import LLMAdapter


@dataclass
class ExtractedFact:
    """A fact extracted from conversation"""
    content: str
    fact_type: str  # preference, fact, decision, insight
    category: Optional[str]
    tags: List[str]
    confidence: float
    source_message_ids: List[str]


class MemoryExtractor:
    """Extract memorable facts from conversations using AI"""
    
    EXTRACTION_PROMPT = """分析以下对话，提取值得长期记忆的重要信息。

对话内容：
{conversation}

请识别以下类型的信息：
1. preference（用户偏好）：用户的喜好、习惯、偏好设置
2. fact（重要事实）：关于用户的背景信息、重要事实
3. decision（决策记录）：用户做出的重要决定
4. insight（洞察总结）：对话中得出的重要结论或学习

对于每条提取的记忆，请给出：
- content: 简洁描述（一句话）
- fact_type: 类型（preference/fact/decision/insight）
- category: 分类标签（如 llm、work、personal 等）
- tags: 关键词列表
- confidence: 可信度（0.5-1.0）

请以 JSON 数组格式返回，如果没有值得记忆的内容，返回空数组 []。

示例输出：
[
  {{"content": "用户偏好使用 qwen-max 模型", "fact_type": "preference", "category": "llm", "tags": ["qwen", "model"], "confidence": 0.9}},
  {{"content": "用户在做 AI Agent 创业项目", "fact_type": "fact", "category": "work", "tags": ["ai", "startup"], "confidence": 0.85}}
]

只返回 JSON 数组，不要其他内容。"""

    SCORING_PROMPT = """评估以下消息是否包含值得长期记忆的信息。

消息：
{message}

上下文：
{context}

评分标准：
- 0.8-1.0: 明确的用户偏好、重要个人信息、关键决策
- 0.6-0.8: 可能有价值的背景信息、一般性偏好
- 0.4-0.6: 普通对话、可能有些参考价值
- 0.0-0.4: 闲聊、问候、无实质内容

请只返回一个 0 到 1 之间的数字，表示记忆价值评分。"""

    def __init__(self):
        self.adapter = LLMAdapter()
    
    async def score_message(
        self,
        message: str,
        context: List[Dict[str, str]],
    ) -> float:
        """Score a message for memory extraction worthiness"""
        # Quick rule-based pre-filtering
        quick_score = self._quick_score(message)
        if quick_score >= 0.8:
            return quick_score
        if quick_score <= 0.2:
            return quick_score
        
        # Use AI for borderline cases
        try:
            context_text = "\n".join([
                f"{m['role']}: {m['content'][:200]}"
                for m in context[-5:]  # Last 5 messages
            ])
            
            prompt = self.SCORING_PROMPT.format(
                message=message,
                context=context_text,
            )
            
            response = await self.adapter.chat(
                message=prompt,
                provider="dashscope",
                model="qwen-turbo",  # Use fast model for scoring
                system_prompt="你是一个记忆评估助手，只返回数字评分。",
            )
            
            # Parse score from response
            score_match = re.search(r"[\d.]+", response)
            if score_match:
                score = float(score_match.group())
                return max(0.0, min(1.0, score))
            
            return 0.5  # Default if parsing fails
            
        except Exception as e:
            print(f"Memory scoring error: {e}")
            return quick_score
    
    def _quick_score(self, message: str) -> float:
        """Quick rule-based scoring for obvious cases"""
        message_lower = message.lower()
        
        # High-value patterns
        high_patterns = [
            r"我喜欢", r"我偏好", r"我更喜欢", r"我习惯",
            r"我是", r"我在", r"我的工作", r"我的公司",
            r"决定", r"选择了", r"采用",
            r"总结", r"结论", r"学到了",
            r"i prefer", r"i like", r"i am", r"i work",
        ]
        
        for pattern in high_patterns:
            if re.search(pattern, message_lower):
                return 0.75
        
        # Low-value patterns
        low_patterns = [
            r"^(好的|嗯|哦|ok|okay|thanks|谢谢|明白)[\s,.!。！]*$",
            r"^(你好|hello|hi|hey)[\s,.!。！]*$",
            r"^(是的|对|没错|yes|right|correct)[\s,.!。！]*$",
        ]
        
        for pattern in low_patterns:
            if re.search(pattern, message_lower):
                return 0.1
        
        # Default for medium cases
        if len(message) < 20:
            return 0.3
        elif len(message) > 200:
            return 0.6
        
        return 0.5
    
    async def extract_facts(
        self,
        messages: List[Dict[str, str]],
        message_ids: Optional[List[str]] = None,
    ) -> List[ExtractedFact]:
        """Extract memorable facts from a conversation"""
        if not messages:
            return []
        
        # Build conversation text
        conversation_text = "\n".join([
            f"{m['role']}: {m['content']}"
            for m in messages
        ])
        
        prompt = self.EXTRACTION_PROMPT.format(conversation=conversation_text)
        
        try:
            response = await self.adapter.chat(
                message=prompt,
                provider="dashscope",
                model="qwen-plus",  # Use better model for extraction
                system_prompt="你是一个记忆提取助手，只返回 JSON 格式。",
            )
            
            # Parse JSON from response
            # Try to find JSON array in response
            json_match = re.search(r"\[[\s\S]*\]", response)
            if json_match:
                facts_data = json.loads(json_match.group())
            else:
                facts_data = json.loads(response)
            
            if not isinstance(facts_data, list):
                return []
            
            # Convert to ExtractedFact objects
            facts = []
            for item in facts_data:
                if not isinstance(item, dict):
                    continue
                
                content = item.get("content", "").strip()
                if not content:
                    continue
                
                fact_type = item.get("fact_type", "fact")
                if fact_type not in ["preference", "fact", "decision", "insight"]:
                    fact_type = "fact"
                
                facts.append(ExtractedFact(
                    content=content,
                    fact_type=fact_type,
                    category=item.get("category"),
                    tags=item.get("tags", []),
                    confidence=min(1.0, max(0.5, item.get("confidence", 0.8))),
                    source_message_ids=message_ids or [],
                ))
            
            return facts
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in memory extraction: {e}")
            return []
        except Exception as e:
            print(f"Memory extraction error: {e}")
            return []
    
    async def should_extract(self, score: float, threshold: float = 0.5) -> bool:
        """Determine if a message should trigger memory extraction"""
        return score >= threshold
    
    async def deduplicate_fact(
        self,
        new_fact: ExtractedFact,
        existing_facts: List[Dict[str, Any]],
        similarity_threshold: float = 0.9,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a fact is duplicate of existing ones.
        Returns (is_duplicate, existing_memory_id if duplicate)
        """
        # Simple text similarity for now
        # Can be enhanced with embedding similarity later
        new_content_lower = new_fact.content.lower()
        
        for existing in existing_facts:
            existing_content_lower = existing.get("content", "").lower()
            
            # Check for high text overlap
            if new_content_lower in existing_content_lower or existing_content_lower in new_content_lower:
                return True, existing.get("memory_id")
            
            # Simple word overlap check
            new_words = set(new_content_lower.split())
            existing_words = set(existing_content_lower.split())
            
            if len(new_words) > 0 and len(existing_words) > 0:
                overlap = len(new_words & existing_words) / max(len(new_words), len(existing_words))
                if overlap >= similarity_threshold:
                    return True, existing.get("memory_id")
        
        return False, None
