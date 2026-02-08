"""LLM-based fraud risk assessment agent."""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.retrieval import retrieve_context
from src.prompts import SYSTEM_PROMPT, USER_PROMPT
from src.schemas import RiskAssessment
from src.decision_logic import apply_decision_logic

api_key = os.getenv('OPENAI_API_KEY')

# Enforce deterministic LLM behavior for stability
llm = ChatOpenAI(temperature=0.0, api_key=api_key)

# Directory to persist raw responses and parse errors for offline analysis
REPORTS_DIR = Path("reports")
RAW_DIR = REPORTS_DIR / "raw_responses"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PARSE_LOG = REPORTS_DIR / "parse_errors.log"


def run_agent(transaction: dict) -> RiskAssessment:
    """Assess transaction fraud risk. Input: dict. Output: RiskAssessment."""
    context_docs = retrieve_context(json.dumps(transaction))
    context = "\n".join([d.page_content for d in context_docs])

    prompt = USER_PROMPT.format(transaction=json.dumps(transaction), context=context)
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    raw = response.content

    try:
        assessment = RiskAssessment.parse_raw(raw)
    except Exception:
        parsed = _fallback_parse(raw)
        assessment = RiskAssessment(
            risk_level=parsed.get('risk_level', 'medium'),
            key_risk_factors=parsed.get('key_risk_factors', []),
            policy_references=parsed.get('policy_references', []),
            recommended_action=parsed.get('recommended_action', 'review'),
            confidence=parsed.get('confidence', 0.0)
        )

    try:
        assessment.raw_response = {
            'raw_text': raw,
            'timestamp': datetime.utcnow().isoformat(),
            'transaction_id': transaction.get('id', 'unknown')
        }
    except Exception:
        pass

    deterministic = apply_decision_logic(assessment.copy())
    if (assessment.recommended_action or '').strip().lower() != (deterministic.recommended_action or '').strip().lower():
        assessment.validation_flag = True
        assessment.validation_notes = f"Overrode LLM action ('{assessment.recommended_action}') to deterministic ('{deterministic.recommended_action}')"
        assessment.recommended_action = deterministic.recommended_action
    else:
        assessment.validation_flag = False

    _persist_raw_output(transaction=transaction, raw=raw, final_assessment=assessment)
    return assessment


def _fallback_parse(raw_text: str) -> dict:
    """Very forgiving parser: extract risk_level, action, confidence, and simple lists."""
    out = {}
    rl = re.search(r'"?risk_level"?\s*[:=]\s*"?(low|medium|high)"?', raw_text, re.I)
    if rl:
        out['risk_level'] = rl.group(1).lower()
    ra = re.search(r'"?recommended_action"?\s*[:=]\s*"?(approve|block|review)"?', raw_text, re.I)
    if ra:
        out['recommended_action'] = ra.group(1).lower()
    conf = re.search(r'"?confidence"?\s*[:=]\s*([0-9]*\.?[0-9]+)', raw_text)
    if conf:
        try:
            out['confidence'] = float(conf.group(1))
        except Exception:
            out['confidence'] = 0.0
    # simple list heuristics
    kr = re.findall(r'key_risk_factors[\]\)\}]*[:=]\s*\[([^\]]+)\]', raw_text, re.I)
    if kr:
        items = re.split(r"\s*,\s*", kr[0])
        out['key_risk_factors'] = [i.strip(' \"\'') for i in items if i.strip()]
    # policy refs heuristic
    prs = re.findall(r'policy_references[\]\)\}]*[:=]\s*\[([^\]]+)\]', raw_text, re.I)
    if prs:
        items = re.split(r"\s*,\s*", prs[0])
        out['policy_references'] = [i.strip(' \"\'') for i in items if i.strip()]
    return out


def _persist_raw_output(transaction: dict, raw: str, final_assessment: RiskAssessment) -> None:
    """Append a single JSON line containing transaction id, timestamp, raw LLM output and final assessment."""
    try:
        fname = RAW_DIR / f"llm_outputs_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        payload = {
            'timestamp': datetime.utcnow().isoformat(),
            'transaction_id': transaction.get('id'),
            'raw': raw,
            'final_assessment': json.loads(final_assessment.json())
        }
        with fname.open('a', encoding='utf-8') as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        logger.exception('Failed to persist raw LLM output')
