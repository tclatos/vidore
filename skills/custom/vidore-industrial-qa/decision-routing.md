# Decision-Model Routing Context (USAF Technical Orders)

This excerpt carries the **navigation** knowledge of the `vidore-industrial-qa` skill. It is
injected verbatim into the decision model's shared state so the model can score
which documents and sections are relevant across the corpus. It contains routing
knowledge only — procedural details and calculations stay on the synthesis side.

## Technical Order Series & Manual Routing

The corpus comprises USAF Technical Orders (TOs), maintenance checklists, and servicing
manuals. Candidate documents and sections map to the following series:

- **TO 00-25-172 & Checklists (`TO_00-25-172CL-1` through `CL-5`, `AFD-091005-056`, `AFD-091005-062`)**:
  - **Core Domain**: Aircraft ground servicing, concurrent servicing (refueling while cargo on/offloading),
    Fuel Servicing Safety Zones (FSSZ), emergency shutdown, defueling, oxygen/flammable restrictions.
  - **CL-1 (`TO_00-25-172CL-1`)**: Ground servicing checklist — general USAF aircraft, bombers, fighters, trainers.
  - **CL-2 (`AFD-091005-056`, `AFD-091005-062`)**: Commercial contract cargo aircraft (LOGAIR and QUICKTRANS:
    C-130, L-188, DC-9, B-727).
  - **CL-3 (`TO_00-25-172CL-3`)**: Strategic transport and tanker aircraft (C-17, C-5, KC-135, KC-10).
  - **CL-4 (`TO_00-25-172CL-4`)**: Reconnaissance, patrol, surveillance, and VIP transport airframes.
  - **CL-5 (`TO_00-25-172CL-5`)**: Unmanned / Remotely Piloted Aircraft (RPA), tiltrotor (CV-22), and specialized platforms.
  - **Key Roles**: CSS (Concurrent Servicing Supervisor), REO (Refueling Equipment Operator),
    LVM (Liquid/Vent Monitor), SCR (Servicing Control Representative), CFR (Crash/Fire/Rescue).
  - **Key Equipment & Zones**: Ground Power Units (GPU), fuel servicing vehicles/trucks, Auxiliary Power
    Units (APU), Materials Handling Equipment (MHE, K-loaders, forklifts), 50-ft FSSZ perimeter.

- **Quality & TO System Administration (`TO_00-25-245_1`, `TO_00-25-260`)**:
  - **TO 00-25-245_1**: Technical Order quality program, deficiency reporting (AFTO Form 22), recommended
    changes, evaluation and routing of technical manual errors.
  - **TO 00-25-260**: Air Force Technical Order system procedures, distribution statements, security
    classification markings, index management, publication formatting, handling restrictions.

- **Ground & Specialized Maintenance Equipment (`TO_00-25-203`)**:
  - Inspection, maintenance, calibration, and safety procedures for aerospace ground equipment (AGE)
    and test equipment.

- **Industrial & Machine Shop Machinery (`TO_34-1-3`)**:
  - Industrial manufacturing processes, metalworking, machine shop operations, cutting tools, lathes,
    milling machines, and shop safety procedures.

## Routing Guidelines

1. **Specific Aircraft Mentioned**:
   - Commercial cargo contract (LOGAIR / QUICKTRANS / C-130 / L-188): target `AFD-091005-056` / `CL-2`.
   - General airframes / fighters / bombers: target `TO_00-25-172CL-1`.
   - Tankers / heavy transports (KC-135, C-17, C-5): target `TO_00-25-172CL-3`.
   - Patrol / reconnaissance / specialized: target `TO_00-25-172CL-4` or `CL-5`.
2. **Deficiency Reporting / Quality / Changes**:
   - AFTO Form 22, manual revisions, error reporting: target `TO_00-25-245_1`.
   - Distribution statements (A, B, C, D, F), publication standards: target `TO_00-25-260`.
3. **Machine Shop / Industrial Tools**:
   - Lathes, drills, metal fabrication, grinding, cutting fluids: target `TO_34-1-3`.
4. **General Servicing / Fuel Safety Zones**:
   - Concurrent servicing, refueling safety distances, GPU stand-off, emergency fire procedures:
     check the relevant `TO 00-25-172` checklist family.
