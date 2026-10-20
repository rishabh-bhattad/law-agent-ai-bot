from app.workflow.context import WorkflowStep, WorkflowContext
from app.integrations.llm import LLMProvider
from app.prompts import build_schema_prompt
from app.schemas.brief import SingleFieldRepair, AuditRepairResult, RepairBriefRequest
from app.core.config import get_settings

class ActorCriticRepairStep(WorkflowStep):
    """Orchestrates the Drafter-Auditor negotiation loop with at most one audit."""
    name = "Multi-agent Repair and Audit"

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def execute(self, context: WorkflowContext) -> None:
        repair_request: RepairBriefRequest = context.request
        brief = repair_request.current_brief
        field = repair_request.target_field
        instruction = repair_request.instruction
        current_text = getattr(brief, field)

        repair_prompt = build_schema_prompt(
            template_name='repair_field.md',
            schema=SingleFieldRepair,
            case_name=brief.case_name,
            target_field=field,
            instruction=instruction,
            current_value=current_text,
            critique_context=""
        )

        proposed_draft = await self.llm.complete_with_json_schema(
            prompt=repair_prompt,
            schema=SingleFieldRepair,
            model=get_settings().LLM_MODEL_FAST,
            on_token_usage=context.budget.record_tokens
        )

        audit_prompt = build_schema_prompt(
            template_name='audit_repair.md',
            schema=AuditRepairResult,
            case_name=brief.case_name,
            target_field=field,
            instruction=instruction,
            original_content=current_text,
            proposed_draft=proposed_draft.repaired_text
        )

        audit_result = await self.llm.complete_with_json_schema(
            prompt=audit_prompt,
            schema=AuditRepairResult,
            model=get_settings().LLM_MODEL_REASONING,
            on_token_usage=context.budget.record_tokens
        )

        if audit_result.approved:
            context.scratch['repaired_text'] = proposed_draft.repaired_text
            context.scratch['critique'] = audit_result.critique
        else:
            repair_prompt = build_schema_prompt(
                template_name='repair_field.md',
                schema=SingleFieldRepair,
                case_name=brief.case_name,
                target_field=field,
                instruction=instruction,
                current_value=current_text,
                critique_context=f"\n\n### Auditor's Critique from Previous Draft (Must be corrected):\n{audit_result.critique}"
            )
            final_draft = await self.llm.complete_with_json_schema(
                prompt=repair_prompt,
                schema=SingleFieldRepair,
                model=get_settings().LLM_MODEL_FAST,
                on_token_usage=context.budget.record_tokens
            )
            context.scratch['repaired_text'] = final_draft.repaired_text
            context.scratch['critique'] = audit_result.critique



        