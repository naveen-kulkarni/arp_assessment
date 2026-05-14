"""AI agent orchestration for the ARP Assessment platform."""
import json
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from src.backend.models import User, AuditLog
from src.backend.tools import TOOLS, ToolContext
from src.backend.config import get_settings
import requests

settings = get_settings()


class AgentOrchestrator:
    """Orchestrate AI agent interactions."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def execute_query(self, user: User, question: str) -> Dict[str, Any]:
        """Execute a user query through the agent."""
        
        # Create tool context
        context = ToolContext(self.db, user)
        
        # Determine which tools to use based on the question
        tools_to_call = self._determine_tools(question)
        
        # Check access for all tools
        denied_tools = [t for t in tools_to_call if not context.check_access(t)]
        
        if denied_tools:
            # Log denied access
            self._log_audit(
                user=user.username,
                role=user.role.value,
                question=question,
                tools_called=json.dumps(tools_to_call),
                result="Access denied",
                allowed=False,
                denial_reason=f"User does not have access to: {', '.join(denied_tools)}"
            )
            return {
                "error": "Access denied",
                "denied_tools": denied_tools,
            }
        
        # Execute tools
        tool_results = {}
        for tool_name in tools_to_call:
            if tool_name in TOOLS:
                try:
                    result = TOOLS[tool_name](context)
                    tool_results[tool_name] = result
                except Exception as e:
                    tool_results[tool_name] = {"error": str(e)}
        
        # Generate response using LLM
        response = self._generate_response(question, tool_results, user.role.value)
        
        # Log successful query
        self._log_audit(
            user=user.username,
            role=user.role.value,
            question=question,
            tools_called=json.dumps(tools_to_call),
            result=response.get("summary", ""),
            allowed=True,
        )
        
        return {
            "question": question,
            "answer": response.get("answer", ""),
            "summary": response.get("summary", ""),
            "tools_used": tools_to_call,
            "data": tool_results,
        }
    
    def _determine_tools(self, question: str) -> List[str]:
        """Determine which tools to call based on the question."""
        question_lower = question.lower()
        
        tools = []
        
        # Keyword matching for tool selection
        if any(word in question_lower for word in ["portfolio", "holdings", "exposure", "assets"]):
            tools.append("get_asset_exposure")
        
        if any(word in question_lower for word in ["summary", "overview", "total", "value"]):
            tools.append("get_portfolio_summary")
        
        if any(word in question_lower for word in ["trade", "recent", "history"]):
            tools.append("get_recent_trades")
        
        if any(word in question_lower for word in ["risk", "alert", "flag", "high risk"]):
            if "trade" in question_lower:
                tools.append("get_high_risk_trades")
            else:
                tools.append("get_risk_alerts")
        
        if any(word in question_lower for word in ["market", "price", "volume"]):
            tools.append("get_market_data")
        
        if any(word in question_lower for word in ["rule", "policy"]):
            tools.append("check_risk_rules")
        
        # If no tools determined, get portfolio summary as default
        if not tools:
            tools.append("get_portfolio_summary")
        
        # Remove duplicates
        return list(set(tools))
    
    def _generate_response(self, question: str, tool_results: Dict[str, Any], role: str) -> Dict[str, Any]:
        """Generate response using LLM or mock logic."""
        
        if settings.LLM_TYPE == "ollama":
            return self._generate_response_ollama(question, tool_results, role)
        else:
            return self._generate_response_mock(question, tool_results, role)
    
    def _generate_response_mock(self, question: str, tool_results: Dict[str, Any], role: str) -> Dict[str, Any]:
        """Generate mock response without external LLM."""
        
        # Build context from tool results
        context_text = json.dumps(tool_results, indent=2, default=str)
        
        # Craft response based on question and results
        summary = self._summarize_results(question, tool_results)
        
        answer = f"Based on the data analysis:\n\n{summary}\n\n[Generated for {role} role]\n\nDetailed data:\n{context_text}"
        
        return {
            "answer": answer,
            "summary": summary,
        }
    
    def _generate_response_ollama(self, question: str, tool_results: Dict[str, Any], role: str) -> Dict[str, Any]:
        """Generate response using Ollama."""
        
        try:
            context_text = json.dumps(tool_results, indent=2, default=str)
            
            prompt = f"""You are an investment operations AI assistant. Answer the following question based on the provided data.
            
Question: {question}
User Role: {role}

Data:
{context_text}

Provide a concise, professional answer in 2-3 sentences."""
            
            response = requests.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=30,
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "")
                summary = answer[:200]
                return {"answer": answer, "summary": summary}
        except Exception as e:
            print(f"Ollama error: {e}")
        
        # Fallback to mock response
        return self._generate_response_mock(question, tool_results, role)
    
    def _summarize_results(self, question: str, tool_results: Dict[str, Any]) -> str:
        """Summarize tool results."""
        summaries = []
        
        if "get_portfolio_summary" in tool_results:
            data = tool_results["get_portfolio_summary"]
            if "error" not in data:
                total = data.get("total_portfolio_value", 0)
                allocation = data.get("allocation_percentage", {})
                summaries.append(f"Portfolio total value: ${total:,.2f}. Allocation: {', '.join([f'{k}: {v}%' for k, v in allocation.items()])}")
        
        if "get_risk_alerts" in tool_results:
            data = tool_results["get_risk_alerts"]
            if "error" not in data:
                alerts = data.get("total_alerts", 0)
                high = data.get("high_severity", 0)
                summaries.append(f"Risk alerts: {alerts} total, {high} high severity")
        
        if "get_recent_trades" in tool_results:
            data = tool_results["get_recent_trades"]
            if "error" not in data:
                total = data.get("total_trades", 0)
                summaries.append(f"Recent trades: {total} transactions")
        
        if "get_high_risk_trades" in tool_results:
            data = tool_results["get_high_risk_trades"]
            if "error" not in data:
                total = data.get("total", 0)
                summaries.append(f"High-risk trades: {total} flagged")
        
        return " | ".join(summaries) if summaries else "Query executed successfully."
    
    def _log_audit(
        self,
        user: str,
        role: str,
        question: str,
        tools_called: str,
        result: str,
        allowed: bool,
        denial_reason: Optional[str] = None,
    ):
        """Log audit entry."""
        audit_log = AuditLog(
            user=user,
            role=role,
            question=question,
            tools_called=tools_called,
            result=result[:500],  # Truncate if too long
            allowed=allowed,
            denial_reason=denial_reason,
            timestamp=datetime.utcnow(),
        )
        self.db.add(audit_log)
        self.db.commit()
