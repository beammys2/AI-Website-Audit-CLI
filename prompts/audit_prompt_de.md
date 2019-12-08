# Website-Audit-Aufgabe

Du auditierst eine öffentliche Website auf Basis strukturierter Daten aus `ai-website-audit-cli`.

Der Report muss praktisch, evidenzbasiert und umsetzungsorientiert sein. Erfinde keine Analytics-Daten, Umsätze, Traffic-Zahlen, Core-Web-Vitals, Ranking-Daten, Wettbewerberdaten oder geschäftliche Aussagen, die nicht im JSON stehen.

## Pflichtstruktur des Reports

1. **Executive Summary**
   - 5-8 Bullet Points.
   - Nenne die wichtigsten bestätigten Probleme und die größten Chancen.

2. **Priorisierte Roadmap**
   - Tabelle mit: Priorität, Bereich, Befund, Warum relevant, Empfohlene Maßnahme, Aufwand.
   - Verwende P0/P1/P2/P3.

3. **SEO-Audit**
   - Title, Meta Description, Canonical, Robots, HTML-Lang, Headings, Schema, Social Preview, interne Links.
   - Nutze konkrete Evidenz aus den extrahierten Daten.

4. **Content- und Messaging-Audit**
   - Erkläre, was die Seite aktuell kommuniziert.
   - Identifiziere unklare Positionierung, fehlendes Vertrauen, fehlende Beweise, schwache CTAs, schwachen Above-the-Fold-Bereich oder dünne Texte.
   - Gib konkrete bessere Copy-Beispiele nur, wenn genug Kontext vorhanden ist.

5. **UX- und Conversion-Audit**
   - CTAs, Formulare, Navigation, Kontaktwege, Pricing-Signale, Trust-Signale, mobile Hinweise, Entscheidungsreibung.

6. **Accessibility-Audit**
   - Fehlende Alt-Texte, Heading-Struktur, Sprachangabe, Formulare/Buttons, Tastatur-/Lesbarkeitsrisiken.
   - Markiere klar, was manuell geprüft werden muss.

7. **Performance- und Technik-Audit**
   - Nutze nur extrahierte Fakten wie HTML-Größe, Ladezeit, Lazy Loading, Bilddimensionen, Text-zu-HTML-Ratio, Technologie-Hinweise.
   - Behaupte keine echten Core-Web-Vitals.

8. **Developer Implementation Checklist**
   - 10-20 konkrete Tasks, gruppiert nach Quick Wins, mittleren Aufgaben und manueller Prüfung.

9. **Offene Punkte für manuelle Prüfung**
   - Alles nennen, was die Extraction nicht sicher prüfen kann.

## Tonalität

Direkt, präzise und nützlich. Kein generischer Fülltext.

## Audit-Kontext JSON

```json
{{AUDIT_CONTEXT_JSON}}
```
