"""Text analysis module for detecting investment risk indicators in promotional material."""

import re
from typing import List, Tuple, Dict, Any
from app.models.schemas import FindingItem, FindingCategory, SeverityLevel


class TextRule:
    def __init__(
        self,
        rule_id: str,
        title: str,
        category: FindingCategory,
        severity: SeverityLevel,
        pattern: str,
        explanation: str,
        flags: int = re.IGNORECASE,
    ):
        self.rule_id = rule_id
        self.title = title
        self.category = category
        self.severity = severity
        self.pattern = re.compile(pattern, flags)
        self.explanation = explanation


# Comprehensive indicator rules catalog
TEXT_RULES: List[TextRule] = [
    # 1. Guaranteed returns claims
    TextRule(
        rule_id="text_guaranteed_profit",
        title="Guaranteed Returns or Profit Promise",
        category=FindingCategory.FINANCIAL_PROMISE,
        severity=SeverityLevel.CRITICAL,
        pattern=r"\b(100%\s+guaranteed(\s+(returns?|profits?|income|capital|growth))?|guaranteed\s+(returns?|profits?|income|yield|growth|payouts?|wealth|capital|daily\s+profit)|risk-?free\s+(profit|return|income))\b",
        explanation=(
            "Legitimate financial investments always carry market risk. Promises of guaranteed profits "
            "are one of the strongest hallmarks of fraudulent schemes and high-yield investment programs (HYIPs)."
        ),
    ),
    # 2. Unrealistic periodic returns (e.g., 2% daily, 10% weekly)
    TextRule(
        rule_id="text_unrealistic_rate",
        title="Unrealistically High Periodic Return Claim",
        category=FindingCategory.FINANCIAL_PROMISE,
        severity=SeverityLevel.CRITICAL,
        pattern=r"\b([1-9][0-9]?(\.[0-9]+)?)\s*%\s*(daily|per\s*day|hourly|per\s*hour|a\s*day|every\s*day|weekly|per\s*week|a\s*week)\b",
        explanation=(
            "Promising fixed percentage returns per day, hour, or week is mathematically unsustainable. "
            "For example, even 1% daily compounded equals over 3,678% annually, which is not achievable in genuine investing."
        ),
    ),
    # 3. Capital doubling / tripling promises
    TextRule(
        rule_id="text_capital_multiplier",
        title="Rapid Wealth Multiplier Claim",
        category=FindingCategory.FINANCIAL_PROMISE,
        severity=SeverityLevel.HIGH,
        pattern=r"\b(double\s+your\s+(money|investment|crypto|funds|btc|deposit)|triple\s+your\s+(money|investment)|2x\s+in\s+[0-9]+\s*(hours?|days?)|instant\s+multiplier)\b",
        explanation=(
            "Promises to double or multiply funds within hours or days are standard tactics in ponzi schemes "
            "and cryptocurrency doubling scams."
        ),
    ),
    # 4. Zero risk / No risk claims
    TextRule(
        rule_id="text_zero_risk",
        title="Claim of Zero or No Risk",
        category=FindingCategory.RISK_CLAIM,
        severity=SeverityLevel.HIGH,
        pattern=r"\b(zero\s+risk|no\s+risk|risk-?free|loss\s+impossible|impossible\s+to\s+lose|capital\s+100%\s+safe|protected\s+from\s+any\s+loss)\b",
        explanation=(
            "All authentic investments entail risk of loss. Claiming an investment is 'zero risk' or that losses "
            "are impossible is deceptive and illegal under most financial conduct regulations."
        ),
    ),
    # 5. High-pressure urgency & artificial scarcity
    TextRule(
        rule_id="text_urgency_pressure",
        title="Urgency and Artificial Scarcity Tactic",
        category=FindingCategory.URGENCY_SCARCITY,
        severity=SeverityLevel.MEDIUM,
        pattern=r"\b(act\s+now|limited\s+(spots?|slots?|time|opportunity)|only\s+[0-9]+\s+(slots?|spots?|members?)\s+left|hurry\s+up|before\s+doors\s+close|last\s+chance\s+to\s+join|join\s+before\s+it'?s\s+too\s+late|offer\s+expires\s+in\s+[0-9]+)\b",
        explanation=(
            "Scammers fabricate intense urgency and scarcity to pressure prospective victims into committing money "
            "before they have time to conduct due diligence, consult advisors, or verify regulatory licenses."
        ),
    ),
    # 6. Referral / Downline / MLM commission emphasis
    TextRule(
        rule_id="text_recruitment_incentive",
        title="Recruitment and Referral Incentive Emphasis",
        category=FindingCategory.RECRUITMENT_MLM,
        severity=SeverityLevel.HIGH,
        pattern=r"\b(referral\s+(bonus(es)?|commissions?|rewards?)|invite\s+friends?\s+and\s+earn|downline|binary\s+(plan|tree)|multi-?level|affiliate\s+tiers?|matrix\s+commission|recruit\s+[0-9]+\s+people)\b",
        explanation=(
            "Heavy emphasis on earning through recruiting new members, downlines, or multi-level commissions "
            "is characteristic of pyramid and Ponzi models, where old investors are paid with funds from newcomers."
        ),
    ),
    # 7. Vague / Mythical trading algorithm or automated bot claims
    TextRule(
        rule_id="text_vague_algorithm",
        title="Vague or Mythical Algorithmic Trading Claim",
        category=FindingCategory.VAGUE_MECHANISM,
        severity=SeverityLevel.MEDIUM,
        pattern=r"\b(quantum\s+ai\s+trading|automated\s+(trading\s+bot|profit\s+system)|foolproof\s+algorithm|secret\s+(trading\s+loophole|algorithm)|proprietary\s+crypto\s+bot|100%\s+automated\s+profits?)\b",
        explanation=(
            "Vague descriptions referencing mysterious 'quantum algorithms', 'flawless AI trading bots', or 'secret loopholes' "
            "often obscure the complete absence of any verifiable investment strategy or licensed asset management."
        ),
    ),
    # 8. Demands for direct, irreversible crypto transfers or unusual payments
    TextRule(
        rule_id="text_irreversible_payment",
        title="Direct Irreversible Payment or Crypto Demand",
        category=FindingCategory.PAYMENT_METHOD,
        severity=SeverityLevel.HIGH,
        pattern=r"\b(send\s+(bitcoin|btc|usdt|eth|crypto)([\w\s\-_]{0,25})\s+to\s+([\w\s]{0,15})(wallet|address)|(deposit|transfer)\s+(usdt|btc|bitcoin|crypto|funds)\s+(trc-?20|erc-?20)|usdt\s+(trc-?20|erc-?20)|western\s+union|moneygram|gift\s+cards?|no\s+bank\s+verification\s+needed|direct\s+wallet\s+transfer)\b",
        explanation=(
            "Legitimate investment firms use regulated custodial accounts, escrow, or licensed payment processors. "
            "Demanding direct cryptocurrency wallet transfers, money orders, or gift cards makes payments nearly impossible to trace or reverse."
        ),
    ),
    # 9. Fake celebrity endorsement or media impersonation
    TextRule(
        rule_id="text_celebrity_media",
        title="Celebrity Endorsement or Sensational Media Association",
        category=FindingCategory.AUTHORITY_ENDORSEMENT,
        severity=SeverityLevel.HIGH,
        pattern=r"\b(endorsed\s+by\s+(elon\s+musk|bill\s+gates|jeff\s+bezos|warren\s+buffett)|as\s+seen\s+on\s+(bbc|cnn|shark\s+tank|dragons?\s+den|forbes)|secret\s+(interview|leak)\s+reveals)\b",
        explanation=(
            "Scam campaigns frequently fabricate fake quotes, video deepfakes, or photoshopped news articles "
            "falsely claiming that prominent entrepreneurs, celebrities, or national media outlets have endorsed their platform."
        ),
    ),
    # 10. Unrealistic lifestyle and quick retirement promises
    TextRule(
        rule_id="text_lifestyle_promise",
        title="Extreme Lifestyle or Instant Wealth Promise",
        category=FindingCategory.FINANCIAL_PROMISE,
        severity=SeverityLevel.LOW,
        pattern=r"\b(quit\s+your\s+(9\s*to\s*5|day\s+job)|financial\s+freedom\s+in\s+[0-9]+\s*(days|weeks)|become\s+a\s+millionaire\s+(overnight|in\s+months)|passive\s+wealth\s+machine)\b",
        explanation=(
            "Sensational appeals to instant wealth, escaping employment, or effortless passive fortunes are "
            "emotional manipulation strategies designed to bypass critical thinking."
        ),
    ),
]


