import asyncio
from pydantic import BaseModel, Field
from app.core.config import get_settings
from app.integrations.llm import llm_provider
from app.integrations.courtlistener import CourtListenerClient
from app.workflow.pipeline import BriefingPipeline
from app.schemas.brief import CaseBrief


class EvalScorecard(BaseModel):
    """Evaluation scorecard produced by the LLM Judge."""
    factual_accuracy_score: int = Field(description="Score 1-5 on whether the brief accurately represents facts.")
    holding_correctness_score: int = Field(description="Score 1-5 on whether the holding accurately reflects the legal ruling.")
    citation_relevance_score: int = Field(description="Score 1-5 on citation quality, validity, and relevance.")
    critique: str = Field(description="Brief explanation justifying the scores.")


BENCHMARKS = [
    {
        "query": "Marbury v. Madison judicial review Supreme Court authority",
        "expected_holding": "The Supreme Court has the authority to declare acts of Congress and executive actions unconstitutional, establishing the doctrine of judicial review.",
        "expected_case_name": "Marbury v. Madison"
    },
    {
        "query": "Brown v. Board of Education equal protection segregation public schools",
        "expected_holding": "Separate educational facilities are inherently unequal, violating the Equal Protection Clause of the Fourteenth Amendment.",
        "expected_case_name": "Brown v. Board of Education"
    },
    {
        "query": "Miranda v. Arizona self incrimination right to counsel",
        "expected_holding": "Prior to custodial interrogation, suspects must be informed of their constitutional right to remain silent and right to consult with an attorney.",
        "expected_case_name": "Miranda v. Arizona"
    },
    {
        "query": "Roe v. Wade abortion constitutional privacy right",
        "expected_holding": "The Constitution of the United States protected the liberty of a pregnant woman to choose to have an abortion under the Due Process Clause of the Fourteenth Amendment.",
        "expected_case_name": "Roe v. Wade"
    },
    {
        "query": "Palsgraf v. Long Island Railroad proximate cause negligence torts",
        "expected_holding": "A defendant is only liable for negligence to a plaintiff if the plaintiff was within the foreseeable zone of danger created by the defendant's negligent conduct.",
        "expected_case_name": "Palsgraf v. Long Island R.R. Co."
    }
]


async def evaluate_brief(
    benchmark: dict,
    generated_brief: CaseBrief,
    judge_llm
) -> EvalScorecard:
    """Evaluates a generated case brief against ground truth criteria using an LLM Judge."""
    judge_prompt = f"""You are an expert legal evaluation judge assessing the quality of an AI-generated legal brief.

GROUND TRUTH REFERENCE:
- Query: {benchmark['query']}
- Expected Case Name: {benchmark['expected_case_name']}
- Expected Holding: {benchmark['expected_holding']}

GENERATED BRIEF TO EVALUATE:
- Case Name: {generated_brief.case_name}
- Holding: {generated_brief.holding}
- Reasoning: {generated_brief.reasoning}
- Citations: {generated_brief.citation}
- Citation Details (URLs): {[item.model_dump() for item in generated_brief.citation_details]}

EVALUATION RUBRIC (Score each 1 to 5):
1. Factual Accuracy: Are the case facts, holdings, and doctrines accurate? (1=Completely fabricated/hallucinated, 5=Fully accurate)
2. Holding Correctness: Does the holding correctly reflect the core legal determination? (1=Wrong rule of law, 5=Exact legal doctrine captured)
3. Citation Relevance: Are the citations relevant, real, and supported by valid URLs? (1=No citations or fabricated, 5=Precise and authoritative with verified docket links)

Evaluate the brief and return the structured EvalScorecard."""

    return await judge_llm.complete_with_json_schema(
        prompt=judge_prompt,
        schema=EvalScorecard
    )


async def run_evaluation_suite() -> list[dict]:
    """Runs the briefing pipeline over all 5 landmark benchmark cases and computes precision and accuracy metrics."""
    settings = get_settings()
    llm = llm_provider(settings)
    court = CourtListenerClient()
    pipeline = BriefingPipeline(llm_client=llm, court_client=court)

    results = []

    print("=" * 70)
    print("STARTING LANDMARK CASES LLM-AS-A-JUDGE EVALUATION SUITE (5 CASES)")
    print("=" * 70)

    for i, benchmark in enumerate(BENCHMARKS, start=1):
        print(f"\n[Test {i}/{len(BENCHMARKS)}] Query: {benchmark['query']}")
        print("  -> Generating case brief via pipeline...")
        try:
            generated_brief = await pipeline.execute(benchmark["query"])
            print(f"  -> Generated brief for: {generated_brief.case_name}")

            print("  -> Running LLM Judge evaluation...")
            scorecard = await evaluate_brief(benchmark, generated_brief, llm)

            print(f"  [Scores] Factual Accuracy: {scorecard.factual_accuracy_score}/5 | Holding: {scorecard.holding_correctness_score}/5 | Citations: {scorecard.citation_relevance_score}/5")
            print(f"  [Critique] {scorecard.critique}")

            results.append({
                "query": benchmark["query"],
                "brief": generated_brief,
                "scorecard": scorecard,
                "success": True
            })
        except Exception as e:
            print(f"  ❌ Error executing pipeline for {benchmark['expected_case_name']}: {e}")
            results.append({
                "query": benchmark["query"],
                "brief": None,
                "scorecard": None,
                "success": False,
                "error": str(e)
            })

        # Pause briefly between benchmark cases to respect CourtListener burst rate limits
        await asyncio.sleep(2.0)

    valid_results = [r for r in results if r["success"]]
    if not valid_results:
        print("\n❌ All evaluation runs failed.")
        return results

    # Compute quantitative metrics
    avg_accuracy = sum(r["scorecard"].factual_accuracy_score for r in valid_results) / len(valid_results)
    avg_holding = sum(r["scorecard"].holding_correctness_score for r in valid_results) / len(valid_results)
    avg_citation = sum(r["scorecard"].citation_relevance_score for r in valid_results) / len(valid_results)

    # Citation Precision & URL Resolution Rate
    total_citations = sum(len(r["brief"].citation) for r in valid_results)
    resolved_urls = sum(sum(1 for item in r["brief"].citation_details if item.url) for r in valid_results)
    citation_resolution_rate = (resolved_urls / total_citations * 100) if total_citations > 0 else 0.0

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY (LANDMARK BENCHMARKS)")
    print(f"Total Benchmarks Run:        {len(BENCHMARKS)}")
    print(f"Successful Executions:       {len(valid_results)} / {len(BENCHMARKS)}")
    print(f"Average Factual Accuracy:    {avg_accuracy:.2f} / 5.0")
    print(f"Average Holding Correctness: {avg_holding:.2f} / 5.0 (Holding Accuracy: {(avg_holding/5.0)*100:.1f}%)")
    print(f"Average Citation Relevance:  {avg_citation:.2f} / 5.0")
    print(f"Citation URL Resolution Rate:{citation_resolution_rate:.1f}% ({resolved_urls}/{total_citations} resolved)")
    print("=" * 70)

    return results


if __name__ == "__main__":
    asyncio.run(run_evaluation_suite())
