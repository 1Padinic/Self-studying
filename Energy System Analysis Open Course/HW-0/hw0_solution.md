# HW 0 — IRA Emission Reduction Assessment

## Part 1: Comparing the three U.S. IRA analyses

### 1. What models do the groups use?

| Group | Model | Type |
|---|---|---|
| REPEAT (Princeton ZERO Lab + Evolved Energy Research) | EnergyPATHWAYS + RIO | Bottom-up: demand-side stock-rollover accounting (EnergyPATHWAYS) feeding a least-cost supply-side capacity-expansion optimization (RIO), with high spatial/temporal resolution and geospatial siting analysis |
| Rhodium Group | RHG-NEMS | Modified version of EIA's National Energy Modeling System — an integrated, full-economy energy-market simulation with macroeconomic feedbacks |
| Energy Innovation | Energy Policy Simulator (EPS) | Open-source system-dynamics simulation (built in Vensim) covering all sectors and all GHGs |

### 2. Key assumptions behind the estimates

- **Common to all:** future fossil-fuel prices, technology cost declines, economic growth, and — critically — how strongly households and firms respond to *voluntary* tax credits (the IRA is subsidies, not mandates; the credits are uncapped, so total impact scales with uptake).
- **REPEAT:** near-perfect, cost-minimizing deployment; transmission construction roughly **doubles** by 2030 to enable the renewables build-out. Central-case, single-scenario framing.
- **Rhodium:** three scenarios (high/central/low) varying fuel prices, growth, and technology costs — hence the wide 31–44% band. Includes non-CO₂ gases and the land carbon sink.
- **Energy Innovation:** business-as-usual calibrated to EIA AEO **Low Economic Growth** case for demand and fuel prices; policy uptake rates set exogenously.

### 3. Pros and cons

| | Pros | Cons |
|---|---|---|
| REPEAT | Highest technological/spatial detail; transparent academic documentation; captures grid constraints explicitly | Least-cost optimization assumes frictionless, rational deployment (optimistic); little uncertainty quantification (point estimate); optimistic transmission assumption |
| Rhodium | Full-economy coverage with macro feedbacks; explicit uncertainty range; NEMS pedigree well understood by policymakers | Proprietary (not reproducible); NEMS is complex and historically conservative on clean-tech adoption |
| Energy Innovation | Free, open source, reproducible; fast; also outputs jobs and health impacts | Coarser structure (no detailed dispatch/grid modeling); results hinge on exogenous BAU and uptake assumptions |

### 4. Uncertainties in the results

1. **Baseline uncertainty:** the "without IRA" counterfactual already spans 24–35% depending on gas prices and growth — it drives much of the headline range.
2. **Uptake uncertainty:** uncapped tax credits mean emissions (and fiscal cost) depend on consumer/investor behavior the models can't observe.
3. **Implementation frictions:** permitting, transmission siting, interconnection queues, supply chains, and litigation are largely outside the models — all bias real-world outcomes below modeled ones.
4. **Technology cost trajectories** (batteries, H₂, CCS) and **fuel price volatility**.

### 5. Interpretation

These are **conditional scenarios, not forecasts**. Three independent models with different architectures converge on ~37–44% below 2005 by 2030 with the IRA vs. ~24–27% without it — the *delta* (~10–15 pp of additional reduction) is the robust finding, more so than any absolute level. The IRA plausibly delivers the 40% goal only if implementation (especially transmission) keeps pace; even then a gap remains to the 50–52% U.S. NDC.

---

## Part 2: The same exercise for the Czech Republic

Three comparable Czech analyses (note: Czech/EU targets are benchmarked to **1990**, not 2005):

### 1. What models do the groups use?

| Group | Model | Type |
|---|---|---|
| **SEEPIA** (Charles University Environment Centre + CENIA + Technology Centre Prague; academic — the Czech analogue of REPEAT) | **TIMES-CZ** plus macroeconomic/CGE and microsimulation modules | Bottom-up least-cost energy-system optimization (national adaptation of the Pan-European TIMES model); SEEPIA scenarios serve as the template for Czechia's decarbonization strategy |
| **McKinsey** — *Carbon-neutral Czechia 2050* (consulting — the analogue of Rhodium) | Proprietary cost-curve / pathway model | Sector-by-sector abatement cost curves and least-cost pathway analysis |
| **Government NECP 2024 update** (Ministry of Industry and Trade / CHMI) | Sectoral WEM/WAM projection models (energy modeling supplied by contracted institutes) | Official "with existing measures" / "with additional measures" GHG projections; the WAM3 scenario is the plan's baseline |

### 2. Results and key assumptions