class TextAnalyzer:
    """Performs linguistic, rule-based, and evidence-span analysis on promotional text."""

    def __init__(self, rules: List[TextRule] = None):
        self.rules = rules or TEXT_RULES

    def analyze(self, text: str) -> Tuple[List[FindingItem], Dict[str, Any]]:
        """
        Analyze submitted text against defined risk rules.
        Returns:
            Tuple of (findings_list, text_metadata_dict)
        """
        if not text:
            return [], {
                "length": 0,
                "word_count": 0,
                "is_sufficient": False,
                "reason": "No text provided",
            }

        cleaned_text = text.strip()
        words = re.findall(r"\b\w+\b", cleaned_text)
        word_count = len(words)
        char_length = len(cleaned_text)

        findings: List[FindingItem] = []
        matched_rule_ids = set()

        for rule in self.rules:
            for match in rule.pattern.finditer(cleaned_text):
                # Avoid duplicate findings of the exact same rule on identical text spans
                evidence_text = match.group(0).strip()
                match_key = f"{rule.rule_id}:{match.start()}:{match.end()}"
                if match_key in matched_rule_ids:
                    continue
                matched_rule_ids.add(match_key)

                # Contextual excerpt around match
                start_char = match.start()
                end_char = match.end()

                finding = FindingItem(
                    id=rule.rule_id,
                    title=rule.title,
                    category=rule.category,
                    severity=rule.severity,
                    explanation=rule.explanation,
                    evidence=evidence_text,
                    start_offset=start_char,
                    end_offset=end_char,
                    source="text_analysis",
                )
                findings.append(finding)

        # Check sufficiency: if text is very short (< 10 words) and no triggers were found
        is_sufficient = word_count >= 10 or len(findings) > 0

        metadata = {
            "length": char_length,
            "word_count": word_count,
            "is_sufficient": is_sufficient,
            "findings_count": len(findings),
        }

        return findings, metadata
