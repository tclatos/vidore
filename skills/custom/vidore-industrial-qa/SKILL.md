---
name: vidore-industrial-qa
description: Domain knowledge and navigation guidelines for ViDoRe v3 Industrial technical orders, USAF maintenance checklists, safety zones, and aircraft fueling procedures.
tags: [vidore, industrial, usaf, technical-order, checklist, safety-zone, aircraft]
version: "1.0"
category: domain
---

# ViDoRe v3 Industrial QA Skill

This skill guides agents answering technical questions across military technical orders (TO) and checklists in the **ViDoRe v3 Industrial** benchmark (specifically USAF Technical Orders, e.g. `TO 00-25-172`, `TO 00-25-172CL-2`, `AFD-091005-056`).

---

## Technical Order Conventions & Layout

1. **Title & Front Matter**:
   - `TO 00-25-172CL-2`: Technical Manual Checklist for Concurrent Servicing of Commercial Contract Cargo Aircraft (LOGAIR and QUICKTRANS).
   - "LIST OF EFFECTIVE PAGES": Records dates of issue, change numbers, and revision indicators.
   - **Revision Indicators**:
     - Outer margin vertical line (`|`) indicates text changes.
     - Shaded or screened areas indicate changes to illustrations.
     - Miniature pointing hands indicate visual updates to diagrams.

2. **Key Operational Personnel**:
   - **CSS**: Concurrent Servicing Supervisor (responsible for overall concurrent operations, safety, acts as RVM).
   - **REO**: Refueling Equipment Operator (operates refueling vehicle/pumps, monitors pressure and emergency shutdown).
   - **LVM**: Liquid/Vent Monitor or Line Valve Monitor.
   - **SCR**: Servicing Control Representative.
   - **CFR / Fire Department**: Crash/Fire/Rescue personnel (notified at least 15 minutes before concurrent servicing).

3. **Ground Equipment & Safety Zones**:
   - **GPU (Ground Power Unit)**: Minimum separation distance of **50 feet** from fuel servicing points/equipment; placed upwind of the fuel servicing operations whenever feasible.
   - **Safety Zones / Clearances**:
     - Regulated by aircraft type, MHE (Materials Handling Equipment), heaters, oxygen carts, and open flame hazards.
     - Spark-producing equipment must be positioned outside designated safety perimeters.

4. **Emergency Shutdown & Fire Procedures**:
   - Immediate cessation of fuel servicing upon fuel spills, leaks, or fire alarms.
   - Emergency evacuation initiation by CSS.
   - Notification and handover to Crash/Fire/Rescue (CFR) personnel.

---

## Navigation & Answering Rules

- **TOC First**: Identify the target manual and chapter (e.g. general safety, concurrent servicing checklists, emergency procedures) via `get_document_toc`.
- **Exact Terminology**: Quote technical roles (CSS, REO, LVM), distances (50 ft), and equipment designations verbatim.
- **Visuals**: For diagrams illustrating equipment placement or revision symbols, use `query_image` to confirm layout specifics.
- **Direct Answers**: State the primary technical conclusion or rule first, followed by supporting checklist references and citations (`[hash::seq]`).
