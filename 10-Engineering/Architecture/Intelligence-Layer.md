---
document: HDC-OS Intelligence Layer
version: 0.1
status: Review
owner: Project Owner
reviewed_by: null
last_review: null
work_order: WO-0047
last_updated: "2026-08-07"
---

# HDC-OS Intelligence Layer v0.1

## Zweck und Grenze

Es existiert genau eine fachneutrale Intelligence Layer unter
`shared/intelligence_layer`. Sie ist die zentrale Wissens- und Entscheidungsschicht
zwischen fachlichem Adapter und lokalem Modellprovider. Version 0.1 wird nur vom
Procurement Agent verwendet; Connectivity, Operations, Monitoring, Security,
Deployment und Backup sind ausschließlich vorgesehene spätere Adapterdomänen.

Die Schicht trainiert kein Modell, verändert keine Gewichte, verwendet keine
Embeddings oder Vektordatenbank und kommuniziert weder mit Cloudprovidern noch
mit anderen Agenten. Lernen bedeutet in v0.1 ausschließlich Retrieval sowie die
erneute Berücksichtigung von Decision Memory und Feedback Memory.

## Komponenten

| Komponente | Verantwortung |
|---|---|
| `IntelligenceLayer` | Einziger Orchestrator für Retrieval, Context, Prompt, Provider, Validation, Fallback und Metrics |
| `IntelligenceProvider` | Austauschbarer Vertrag `generate(prompt, schema)` |
| `RepositoryKnowledgeRetriever` | Ausschließlich erlaubte Quellen und relevante Zeilenauszüge laden |
| `ContextBuilder` | Rohauftrag, relevante Wissenselemente und relevante Entscheidungen deterministisch zusammensetzen |
| `PromptBuilder` | Nur Rolle, Analyseauftrag, Kontext- und Schema-Integration |
| `DecisionMemory` | Empfehlung, Owner-Entscheidung, Begründung, Zeitpunkt und Procurement Case speichern |
| `FeedbackMemory` | Genau einen der Werte `ACCEPT`, `REJECT`, `DEFER` je erfasster Owner-Entscheidung speichern |
| `IntelligenceMetrics` | KI-Aufrufe, Erfolge, Schemafehler, Fallback-Quote, mittlere Antwortzeit und letzten Erfolg dauerhaft führen |

## Provider-Abstraktion

Der Kern kennt nur `IntelligenceProvider` und importiert keinen konkreten Provider.
Die Adapter liegen getrennt unter `shared/intelligence_providers`. Vorgesehen sind `OLLAMA`, `LLAMACPP`,
`LOCAL_MODEL` und `DETERMINISTIC`. Konkrete lokale HTTP-Adapter liegen hinter
diesem Vertrag und akzeptieren ausschließlich numerische Loopback-Adressen über
HTTP. Die zentrale Konfiguration liegt in
`10-Engineering/config/intelligence.yaml`; ein Providerwechsel erfordert keine
Änderung an Procurement, Agent Runtime, Dashboard oder Scheduler. Cloudendpunkte
sind technisch ausgeschlossen.

## Erlaubte Retrieval-Quellen

Die v0.1-Allowlist ist geschlossen: Accepted Architecture, Procurement Cases,
Procurement Reports, Procurement History, Asset Status, Governance Rules,
Current Sprint, Current Bottleneck und Current Deployment State. Der Retriever
läuft nicht über den Repository-Baum, sondern nur über feste Pfade. Aus Dateien
werden nur zu Case-IDs und Analysebegriffen passende Auszüge übernommen. Damit
kann das vollständige Repository niemals ungefiltert in einen Modellprompt
gelangen.

## Ablauf und Validierung

```text
Procurement-Rohkontext → allow-listed Retrieval → Context Builder → Prompt Builder
→ lokaler Provider → bestehende JSON-Schema-Validierung → Procurement-Bericht
```

Eine ungültige Modellantwort wird nie weiterverarbeitet. Der bestehende
`DeterministicFallbackAnalysisProvider` bleibt im Procurement-Adapter
unverändert erhalten und wird ausschließlich nach Provider- oder
Validierungsfehlern aufgerufen. Empfehlungen bleiben beratend; Entscheidung und
Freigabe liegen beim Project Owner.

## Explainability und Health

Jeder Bericht enthält die verwendeten Wissensquellen, die berücksichtigten
Entscheidungen und die Begründung je Empfehlung. Der einzige Intelligence-Health-
Zustand ist `HEALTHY`, `WARNING` oder `DEGRADED`. Das Cockpit erhält einen
fachneutralen `intelligence`-Contract mit Health, aktivem Provider, Modell,
Fallback-Quote und Zeitpunkt der letzten erfolgreichen KI-Antwort.