- **NECP (official):** ~**−57% by 2030 vs. 1990** in the WAM scenario, driven mainly by coal decline in power/heat. But in the EU **Effort Sharing** sectors (transport, buildings, agriculture) Czechia *misses* its −26% (vs. 2005) target by ~7–9 pp even with additional measures.
- **McKinsey:** current trajectory delivers only part of the way; reaching −55% by 2030 requires ~**CZK 500 bn (€18 bn, ~1% GDP/yr)** additional investment, +3.2 GW solar/wind by 2030, and sustained cuts of ~3.2 Mt/yr.
- **SEEPIA:** deep decarbonization is feasible at moderate cost; pathway dominated by coal phase-out, then electrification and industry.
- **Shared key assumptions:** EU ETS price trajectory (drives the economics of the coal phase-out — the single biggest lever); coal exit timing (official 2033 vs. market-driven earlier); new nuclear (Dukovany unit ~2036+); RES build-out limited by permitting and grid; availability of EU money (Modernisation Fund, RRF, cohesion funds).

### 3. Uncertainties

1. **Coal phase-out timing** — driven by ETS prices and heat-sector economics, not a fixed date; a few years' shift moves 2030 emissions by several Mt.
2. **Large discrete projects:** nuclear construction schedule/cost overruns; unlike the U.S., a handful of lumpy decisions dominate the outcome.
3. **ESR sectors:** transport and buildings persistently under-deliver in every model — the main compliance risk.
4. **Dependence on EU-level instruments** (ETS2, CBAM, Fit for 55 legislation) whose final form and prices are exogenous to national models.
5. **Structure of the economy:** high industrial energy intensity makes projections sensitive to growth and relocation assumptions.

### 4. Interpretation

The structural picture mirrors the U.S. case: an academic optimization model (SEEPIA/TIMES-CZ ↔ REPEAT), a consultancy study (McKinsey ↔ Rhodium), and simulation-based official projections (NECP ↔ EIA/NEMS heritage) all agree on the **direction**: Czechia reaches roughly −50 to −57% vs. 1990 by 2030, essentially because coal power collapses. The robust finding is again the *gap*, not the point estimate: power-sector decarbonization is on track, while **ESR sectors miss their targets in every scenario** — so additional transport/buildings policy, not more power-sector modeling precision, is the actionable conclusion. Key contrast with the IRA analyses: U.S. uncertainty centers on *voluntary subsidy uptake*; Czech uncertainty centers on *ETS prices and a few large lumpy projects* (coal closures, nuclear).

---

## Sources

- [REPEAT Project reports](https://repeatproject.org/reports) · [Evolved Energy: Impact of the IRA](https://www.evolved.energy/post/impact-of-the-inflation-reduction-act) · [EnergyPATHWAYS model description](https://decarbamerica.org/wp-content/uploads/2020/12/EnergyPATHWAYS-Model-Description.pdf)
- [Rhodium: A Turning Point for US Climate Progress](https://rhg.com/research/climate-clean-energy-inflation-reduction-act/) · [RHG-NEMS](https://rhg.com/energy-climate/data-and-tools/rhg-nems/)
- [Energy Innovation: Modeling the IRA with the EPS (PDF)](https://energyinnovation.org/wp-content/uploads/2022/08/Modeling-the-Inflation-Reduction-Act-with-the-US-Energy-Policy-Simulator_August.pdf) · [EPS documentation](https://docs.energypolicy.solutions/)
- [E&E News: Modeling IRA carbon cuts — caveats, uncertainty and luggage](https://www.eenews.net/articles/modeling-ira-carbon-cuts-caveats-uncertainty-and-luggage/)
- [SEEPIA project](https://seepia.cz/en/) · [CUEC: Pathways to deep decarbonisation](https://www.czp.cuni.cz/czp/index.php/en/component/content/article/8-centrum/aktuality/967-pathways-to-deep-decarbonisation)
- [McKinsey: Pathways to decarbonize the Czech Republic (PDF)](https://www.mckinsey.com/cz/~/media/McKinsey/Locations/Europe%20and%20Middle%20East/Czech%20Republic/Our%20work/Decarbonization_Report_EN_vFinal.pdf)
- [Czechia updated NECP 2021–2030](https://cdn.climatepolicyradar.org/navigator/CZE/2024/czechia-updated-final-national-energy-and-climate-plan-necp-2021-2030_72a94076f5cf55774cfb406ecde5cd5c.pdf) · [EC assessment of the Czech draft NECP (SWD(2023) 926)](https://commission.europa.eu/document/download/70364812-3095-4eda-9c6f-80c10fd40c0a_en?filename=SWD_Assessment_draft_updated_NECP_Czechia_2023.pdf)
- [Green Deal and Carbon Neutrality Assessment of Czechia (Energies, 2023)](https://doi.org/10.3390/en16052152) · [OECD: Towards net zero in the Czech Republic](https://www.oecd.org/content/dam/oecd/en/publications/reports/2023/05/towards-net-zero-in-the-czech-republic_503c0ca6/7ce7c9dd-en.pdf)
