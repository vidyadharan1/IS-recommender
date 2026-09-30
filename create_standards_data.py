import json
import os

STANDARDS = [
    # 1. CEMENT
    {
        "is_code": "IS 8112:2013",
        "title": "43 Grade Ordinary Portland Cement - Specification",
        "category": "Cement",
        "scope": "Covers requirements for 43 grade ordinary portland cement (OPC) used in general civil engineering and residential construction. Specifies physical properties including fineness (min 225 m2/kg), sound testing by Le-Chatelier method, setting time (initial min 30 min, final max 600 min), and minimum compressive strength of 23 MPa at 72 hours, 33 MPa at 168 hours, and 43 MPa at 672 hours (28 days).",
        "keywords": ["cement", "opc", "43 grade", "ordinary portland cement", "compressive strength", "residential construction", "rcc", "concrete", "mortar", "fineness", "setting time"]
    },
    {
        "is_code": "IS 12269:2013",
        "title": "53 Grade Ordinary Portland Cement - Specification",
        "category": "Cement",
        "scope": "Specifies chemical and physical requirements for 53 grade ordinary portland cement for high-strength concrete works, prestressed concrete, bridge girders, high-rise buildings, and industrial pavements. Mandates minimum 28-day compressive strength of 53 MPa (with max 58 MPa) and rapid strength gain characteristics.",
        "keywords": ["cement", "opc", "53 grade", "high strength cement", "prestressed concrete", "bridges", "flyovers", "compressive strength", "structural concrete"]
    },
    {
        "is_code": "IS 269:2015",
        "title": "Ordinary Portland Cement - Specification (33 Grade, 43 Grade, and 53 Grade)",
        "category": "Cement",
        "scope": "Comprehensive standard covering chemical and physical requirements of all grades of Ordinary Portland Cement (OPC 33, OPC 43, OPC 53). Specifies insoluble residue, magnesia content, loss on ignition, sulfur trioxide, lime saturation factor, compressive strength benchmarks, and packaging requirements.",
        "keywords": ["cement", "opc", "33 grade", "43 grade", "53 grade", "ordinary portland cement", "bis certification", "concrete mix", "plastering"]
    },
    {
        "is_code": "IS 1489 (Part 1):2015",
        "title": "Portland Pozzolana Cement - Specification (Part 1: Fly Ash Based)",
        "category": "Cement",
        "scope": "Specifies manufacture, chemical and physical requirements of fly ash based Portland Pozzolana Cement (PPC). Covers pozzolanic material percentage (15% to 35% fly ash conforming to IS 3812), low heat of hydration, sulfate attack resistance, durability in marine and coastal environments, and mass concreting.",
        "keywords": ["cement", "ppc", "portland pozzolana cement", "fly ash", "blended cement", "durability", "hydraulic structures", "marine concrete", "low heat"]
    },
    {
        "is_code": "IS 1489 (Part 2):2015",
        "title": "Portland Pozzolana Cement - Specification (Part 2: Calcined Clay Based)",
        "category": "Cement",
        "scope": "Covers requirements of calcined clay based Portland Pozzolana Cement. Mandates blending of Portland cement clinker with 10% to 25% calcined pozzolanic clay. Suitable for water-retaining structures, dams, foundations, and soil stabilization.",
        "keywords": ["cement", "ppc", "calcined clay", "pozzolanic", "hydraulic structures", "dams", "mass concrete"]
    },
    {
        "is_code": "IS 455:2015",
        "title": "Portland Slag Cement - Specification",
        "category": "Cement",
        "scope": "Covers manufacture and properties of Portland Slag Cement (PSC) produced by intimate intergrinding of Portland clinker, granulated blast furnace slag (25% to 70%), and gypsum. Offers high chemical resistance against chloride and sulfate attack, ideal for sewage treatment plants, underground piles, and coastal construction.",
        "keywords": ["cement", "psc", "portland slag cement", "slag", "blast furnace", "marine environment", "sewage treatment", "sulfate resistance"]
    },
    {
        "is_code": "IS 8041:1990",
        "title": "Rapid Hardening Portland Cement - Specification",
        "category": "Cement",
        "scope": "Specifies requirements for rapid hardening portland cement characterized by high early compressive strength development. Intended for urgent road repair, precast concrete manufacturing, slipform shuttering, and cold weather concreting.",
        "keywords": ["cement", "rapid hardening", "early strength", "road repair", "precast concrete", "cold weather"]
    },
    {
        "is_code": "IS 12330:1988",
        "title": "Sulphate Resisting Portland Cement - Specification",
        "category": "Cement",
        "scope": "Covers requirements for sulfate resisting Portland cement with tricalcium aluminate (C3A) content capped at 5.0%. Designed specifically for concrete exposed to aggressive sulfate ions in soils, marshes, tidal zones, and saline groundwater.",
        "keywords": ["cement", "sulfate resisting", "src", "c3a", "marine foundation", "saline soil", "marshy ground"]
    },
    {
        "is_code": "IS 3466:1988",
        "title": "Masonry Cement - Specification",
        "category": "Cement",
        "scope": "Specifies requirements for masonry cement utilized exclusively for brick, block, and stone masonry work and wall plastering. Provides high water retention, plasticity, workability, and reduced cracking tendencies.",
        "keywords": ["cement", "masonry", "brickwork", "plastering", "mortar", "workability", "block laying"]
    },
    {
        "is_code": "IS 6909:1990",
        "title": "Supersulphated Cement - Specification",
        "category": "Cement",
        "scope": "Covers supersulphated cement composed of granulated blast furnace slag, calcium sulphate, and Portland clinker. Highly resistant to chemical attacks by acids, sulfates, and industrial effluents in foundation slabs.",
        "keywords": ["cement", "supersulphated", "chemical resistance", "industrial effluent", "slag", "acid resistance"]
    },

    # 2. STEEL
    {
        "is_code": "IS 1786:2008",
        "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement - Specification",
        "category": "Steel",
        "scope": "Covers requirements of deformed steel bars (TMT) and cold worked deformed rebars in strength grades: Fe 415, Fe 415D, Fe 500, Fe 500D, Fe 550, Fe 550D, and Fe 600. Specifies chemical composition (C, S, P max limits), proof stress, ultimate tensile strength, TS/YS ratio, minimum elongation (16% for 500D), bend and rebend tests for earthquake-resistant RCC structures.",
        "keywords": ["steel", "tmt", "rebar", "fe 500d", "fe 415", "fe 550d", "reinforcement", "concrete reinforcement", "tensile strength", "yield stress", "ductility"]
    },
    {
        "is_code": "IS 2062:2011",
        "title": "Hot Rolled Medium and High Tensile Structural Steel - Specification",
        "category": "Steel",
        "scope": "Specifies hot rolled structural steel plates, sections (angles, tees, beams, channels, flats), and hollow sections for bridges, PEB sheds, transmission towers, and industrial buildings. Covers grades E250, E275, E300, E350, E410, and E450 in quality subgrades A, B, BR, B0, and C with Charpy V-notch impact toughness requirements.",
        "keywords": ["steel", "structural steel", "e250", "e350", "angles", "channels", "beams", "plates", "hot rolled", "welding", "peb", "bridges"]
    },
    {
        "is_code": "IS 432 (Part 1):1982",
        "title": "Mild Steel and Medium Tensile Steel Bars and Hard-Drawn Steel Wire for Concrete Reinforcement",
        "category": "Steel",
        "scope": "Covers plain round mild steel bars (Grade I and Grade II) and medium tensile steel bars for general RCC work, ties, stirrups, column dowels, and secondary reinforcement.",
        "keywords": ["steel", "mild steel", "round bars", "stirrups", "ties", "grade i", "concrete reinforcement", "dowels"]
    },
    {
        "is_code": "IS 2830:2012",
        "title": "Carbon Steel Cast Billet Ingots, Billets, Blooms and Slabs for Re-rolling into Steel for General Structural Purposes",
        "category": "Steel",
        "scope": "Covers chemical composition and quality parameters of continuously cast billets, blooms, and slabs intended for re-rolling into TMT bars, structural sections, and wire rods.",
        "keywords": ["steel", "billet", "ingot", "bloom", "slab", "re-rolling", "carbon steel", "smelting", "rolling mill"]
    },
    {
        "is_code": "IS 1367 (Part 3):2017",
        "title": "Technical Supply Conditions for Threaded Steel Fasteners - Mechanical Properties of Fasteners",
        "category": "Steel",
        "scope": "Covers mechanical properties, tensile strength, proof load, and hardness of carbon steel and alloy steel bolts, screws, and studs for property classes 4.6, 5.6, 8.8, 10.9, and 12.9 for structural jointing.",
        "keywords": ["steel", "fasteners", "bolts", "nuts", "screws", "studs", "grade 8.8", "grade 10.9", "tensile proof load", "structural joints"]
    },
    {
        "is_code": "IS 277:2018",
        "title": "Galvanized Steel Sheets (Plain and Corrugated) - Specification",
        "category": "Steel",
        "scope": "Specifies hot-dip zinc-coated (galvanized) plain and corrugated sheet steel (GI sheets) for roofing, side cladding, grain silos, air conditioning ducts, and rainwater gutters. Covers coating classes from 120 g/m2 up to 450 g/m2.",
        "keywords": ["steel", "gi sheets", "galvanized", "zinc coating", "corrugated roofing", "cladding", "silos", "ducts"]
    },
    {
        "is_code": "IS 1161:2014",
        "title": "Steel Tubes for Structural Purposes - Specification",
        "category": "Steel",
        "scope": "Covers hot finished and electric resistance welded (ERW) circular hollow steel tubes for structural uses, tubular roof trusses, scaffolding, transmission poles, and railings. Grades YSt 210, YSt 240, and YSt 310.",
        "keywords": ["steel", "hollow sections", "steel tubes", "scaffolding", "trusses", "erw pipes", "structural pipe"]
    },
    {
        "is_code": "IS 1079:2017",
        "title": "Low Carbon Steel Plates, Sheets and Strips for Cold Forming",
        "category": "Steel",
        "scope": "Specifies requirements of low carbon hot-rolled steel plates, sheets, and strips for press work, automotive frames, electrical stamping, cold forming, and general engineering fabrication.",
        "keywords": ["steel", "hot rolled sheets", "low carbon", "cold forming", "deep drawing", "fabrication"]
    },
    {
        "is_code": "IS 1239 (Part 1):2004",
        "title": "Steel Tubes, Tubulars and Other Wrought Steel Fittings - Specification (Part 1: Steel Tubes)",
        "category": "Steel",
        "scope": "Covers welded and seamless steel tubes (Black and Galvanized) for water, non-hazardous gas, air, and steam lines. Classes: Light (A-class / Yellow), Medium (B-class / Blue), and Heavy (C-class / Red).",
        "keywords": ["steel", "gi pipes", "ms pipes", "black pipes", "steam lines", "plumbing", "water pipes", "flanges"]
    },
    {
        "is_code": "IS 1875:1992",
        "title": "Carbon Steel Billets, Blooms, Slabs and Bars for Forgings - Specification",
        "category": "Steel",
        "scope": "Specifies requirements for carbon steel wrought products supplied for forging applications such as crankshafts, connecting rods, machine spindles, railway axles, and gears.",
        "keywords": ["steel", "forging", "carbon steel", "machinery", "axles", "shafts", "gears"]
    },

    # 3. ELECTRICAL
    {
        "is_code": "IS 694:2010",
        "title": "Polyvinyl Chloride Insulated Unshead and Sheathed Cables/Cords for Rated Voltages up to 1100 V",
        "category": "Electrical",
        "scope": "Covers single-core, twin, and multi-core PVC insulated electrical wires with copper and aluminum conductors for internal wiring of residential, commercial buildings, industrial panels, and appliances. Specifies flame retardant (FR) and low smoke (FRLS) characteristics.",
        "keywords": ["electrical", "cables", "wires", "copper wire", "pvc insulation", "frls", "1100v", "building wiring", "conductor", "domestic cables"]
    },
    {
        "is_code": "IS 1180 (Part 1):2014",
        "title": "Outdoor Type Oil Immersed Distribution Transformers up to and including 2500 kVA, 33 kV - Specification",
        "category": "Electrical",
        "scope": "Covers outdoor type, mineral oil-immersed, naturally cooled three-phase step-down distribution transformers (16 kVA to 2500 kVA, 11 kV and 33 kV primary voltage, 433 V secondary). Mandates BEE Star rating loss levels, temperature rise limits, impedance, and safety fittings.",
        "keywords": ["electrical", "transformer", "distribution transformer", "11kv", "433v", "oil immersed", "bee star rating", "power distribution", "substation"]
    },
    {
        "is_code": "IS/IEC 60898 (Part 1):2002",
        "title": "Electrical Accessories - Circuit-Breakers for Overcurrent Protection for Household and Similar Installations",
        "category": "Electrical",
        "scope": "Covers AC miniature circuit breakers (MCBs) intended for household and commercial distribution boards for operation at 50 Hz, rated voltage not exceeding 440 V, rated current up to 125 A, and short-circuit capacity up to 10 kA (B, C, D trip curves).",
        "keywords": ["electrical", "mcb", "miniature circuit breaker", "overcurrent", "short circuit", "distribution board", "switchgear", "tripping"]
    },
    {
        "is_code": "IS 3854:1997",
        "title": "Switches for Domestic and Similar Fixed Electrical Installations - Specification",
        "category": "Electrical",
        "scope": "Specifies manually operated general purpose switches (modular, piano, rocker, toggle) for AC circuits up to 250 V and rated current up to 16 A for household fixed installations. Covers electrical endurance, insulation resistance, and fire risk test.",
        "keywords": ["electrical", "switch", "modular switch", "piano switch", "socket", "lighting switch", "domestic wiring", "250v"]
    },
    {
        "is_code": "IS 1293:2019",
        "title": "Plugs and Socket-Outlets for Household and Similar Purposes of Rated Voltage up to 250 V",
        "category": "Electrical",
        "scope": "Covers two-pole and three-pole round-pin plugs and socket-outlets (6A and 16A) with safety shutters for connection of electrical appliances up to 250 V. Specifies child safety shutters, grounding contacts, and temperature rise.",
        "keywords": ["electrical", "plug", "socket", "outlet", "power point", "3-pin plug", "16a socket", "safety shutter"]
    },
    {
        "is_code": "IS 16102 (Part 1):2012",
        "title": "Self-Ballasted LED Lamps for General Lighting Services - Part 1: Safety Requirements",
        "category": "Electrical",
        "scope": "Specifies safety and interchangeability requirements for self-ballasted LED lamps (LED bulbs) for domestic and commercial general lighting services having rated wattage up to 60 W and voltage from 50 V to 250 V.",
        "keywords": ["electrical", "led lamp", "led bulb", "lighting", "illumination", "energy saving", "luminaire", "b22 cap", "e27 cap"]
    },
    {
        "is_code": "IS 3043:2018",
        "title": "Code of Practice for Earthing",
        "category": "Electrical",
        "scope": "Provides detailed engineering guidelines for design, installation, and testing of electrical grounding and earthing systems (pipe earthing, plate earthing, chemical rod earthing, substation earthing mats) for human safety and equipment protection.",
        "keywords": ["electrical", "earthing", "grounding", "earthing pit", "chemical earthing", "substation", "leakage protection", "gi earth electrode"]
    },
    {
        "is_code": "IS 7098 (Part 1):1988",
        "title": "Crosslinked Polyethylene Insulated Thermoplastic Sheathed Cables (Part 1: For Working Voltage up to 1.1 kV)",
        "category": "Electrical",
        "scope": "Specifies single, two, three, and four-core XLPE insulated armored and unarmored aluminum and copper power cables for working voltage up to and including 1100 V in power distribution networks.",
        "keywords": ["electrical", "xlpe cable", "armored cable", "underground cable", "aluminum cable", "power distribution", "1.1 kv"]
    },
    {
        "is_code": "IS 7098 (Part 2):2011",
        "title": "Crosslinked Polyethylene Insulated Thermoplastic Sheathed Cables (Part 2: For Working Voltages from 3.3 kV up to 33 kV)",
        "category": "Electrical",
        "scope": "Covers high-tension (HT) XLPE insulated cables with metallic screen and extruded armor for power transmission and primary distribution networks operating at voltages from 3.3 kV to 33 kV.",
        "keywords": ["electrical", "ht cable", "xlpe", "11kv cable", "33kv cable", "power transmission", "high voltage"]
    },
    {
        "is_code": "IS 2026 (Part 1):2011",
        "title": "Power Transformers - Part 1: General Requirements",
        "category": "Electrical",
        "scope": "Applies to large three-phase and single-phase power transformers (including auto-transformers) used in transmission substations, power generating stations, and heavy industrial facilities.",
        "keywords": ["electrical", "power transformer", "substation", "high voltage", "grid transformer", "step-up"]
    },
    {
        "is_code": "IS 9857:1990",
        "title": "Welding Cables - Specification",
        "category": "Electrical",
        "scope": "Covers requirements of flexible copper and aluminum conductor cables insulated with elastomeric or PVC compound for secondary circuit of electric arc welding equipment.",
        "keywords": ["electrical", "welding cable", "arc welding", "flexible copper", "rubber cable", "welding electrode cable"]
    },

    # 4. FOOD
    {
        "is_code": "IS 1155:1968",
        "title": "Wheat Flour (Maida and Chakki Atta) - Specification",
        "category": "Food",
        "scope": "Covers whole wheat flour (Chakki Atta) and refined flour (Maida) for human consumption and procurement by public distribution systems, defense rations, and institutions. Specifies limits on moisture (max 14.0%), total ash (max 2.0% for atta), acid insoluble ash, gluten content (min 6.0%), and freedom from rodent hair and insect infestation.",
        "keywords": ["food", "wheat flour", "atta", "chakki atta", "maida", "grain", "rations", "pds", "moisture", "gluten", "ash content"]
    },
    {
        "is_code": "IS 14543:2016",
        "title": "Packaged Drinking Water (Other than Packaged Natural Mineral Water) - Specification",
        "category": "Food",
        "scope": "Specifies chemical, physical, and microbiological requirements for packaged drinking water filled in sealed retail bottles, pet jars, and bulk 20-litre carboys. Details limits on TDS (75 to 500 mg/l), hardness, heavy metals, pesticides, Coliforms, E. coli, and mandatory remineralization.",
        "keywords": ["food", "packaged drinking water", "bottled water", "water 20l", "ro water", "drinking water", "tds", "microbiological", "mineral water"]
    },
    {
        "is_code": "IS 13428:2005",
        "title": "Packaged Natural Mineral Water - Specification",
        "category": "Food",
        "scope": "Covers potable mineral water sourced directly from underground aquifers, natural springs, or borewells, containing distinctive natural dissolved mineral salts. Restricts chemical treatment while mandating microbiological sterility.",
        "keywords": ["food", "natural mineral water", "spring water", "aquifer", "drinking water", "beverage", "trace minerals"]
    },
    {
        "is_code": "IS 1165:2002",
        "title": "Milk Powder - Specification",
        "category": "Food",
        "scope": "Covers requirements of whole milk powder, partly skimmed milk powder, and skimmed milk powder for institutional procurement, army rations, and confectionery. Specifies moisture (max 4.0%), fat content (min 26.0% for whole milk), titratable acidity, and total bacterial count.",
        "keywords": ["food", "milk powder", "dairy", "skimmed milk", "whole milk powder", "fat content", "powdered milk", "rations"]
    },
    {
        "is_code": "IS 515:1959",
        "title": "Specification for Refined Sugar",
        "category": "Food",
        "scope": "Covers chemical purity and grade specifications for refined white cane sugar and beet sugar for food processing, sweet manufacture, and hospital/institutional use. Limits moisture max 0.05%, polarization min 99.8%, and reducing sugar max 0.04%.",
        "keywords": ["food", "sugar", "refined sugar", "white sugar", "sucrose", "cane sugar", "sweetener", "confectionery"]
    },
    {
        "is_code": "IS 1005:1992",
        "title": "Edible Common Salt - Specification",
        "category": "Food",
        "scope": "Covers specifications for edible common salt, iodized salt, and vacuum-evaporated table salt for human consumption. Specifies minimum sodium chloride content (96.0% dry basis), water insoluble matter, moisture, and iodine content (min 15 ppm at retail level).",
        "keywords": ["food", "salt", "iodized salt", "common salt", "table salt", "sodium chloride", "iodine", "edible salt"]
    },
    {
        "is_code": "IS 548 (Part 1):1964",
        "title": "Methods of Sampling and Test for Oils and Fats - Part 1: Sampling, Physical and Chemical Tests",
        "category": "Food",
        "scope": "Prescribes methods of sampling and testing for vegetable oils, cooking oils, mustard oil, soybean oil, sunflower oil, and animal fats. Details determinations of moisture, insoluble impurities, acid value, iodine value, and saponification value.",
        "keywords": ["food", "edible oil", "cooking oil", "mustard oil", "sunflower oil", "fats", "acid value", "saponification"]
    },
    {
        "is_code": "IS 4251:1967",
        "title": "Quality Tolerances for Water for Processed Food Industry",
        "category": "Food",
        "scope": "Prescribes quality limits for water used as an ingredient or processing aid in food processing factories, dairy plants, beverage bottling plants, canning factories, and bakeries.",
        "keywords": ["food", "process water", "food industry", "beverage", "dairy plant", "water quality", "canning"]
    },
    {
        "is_code": "IS 15757:2007",
        "title": "Fortified Wheat Flour (Chakki Atta) - Specification",
        "category": "Food",
        "scope": "Specifies whole wheat flour fortified with essential micronutrients: Iron (sodium iron EDTA or ferrous sulphate), Folic acid, and Vitamin B12, for government social welfare feeding schemes and public distribution.",
        "keywords": ["food", "fortified flour", "chakki atta", "micronutrients", "iron fortified", "mid day meal", "welfare ration"]
    },
    {
        "is_code": "IS 16076:2013",
        "title": "Fortified Edible Vegetable Oils - Specification",
        "category": "Food",
        "scope": "Specifies requirements for edible vegetable oils fortified with Vitamin A (retinyl acetate/palmitate) and Vitamin D2/D3 for fighting malnutrition through targeted public procurement.",
        "keywords": ["food", "fortified oil", "vegetable oil", "vitamin a", "vitamin d", "edible oil", "cooking oil", "nutrition"]
    },
    {
        "is_code": "IS 1488:1969",
        "title": "Canned Green Peas - Specification",
        "category": "Food",
        "scope": "Prescribes requirements for green peas canned in brine for institutional catering and defense rations. Covers vacuum, headspace, drained weight, and defects.",
        "keywords": ["food", "canned peas", "canned food", "preserved vegetables", "tinned food", "defense rations"]
    },

    # 5. TEXTILES
    {
        "is_code": "IS 16289:2014",
        "title": "Medical Textiles - Surgical Face Masks - Specification",
        "category": "Textiles",
        "scope": "Covers design, construction, and performance of 3-ply disposable surgical face masks made of nonwoven polypropylene fabrics with meltblown microfiltration media. Mandates Bacterial Filtration Efficiency (BFE Class 1 min 95%, Class 2 & 3 min 98%), differential pressure (breathability), synthetic blood splash resistance at 120 mmHg, and sub-micron particulate filtration efficiency (PFE).",
        "keywords": ["textiles", "surgical mask", "face mask", "medical textiles", "meltblown", "bfe", "ppe", "hospital", "splash resistance", "3-ply mask"]
    },
    {
        "is_code": "IS 17349:2020",
        "title": "Medical Textiles - Protective Coveralls for Healthcare Workers - Specification",
        "category": "Textiles",
        "scope": "Specifies material and barrier performance of disposable protective coveralls (PPE suits) for healthcare personnel handling biological hazards and infectious viral agents. Requires synthetic blood penetration resistance at 3.5 kPa (ASTM F1670), heat-sealed taped seams, and tear resistance.",
        "keywords": ["textiles", "coveralls", "ppe suit", "healthcare", "protective clothing", "viral barrier", "synthetic blood penetration", "seam tape"]
    },
    {
        "is_code": "IS 15809:2008",
        "title": "High Visibility Warning Clothes - Specification",
        "category": "Textiles",
        "scope": "Specifies photometric and physical performance of high-visibility safety clothing (reflective vests, jackets, coats) for road workers, airport ground staff, and emergency services. Mandates fluorescent background material (yellow/orange) and retroreflective tape luminance.",
        "keywords": ["textiles", "reflective vest", "high visibility", "safety jacket", "fluorescent", "retroreflective", "road worker", "traffic safety"]
    },
    {
        "is_code": "IS 1969 (Part 1):2018",
        "title": "Textiles - Tensile Properties of Fabrics - Determination of Maximum Force and Elongation (Strip Method)",
        "category": "Textiles",
        "scope": "Prescribes procedure for determining breaking strength (maximum tensile force) and elongation at break of woven and knitted fabrics using the strip method on constant-rate-of-extension tensile testing machines.",
        "keywords": ["textiles", "tensile strength", "breaking force", "fabric test", "elongation", "woven fabric", "strip method"]
    },
    {
        "is_code": "IS 2977:1989",
        "title": "Terry Towels and Terry Towelling Cloth - Specification",
        "category": "Textiles",
        "scope": "Prescribes requirements for cotton terry towels (bath towels, hand towels, face towels) for hospital wards, government guest houses, and hotels. Mandates pile yarn count, water absorbency rate, color fastness, and dimensional stability.",
        "keywords": ["textiles", "towels", "terry towels", "bath towel", "cotton cloth", "absorbency", "hospital linen", "bed linen"]
    },
    {
        "is_code": "IS 15852:2016",
        "title": "Cotton-Polyester Blended Fabrics for Uniforms - Specification",
        "category": "Textiles",
        "scope": "Specifies requirements for woven blended shirting and suiting fabrics (e.g. 67/33 or 80/20 polyester-cotton) for military, police, paramilitary, and school uniforms. Details breaking strength, tear resistance, pilling resistance, and wash fastness.",
        "keywords": ["textiles", "uniform fabric", "poly-cotton", "shirting", "suiting", "police uniform", "tear strength", "blended fabric"]
    },
    {
        "is_code": "IS 177:2016",
        "title": "Cotton Drill - Specification",
        "category": "Textiles",
        "scope": "Specifies physical and chemical requirements of all-cotton heavy drill cloth used for military dungarees, industrial workwear, overalls, aprons, and tentage.",
        "keywords": ["textiles", "cotton drill", "heavy cotton", "dungarees", "workwear", "industrial uniform", "overalls"]
    },
    {
        "is_code": "IS 1259:2016",
        "title": "Vinyl Coated Fabrics (Rexine / Artificial Leather) - Specification",
        "category": "Textiles",
        "scope": "Covers PVC coated knitted and woven fabrics (artificial leather / rexine) for automotive seat upholstery, railway berths, hospital mattress covers, and protective tarpaulins.",
        "keywords": ["textiles", "rexine", "artificial leather", "pvc coated fabric", "upholstery", "seat cover", "waterproof fabric"]
    },
    {
        "is_code": "IS 16654:2017",
        "title": "Geotextiles Used in Subsurface Drainage - Specification",
        "category": "Textiles",
        "scope": "Specifies physical, hydraulic, and mechanical requirements of non-woven polypropylene or polyester geotextile membranes used for road sub-grade stabilization, retaining wall drainage, and embankment erosion control.",
        "keywords": ["textiles", "geotextiles", "non-woven", "drainage membrane", "soil stabilization", "road construction", "filtration"]
    },
    {
        "is_code": "IS 1390:1983",
        "title": "Methods for Determination of pH Value of Aqueous Extracts of Textile Materials",
        "category": "Textiles",
        "scope": "Prescribes electrometric methods for measuring pH value of water extract of fabrics, wool, cotton, and synthetic yarns to prevent skin irritation and contact dermatitis.",
        "keywords": ["textiles", "ph value", "skin safety", "aqueous extract", "dyeing test", "skin contact"]
    },

    # 6. PIPES
    {
        "is_code": "IS 4985:2021",
        "title": "Unplasticized Polyvinyl Chloride (uPVC) Pipes for Potable Water Supplies - Specification",
        "category": "Pipes",
        "scope": "Covers requirements for unplasticized polyvinyl chloride (uPVC) pipes with plain or socket ends for municipal, rural, and domestic potable water supply. Classes: Class 1 (0.25 MPa) to Class 6 (1.6 MPa) from 20 mm to 630 mm diameter. Mandates lead-free stabilizer formulations, hydrostatic pressure test, and impact resistance.",
        "keywords": ["pipes", "upvc", "upvc pipes", "potable water", "drinking water pipe", "lead free", "pvc plumbing", "water supply", "pressure pipe", "jal jeevan mission"]
    },
    {
        "is_code": "IS 15778:2007",
        "title": "Chlorinated Polyvinyl Chloride (CPVC) Pipes for Potable Hot and Cold Water Distribution Supplies",
        "category": "Pipes",
        "scope": "Specifies requirements for CPVC pipes in copper tube sizes (CTS) SDR 11 and SDR 13.5 for pressurized domestic and commercial hot and cold water distribution up to 93°C. Covers tensile strength, flattening test, and thermal expansion properties.",
        "keywords": ["pipes", "cpvc", "cpvc pipes", "hot water pipe", "plumbing", "cold water", "sdr 11", "sdr 13.5", "temperature resistance"]
    },
    {
        "is_code": "IS 8329:2000",
        "title": "Centrifugally Cast (Spun) Ductile Iron Pipes for Water, Gas and Sewage - Specification",
        "category": "Pipes",
        "scope": "Covers centrifugally cast ductile iron (DI) pipes socket and spigot type (Class K7, K9, K12) with internal cement mortar lining and external zinc-bitumen coating for bulk potable water transmission, fire mains, and sewerage pumping lines.",
        "keywords": ["pipes", "ductile iron", "di pipes", "class k9", "class k7", "water transmission", "sewage pipe", "spun pipes", "cement lining"]
    },
    {
        "is_code": "IS 14333:1996",
        "title": "High Density Polyethylene (HDPE) Pipes for Sewerage - Specification",
        "category": "Pipes",
        "scope": "Covers black HDPE pipes (grades PE 63, PE 80, PE 100) from 63 mm to 1000 mm outer diameter for municipal sewerage, storm water drainage, and industrial chemical effluents under gravity and low pressure flow.",
        "keywords": ["pipes", "hdpe", "hdpe pipes", "sewerage", "drainage pipe", "pe 100", "pe 80", "polyethylene", "effluent"]
    },
    {
        "is_code": "IS 1239 (Part 2):2011",
        "title": "Steel Tubes, Tubulars and Other Wrought Steel Fittings - Specification (Part 2: Fittings)",
        "category": "Pipes",
        "scope": "Covers wrought steel and malleable iron pipe fittings: elbows, tees, reducers, couplings, nipples, and unions for threaded plumbing, steam lines, and fire fighting sprinkler systems.",
        "keywords": ["pipes", "pipe fittings", "elbows", "tees", "gi fittings", "plumbing fittings", "unions", "threaded fittings"]
    },
    {
        "is_code": "IS 458:2003",
        "title": "Precast Concrete Pipes (With and Without Reinforcement) - Specification",
        "category": "Pipes",
        "scope": "Covers requirements for precast non-reinforced and reinforced concrete pipes (NP2, NP3, NP4 classes) used for culverts, highway crossings, railway tracks, and storm water drains.",
        "keywords": ["pipes", "rcc pipes", "concrete pipes", "culverts", "np2", "np3", "np4", "drainage", "storm water"]
    },
    {
        "is_code": "IS 13592:2013",
        "title": "Unplasticized PVC Pipes for Soil and Waste Discharge System Inside Buildings",
        "category": "Pipes",
        "scope": "Specifies uPVC pipes for soil, waste, and rainwater drainage systems inside buildings (SWR pipes). Type A for rainwater drainage, Type B for soil and waste discharge with ring fit socket joints.",
        "keywords": ["pipes", "swr pipes", "soil waste rainwater", "drainage", "building plumbing", "pvc sewer", "sanitary pipes"]
    },
    {
        "is_code": "IS 14846:2000",
        "title": "Sluice Valves for Water Works Purposes - Specification",
        "category": "Pipes",
        "scope": "Covers cast iron resilient seated and metal seated sluice valves (gate valves) with flanged ends from 50 mm to 1200 mm diameter for water supply and transmission pipeline isolation (PN 1.0 and PN 1.6).",
        "keywords": ["pipes", "valves", "sluice valve", "gate valve", "water distribution", "flanged valve", "pipeline isolation"]
    },
    {
        "is_code": "IS 1536:2001",
        "title": "Centrifugally Cast (Spun) Iron Pressure Pipes for Water, Gas and Sewage",
        "category": "Pipes",
        "scope": "Specifies cast iron (CI) pressure pipes for water mains, fire protection lines, and municipal gas transmission lines.",
        "keywords": ["pipes", "cast iron pipe", "ci pipe", "pressure pipe", "water mains", "fire water pipe"]
    },

    # 7. PAINTS
    {
        "is_code": "IS 154:2015",
        "title": "Synthetic Enamel Paint, Exterior, Undercoating and Finishing - Specification",
        "category": "Paints",
        "scope": "Covers air-drying alkyd resin based gloss synthetic enamel paint for protective and decorative finishing on steel gates, grills, machinery, wood, and exterior architectural surfaces. Specifies drying time, gloss retention, adhesion, and lead limits (< 90 ppm).",
        "keywords": ["paints", "enamel paint", "synthetic enamel", "gloss finish", "metal paint", "wood paint", "anti rust", "alkyd resin"]
    },
    {
        "is_code": "IS 5410:2013",
        "title": "Cement Paint - Specification",
        "category": "Paints",
        "scope": "Covers Portland cement based dry powder paint formulated for application on exterior porous masonry surfaces, cement plaster, concrete blocks, and brickwork. Provides weatherproofing, water repellency, and fungal resistance.",
        "keywords": ["paints", "cement paint", "exterior paint", "masonry coating", "weatherproof paint", "facade paint", "plaster paint"]
    },
    {
        "is_code": "IS 15489:2004",
        "title": "Plastic Emulsion Paint - Specification",
        "category": "Paints",
        "scope": "Specifies requirements for water-thinnable plastic emulsion paints (acrylic interior and exterior emulsions) for concrete walls, gypsum plaster, and ceilings. Mandates scrub resistance, washability, opacity, and volatile organic compound (VOC) limits.",
        "keywords": ["paints", "plastic emulsion", "acrylic emulsion", "interior paint", "wall paint", "washable paint", "low voc", "matte finish"]
    },
    {
        "is_code": "IS 2074:2015",
        "title": "Ready Mixed Paint, Air Drying, Red Oxide-Zinc Chrome, Priming - Specification",
        "category": "Paints",
        "scope": "Covers solvent-borne red oxide zinc chrome anti-corrosive primer for ferrous metal surfaces, steel bridges, trusses, rolling shutters, and storage tanks prior to application of enamel topcoats.",
        "keywords": ["paints", "red oxide primer", "anti corrosive primer", "zinc chrome", "metal primer", "rust prevention", "steel coating"]
    },
    {
        "is_code": "IS 101 (Part 1):1986",
        "title": "Methods of Sampling and Test for Paints, Varnishes and Related Products - Part 1: Tests on Liquid Paints",
        "category": "Paints",
        "scope": "Covers standardized laboratory test methods for paints: consistency, viscosity, density, drying time, fineness of grind, flash point, and non-volatile matter content.",
        "keywords": ["paints", "paint testing", "viscosity", "drying time", "fineness of grind", "paint sampling", "laboratory test"]
    },
    {
        "is_code": "IS 2932:2003",
        "title": "Enamel, Synthetic, Exterior: Undercoating and Finishing - Specification",
        "category": "Paints",
        "scope": "Covers premium synthetic enamel paint formulated for railway rolling stock, state transport buses, public transport, and harsh industrial environments requiring high chemical and UV resistance.",
        "keywords": ["paints", "railway enamel", "industrial paint", "synthetic enamel", "uv resistance", "protective coating"]
    },
    {
        "is_code": "IS 13183:2014",
        "title": "Polyurethane Coatings for Exterior Application - Specification",
        "category": "Paints",
        "scope": "Covers two-pack polyurethane (PU) finish coatings providing outstanding weatherability, abrasion resistance, and color retention on bridges, chemical storage tanks, and industrial steelwork.",
        "keywords": ["paints", "pu paint", "polyurethane", "two pack coating", "corrosion resistance", "chemical tanks", "protective coating"]
    },
    {
        "is_code": "IS 341:2018",
        "title": "Black Japan, Types A, B and C - Specification",
        "category": "Paints",
        "scope": "Specifies bituminous black paint for anti-corrosion coating of cast iron underground pipes, foundation structural steel, chassis, and marine hardware.",
        "keywords": ["paints", "black japan", "bituminous paint", "anti corrosion", "cast iron coating", "pipe paint"]
    },

    # 8. PACKAGING
    {
        "is_code": "IS 2771 (Part 1):1990",
        "title": "Corrugated Fibreboard Boxes - Specification (Part 1: For General Packaging)",
        "category": "Packaging",
        "scope": "Specifies construction, bursting strength, edge crush resistance (ECT), flute geometry (A, B, C, E flutes), and drop test requirements for 3-ply, 5-ply, and 7-ply corrugated kraft paper shipping boxes and master cartons for goods transit.",
        "keywords": ["packaging", "corrugated boxes", "cartons", "kraft paper", "bursting strength", "flute", "shipping carton", "packaging box"]
    },
    {
        "is_code": "IS 10221:2008",
        "title": "Code of Practice for Anti-Corrosion Packaging",
        "category": "Packaging",
        "scope": "Prescribes standard guidelines for preservation and packaging of precision metal components, machinery, bearings, and defense hardware against corrosion during storage and maritime transport using VCI paper, desiccants, and barrier films.",
        "keywords": ["packaging", "vci packaging", "anti corrosion packaging", "desiccants", "moisture barrier", "rust prevention packaging", "machinery transit"]
    },
    {
        "is_code": "IS 15644:2006",
        "title": "Wooden Crates - Specification",
        "category": "Packaging",
        "scope": "Specifies design, timber species, nailing, corner bracing, and load carrying capacity of wooden crates and sheathed timber boxes for shipping heavy industrial equipment, transformers, and export cargo.",
        "keywords": ["packaging", "wooden crates", "timber boxes", "export packaging", "heavy cargo packaging", "wooden box"]
    },
    {
        "is_code": "IS 12795:2016",
        "title": "Linear Low Density Polyethylene (LLDPE) Pouches for Packaging of Liquid Milk - Specification",
        "category": "Packaging",
        "scope": "Specifies co-extruded virgin polyethylene film pouches for automated packaging of pasteurized liquid milk. Mandates drop test, seal integrity, dart impact resistance, light transmission barrier, and zero taint/odor.",
        "keywords": ["packaging", "milk pouch", "lldpe film", "liquid packaging", "dairy packaging", "plastic pouch", "food contact film"]
    },
    {
        "is_code": "IS 14001:2010",
        "title": "High Density Polyethylene (HDPE) / Polypropylene (PP) Woven Sacks for Packaging of 50 kg Cement",
        "category": "Packaging",
        "scope": "Specifies requirements for HDPE/PP woven block bottom valve sacks or stitched bags for packing 50 kg cement. Covers fabric tensile breaking strength, elongation, drop test from 1.2 m, and air permeability for high-speed filling.",
        "keywords": ["packaging", "cement bags", "hdpe sacks", "pp woven sacks", "50 kg bags", "cement packaging", "drop test"]
    },
    {
        "is_code": "IS 14005:2018",
        "title": "High Density Polyethylene (HDPE) / Polypropylene (PP) Woven Sacks for Packaging of Food Grains",
        "category": "Packaging",
        "scope": "Specifies woven sacks manufactured from virgin food-grade polymer tapes for packaging 50 kg and 25 kg food grains (wheat, paddy, rice, maize) for Food Corporation of India (FCI) procurement and buffer stocking.",
        "keywords": ["packaging", "grain sacks", "food grain bags", "hdpe woven sacks", "fci sacks", "paddy packaging", "wheat bags"]
    },
    {
        "is_code": "IS 10146:1982",
        "title": "Polyethylene for its Safe Use in Contact with Foodstuffs, Pharmaceuticals and Drinking Water",
        "category": "Packaging",
        "scope": "Specifies positive list of additives, monomer purity, overall migration limits (max 10 mg/dm2 or 60 mg/kg), and extraction tests for polyethylene polymers used in food containers, bottles, and films.",
        "keywords": ["packaging", "food grade plastic", "polyethylene", "migration limit", "food contact material", "fda bis", "containers"]
    },
    {
        "is_code": "IS 15886:2010",
        "title": "Agricultural Produce Packaging - Woven Sacks for Packaging Food Grains - Specification",
        "category": "Packaging",
        "scope": "Covers standardized woven bags for procurement of agricultural produce with UV stabilization for outdoor depot stack storage up to 12 months.",
        "keywords": ["packaging", "agricultural packaging", "grain bags", "uv stabilized", "jute alternative", "produce packaging"]
    },
    {
        "is_code": "IS 13947:1994",
        "title": "Corrugated Fibreboard Containers for Packing of Fruits and Vegetables",
        "category": "Packaging",
        "scope": "Specifies ventilated, moisture-resistant corrugated boxes for grading, packing, cold storage, and export of fresh fruits (apples, mangoes, grapes) and horticultural produce.",
        "keywords": ["packaging", "fruit boxes", "horticulture packaging", "cold storage box", "apple carton", "ventilated box"]
    },

    # 9. SAFETY EQUIPMENT
    {
        "is_code": "IS 2925:1984",
        "title": "Industrial Safety Helmets - Specification",
        "category": "Safety Equipment",
        "scope": "Covers requirements for non-metallic industrial safety helmets (hard hats) providing head protection against falling objects, shock, and electrical shock. Specifies shock absorption (transmitted force max 5.0 kN), penetration resistance (3 kg drop), flame retardancy, and electrical insulation at 2000 V.",
        "keywords": ["safety equipment", "safety helmet", "hard hat", "head protection", "construction safety", "shock absorption", "electrical helmet", "ppe"]
    },
    {
        "is_code": "IS 15683:2018",
        "title": "Portable Fire Extinguishers - Performance and Construction - Specification",
        "category": "Safety Equipment",
        "scope": "Covers design, construction, mechanical strength, and fire test performance of portable fire extinguishers: stored-pressure ABC dry powder, CO2, water, and mechanical foam types. Specifies fire ratings (1A to 20A, 8B to 144B), pressure gauges, burst pressure, and discharge duration.",
        "keywords": ["safety equipment", "fire extinguisher", "abc extinguisher", "dry powder", "co2 extinguisher", "fire safety", "fire fighting", "portable extinguisher"]
    },
    {
        "is_code": "IS 15298 (Part 2):2016",
        "title": "Personal Protective Equipment - Safety Footwear - Specification",
        "category": "Safety Equipment",
        "scope": "Specifies design, construction, and mechanical performance of industrial safety shoes and boots fitted with safety toecap resistant to 200 Joules impact energy and 15 kN compression. Covers slip resistance (SRC), oil/chemical resistance, antistatic properties, and penetration-resistant steel midsoles.",
        "keywords": ["safety equipment", "safety shoes", "safety boots", "steel toe", "safety footwear", "slip resistant", "protective shoes", "ppe"]
    },
    {
        "is_code": "IS 3521 (Part 1):1999",
        "title": "Industrial Safety Belts and Harnesses - Specification (Full Body Harnesses)",
        "category": "Safety Equipment",
        "scope": "Specifies requirements for industrial fall arrest systems, full body harnesses (Class A), lanyards, energy absorbers, and connector snap hooks for workers at heights on construction scaffolds, transmission towers, and high-rise structures.",
        "keywords": ["safety equipment", "safety harness", "safety belt", "fall arrest", "full body harness", "lanyard", "working at height", "construction safety"]
    },
    {
        "is_code": "IS 8521 (Part 1):1977",
        "title": "Industrial Safety Face Shields - Part 1: With Plastics Visor",
        "category": "Safety Equipment",
        "scope": "Covers requirements for industrial face shields with clear polycarbonate or cellulose acetate visors for protection of eyes and face against flying particles, chemical splashes, molten metal drops, and grinding sparks.",
        "keywords": ["safety equipment", "face shield", "eye protection", "grinding shield", "chemical splash shield", "polycarbonate visor", "ppe"]
    },
    {
        "is_code": "IS 9473:2002",
        "title": "Respiratory Protective Devices - Filtering Half Masks to Protect Against Particles",
        "category": "Safety Equipment",
        "scope": "Specifies performance requirements and test methods for particle filtering half masks (respirators FFP1, FFP2, FFP3, equivalent to N95/N99). Covers sodium chloride and paraffin oil penetration tests (min 94% efficiency for FFP2), breathing resistance, and carbon dioxide clearance.",
        "keywords": ["safety equipment", "respirator", "n95 mask", "ffp2 mask", "particulate mask", "dust mask", "respiratory protection", "filtration"]
    },
    {
        "is_code": "IS 2573:1986",
        "title": "Leather Safety Boots and Shoes for Heavy Metal Industries",
        "category": "Safety Equipment",
        "scope": "Specifies heavy-duty leather boots for foundry and molten steel workers with heat resistant nitrile rubber soles, quick-release buckles, and molten metal splash shedding design.",
        "keywords": ["safety equipment", "foundry boots", "leather safety shoes", "molten metal", "heat resistant", "steel industry boots"]
    },
    {
        "is_code": "IS 6994 (Part 1):1973",
        "title": "Industrial Safety Gloves - Specification (Part 1: Leather and Cotton Gloves)",
        "category": "Safety Equipment",
        "scope": "Specifies leather split gloves, chrome leather gloves, and reinforced cotton gloves for hand protection against cuts, abrasions, puncture, and handling rough steel bars and glass.",
        "keywords": ["safety equipment", "safety gloves", "leather gloves", "cut resistant", "hand protection", "welding gloves", "work gloves"]
    },
    {
        "is_code": "IS 8808:1995",
        "title": "Burner and Fireman's Boots - Specification",
        "category": "Safety Equipment",
        "scope": "Covers rubber boots for fire fighters and boiler attendants offering protection against high radiant heat, flame immersion, live electrical conductors, and punctured sole hazards.",
        "keywords": ["safety equipment", "fireman boots", "fire fighting boots", "heat resistant footwear", "electrical safety boots"]
    }
]

out_dir = os.path.join(os.path.dirname(__file__), 'backend', 'data')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'standards.json')

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(STANDARDS, f, indent=2, ensure_ascii=False)

print(f'Successfully wrote {len(STANDARDS)} standards to {out_path}')
category_counts = {}
for s in STANDARDS:
    cat = s['category']
    category_counts[cat] = category_counts.get(cat, 0) + 1
for cat, count in category_counts.items():
    print(f' - {cat}: {count}')
