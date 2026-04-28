# Paper 3 — Lessons Learned

Cumulative log of analytical insights, mistakes avoided, and process notes from our discussions.

---

## Session 1 — 2026-04-09: Project Setup and Literature Mapping

### Process
- Claude Code cannot read .docx files natively (binary format). User pasted outline text directly — fastest workaround.
- Shell commands (python3, powershell, cmd) returned empty output consistently — likely sandbox restriction on this Windows/OneDrive environment. Do not rely on shell execution for file conversion tasks.

### Analytical
- The paper's novelty is at the *intersection* of literatures, not within any single one. The employment-multiplier literature and the DMDU/scenario discovery literature have not been connected before. Positioning must make this explicit.
- The I-O vs. CGE debate is not just methodological — it determines what question you're answering. The RDM framing reframes the I-O limitations as features (parameters to explore, not errors to defend). This is a strong rhetorical move but needs to be stated explicitly in Section 2 or 3.
- The country set (Mexico, Belize, Uganda, Egypt, Morocco, Libya, Bulgaria) needs a structured justification — not just "CCDR engagements" but a demonstration that they span the heterogeneity dimensions the framework needs to stress-test.

### Literature
- Four main literature strands identified: (A) green employment multipliers, (B) cost dynamics of decarbonization, (C) DMDU/scenario discovery, (D) climate policy in developing countries.
- The gap lives between strands A and C: employment literature produces point estimates; nobody uses exploratory methods to map conditions under which those estimates hold.
- Key anchoring papers: Garrett-Peltier (2017), Way et al. (2022), Lempert et al. (2003), Marchau et al. (2019).

---

## Session 2 — 2026-04-10: Clarifying the Research Question

### Analytical
- **Critical framing clarification:** The paper is Version A (conditions for substantial job creation from climate investment), NOT Version B (winners/losers from net-zero transition). Version B would require modeling the contraction of fossil/carbon-intensive sectors — displacement and opportunity costs — which the current I-O pipeline doesn't do. It only models the incremental employment from demand shocks.
- The "positive vs. negative" language in the outline is misleading. In an I-O framework, any expenditure injected produces positive output and employment mechanically (Leontief multiplier is always positive). The real variation is in *magnitude* — high vs. low job creation — and in *sectoral concentration*. Scenario discovery should classify above/below a policy-relevant threshold, not positive vs. negative.
- Sectoral decomposition (which sectors benefit more/less) is compatible with Version A. It shows where jobs concentrate under different cost-structure assumptions. But it does NOT identify "losers" in the transition sense — that requires a different model.
- If the paper ever claims to identify transition losers, reviewers will correctly point out that the framework can't do that. Scope the claims precisely.

### Process
- Answering the five clarifying questions *before* deep-diving into literature was the right sequencing. It revealed that the counterfactual and framing needed sharpening — which would have gone unnoticed if we'd jumped straight to reading papers.

---

## Session 3 — 2026-04-11: Citation Verification and Reading Schedule

### Process — Citation Hallucination Risk
- **The sub-agent misattributed Bucker et al. (2025) as "Mayfield, Henner, Engel-Cox & Egan (2025)."** The paper is actually Bucker, del Rio-Chanona, Pichler, Ives & Farmer (2025) in Joule. This is a fabricated citation from the PDF extraction agent.
- **Lesson: Never trust agent-extracted citations without verification.** The reading list now includes a confidence audit. Papers fall into four tiers: CONFIRMED (user verified), HIGH CONFIDENCE (well-established papers from training data), MEDIUM CONFIDENCE (likely correct, verify details), LOWER CONFIDENCE (from web search, must verify on Google Scholar before citing).
- **Rule going forward:** Do not cite any paper in the dissertation without confirming it exists via Google Scholar or publisher website. This applies especially to all web-search-sourced papers and agent-extracted citations.

### Analytical — Key Research Group Identified
- Mealy, Bucker, Senra de Moura, Knudsen (+ del Rio-Chanona, Farmer) form a single World Bank / Oxford research cluster. They authored "Five Frictions" (WP 11224), "Beyond Green Jobs" (WP 11262), the Joule power sector paper, and the occupational skill space paper.
- This group has laid out the conceptual agenda that Paper 3 operationalizes empirically. The positioning is: they argue someone should do conditional analysis with scenario discovery; you actually do it across seven countries.
- They are NOT coauthors on Paper 3. This makes the positioning cleaner — independent implementation of their research agenda. But reviewers from this group may be assigned, so the contribution beyond their conceptual work must be crystal clear.

---

## Session 4 — 2026-04-13: Citation Verification of Tier Plan

### Process — More Fabricated Citations Found
- **Two more misattributed citations caught.** Both papers #3 and #6, attributed to "Semieniuk et al. (2024)" by the PDF extraction agent, are actually by different authors:
  - #3 is actually **Hanna, Heptonstall & Gross (2024)** "Job creation in a low carbon transition to renewables and energy efficiency: a review of international evidence" — *Sustainability Science*
  - #6 is actually **Ravillard, Chueca, Weiss & Hallack (2021)** "Implications of the Energy Transition on Employment: Today's Results, Tomorrow's Needs" — IDB report (not even 2024, and not peer-reviewed)
- This is the same pattern as the Session 3 Bucker et al. misattribution. The agent extracted titles from PDFs correctly but fabricated/confused the authors.
- **Lesson reinforced:** Agent-extracted citations from PDFs are unreliable for author attribution. Always verify authors independently. Three out of three agent-extracted Readings folder citations checked so far have had wrong authors. Papers #35, #40, #62 (also from Readings folder) are HIGH RISK and must be verified before citing.

### Analytical — Impact on Reading Plan
- #3 (Hanna et al.) is still a valuable Tier 1 review paper — the content didn't change, just the attribution. It stays as a full read.
- #6 (Ravillard et al.) is demoted from Tier 2 careful read to a quick skim. It's an IDB policy report, not a peer-reviewed paper explicitly calling for our research agenda. The gap-framing quotes we expected to find there likely don't exist in the form assumed. This role needs to be filled by other papers (Mealy et al. #12 and Knudsen et al. #15 already do this).

### Additional Corrections
- #4 Cerny et al. year corrected from 2021 to 2022 (SSRN deposit date)
- #9 Montt et al. subtitle corrected: "2-degree goal" not "Paris Agreement"
- #28 IRENA corrected: co-published with ILO; full title includes "2023"

---

*Add new entries below as sessions continue.*
