#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Populate a REAL Enterprise Architect base repository (.qea) with the
znalosti.gov.sk architecture model.

Why this exists
---------------
A .qea is a SQLite database, but Enterprise Architect validates a complete,
version-stamped EA base schema (~200 system tables + seed rows) when it opens a
project. That schema ships only inside EA's own template `EABase.qea` and cannot
be reproduced by hand (attempts fail with "Sparx Systems Database API
[0x00001086]" or malformed inserts such as `Insert into usys_system () value ()`).

This script therefore does NOT build a schema. It opens an existing, valid EA
base file, introspects the actual columns of each table, and inserts the model
using only the columns that really exist. The result is a genuine .qea that EA
opens directly (File > Open Project).

How to use
----------
1. In Enterprise Architect: Home > New Project, save an empty project as
   `docs/architecture/base.qea` (this clones EABase.qea, which is free to copy).
   Alternatively copy EABase.qea from your EA installation directory to that path.
2. Commit/push that base.qea, or otherwise make it available at the path below.
3. Run:  python3 generate_qea_from_base.py [base.qea] [output.qea]
   Defaults: base = base.qea, output = znalosti-gov-sk-architecture.qea
"""

import os
import sys
import shutil
import sqlite3

import generate_ea_model as g   # reuses the in-memory model definition (g.m)

HERE = os.path.dirname(os.path.abspath(__file__))
NOW = "2026-06-26 00:00:00"


def table_columns(cur, table):
    try:
        return {row[1] for row in cur.execute("PRAGMA table_info(%s)" % table)}
    except sqlite3.OperationalError:
        return set()


def maxid(cur, table, col):
    try:
        v = cur.execute("SELECT MAX(%s) FROM %s" % (col, table)).fetchone()[0]
        return int(v) if v is not None else 0
    except (sqlite3.OperationalError, TypeError, ValueError):
        return 0


def insert(cur, table, values, existing):
    """Insert a row using only columns that exist in the target table."""
    cols = [c for c in values if c in existing]
    if not cols:
        return
    placeholders = ",".join("?" for _ in cols)
    collist = ",".join('"%s"' % c for c in cols)
    cur.execute('INSERT INTO "%s" (%s) VALUES (%s)' % (table, collist, placeholders),
                [values[c] for c in cols])


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "base.qea")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "znalosti-gov-sk-architecture.qea")

    if not os.path.exists(base):
        sys.exit("ERROR: base EA file not found: %s\n"
                 "Create one in EA (Home > New Project -> save as base.qea) or copy\n"
                 "EABase.qea from your Enterprise Architect installation directory." % base)

    shutil.copyfile(base, out)
    db = sqlite3.connect(out)
    cur = db.cursor()

    m = g.m

    # column inventories of the real EA schema
    C = {t: table_columns(cur, t) for t in
         ["t_package", "t_object", "t_attribute", "t_operation", "t_connector",
          "t_diagram", "t_diagramobjects", "t_diagramlinks", "usys_system"]}

    # id bases (append above whatever the base file already contains)
    base_pkg = maxid(cur, "t_package", "Package_ID")
    base_obj = maxid(cur, "t_object", "Object_ID")
    base_conn = maxid(cur, "t_connector", "Connector_ID")
    base_diag = maxid(cur, "t_diagram", "Diagram_ID")
    base_attr = maxid(cur, "t_attribute", "ID")
    base_op = maxid(cur, "t_operation", "OperationID")
    base_dobj = maxid(cur, "t_diagramobjects", "Instance_ID")
    base_dlink = maxid(cur, "t_diagramlinks", "Instance_ID")

    PKG_OBJ_OFFSET = base_obj + 100000   # separate id band for package-objects

    def PKID(pid):
        return base_pkg + pid

    def OBJID(eid):
        return base_obj + eid

    # the model root node of the base file (Parent_ID = 0)
    row = cur.execute(
        "SELECT Package_ID FROM t_package WHERE Parent_ID=0 ORDER BY Package_ID LIMIT 1"
    ).fetchone()
    root_model_id = row[0] if row else 0
    root_guid_row = cur.execute(
        "SELECT ea_guid FROM t_package WHERE Package_ID=?", (root_model_id,)).fetchone()
    root_guid = root_guid_row[0] if root_guid_row else g.guid()

    # ----- packages (+ their package-objects) ----------------------------
    for p in m.packages:
        parent = root_model_id if p["parent_id"] == 0 else PKID(p["parent_id"])
        insert(cur, "t_package", {
            "Package_ID": PKID(p["id"]), "Name": p["name"], "Parent_ID": parent,
            "CreatedDate": NOW, "ModifiedDate": NOW, "Notes": p["notes"],
            "ea_guid": p["guid"], "IsControlled": 0, "Protected": 0,
            "IsNamespace": 1, "TPos": p["id"], "BatchSave": 0, "BatchLoad": 0,
            "UseDTD": 0, "LogXML": 0, "UMLVersion": "2.5", "UseModelGen": 0,
        }, C["t_package"])
        insert(cur, "t_object", {
            "Object_ID": PKG_OBJ_OFFSET + p["id"], "Object_Type": "Package",
            "Name": p["name"], "Note": p["notes"], "Package_ID": parent,
            "Stereotype": "", "CreatedDate": NOW, "ModifiedDate": NOW,
            "ea_guid": g.guid(), "PDATA1": str(PKID(p["id"])), "ParentID": 0,
            "Scope": "Public", "NType": 0, "Status": "Proposed", "Visibility": "Public",
        }, C["t_object"])

    # ----- elements (+ attributes / operations) --------------------------
    attr_seq = base_attr
    op_seq = base_op
    for e in m.elements:
        insert(cur, "t_object", {
            "Object_ID": OBJID(e["id"]), "Object_Type": e["type"], "Name": e["name"],
            "Note": e["notes"], "Package_ID": PKID(e["package_id"]),
            "Stereotype": e["stereotype"], "CreatedDate": NOW, "ModifiedDate": NOW,
            "ea_guid": e["guid"], "Abstract": "1" if e["abstract"] else "0",
            "Scope": "Public", "ParentID": 0, "Status": "Proposed",
            "Visibility": "Public", "NType": 0,
        }, C["t_object"])
        pos = 0
        for a in e["attrs"]:
            pos += 1
            attr_seq += 1
            aname, atype = (a + ("",))[:2] if isinstance(a, tuple) else (a, "")
            insert(cur, "t_attribute", {
                "Object_ID": OBJID(e["id"]), "Name": aname, "Scope": "Private",
                "Type": atype, "Pos": pos, "ea_guid": g.guid(), "ID": attr_seq,
                "LowerBound": "1", "UpperBound": "1", "Object_Type": "Attribute",
                "IsStatic": 0, "IsCollection": 0, "IsOrdered": 0, "AllowDuplicates": 0,
                "Derived": 0, "Const": 0,
            }, C["t_attribute"])
        pos = 0
        for o in e["ops"]:
            pos += 1
            op_seq += 1
            oname, otype, onote = (list(o) + ["", ""])[:3]
            insert(cur, "t_operation", {
                "OperationID": op_seq, "Object_ID": OBJID(e["id"]), "Name": oname,
                "Scope": "Public", "Type": otype, "Pos": pos, "ea_guid": g.guid(),
                "Notes": onote, "ReturnArray": 0, "IsStatic": 0, "IsAbstract": 0,
                "Pure": 0, "IsQuery": 0, "IsConst": 0, "IsSynchronized": 0,
            }, C["t_operation"])

    # ----- connectors ----------------------------------------------------
    for c in m.connectors:
        insert(cur, "t_connector", {
            "Connector_ID": base_conn + c["id"], "Name": c["name"],
            "Connector_Type": c["type"], "Notes": c["notes"],
            "Start_Object_ID": OBJID(c["src"]), "End_Object_ID": OBJID(c["dst"]),
            "SourceCard": c["src_card"], "DestCard": c["dst_card"],
            "Stereotype": c["stereotype"], "ea_guid": c["guid"], "SeqNo": 0,
            "DestRole": "", "SourceRole": "", "Direction": "Source -> Destination",
        }, C["t_connector"])

    # ----- diagrams + placement -----------------------------------------
    dobj = base_dobj
    dlink = base_dlink
    cols_n, cell_w, cell_h, box_w, box_h = 4, 220, 150, 170, 90
    for d in m.diagrams:
        insert(cur, "t_diagram", {
            "Diagram_ID": base_diag + d["id"], "Package_ID": PKID(d["package_id"]),
            "Diagram_Type": d["type"], "Name": d["name"], "Notes": d["notes"],
            "CreatedDate": NOW, "ModifiedDate": NOW, "ea_guid": d["guid"],
            "Scale": 100, "ShowDetails": 0, "Orientation": "P", "cx": 827, "cy": 1169,
            "ParentID": 0,
        }, C["t_diagram"])
        placed = set()
        for idx, eid in enumerate(d["elems"]):
            dobj += 1
            col = idx % cols_n
            rrow = idx // cols_n
            left = 30 + col * cell_w
            top = 30 + rrow * cell_h
            insert(cur, "t_diagramobjects", {
                "Diagram_ID": base_diag + d["id"], "Object_ID": OBJID(eid),
                "RectTop": -top, "RectLeft": left, "RectRight": left + box_w,
                "RectBottom": -(top + box_h), "Sequence": idx + 1,
                "Instance_ID": dobj, "ObjectStyle": "",
            }, C["t_diagramobjects"])
            placed.add(eid)
        for c in m.connectors:
            if c["src"] in placed and c["dst"] in placed:
                dlink += 1
                insert(cur, "t_diagramlinks", {
                    "DiagramID": base_diag + d["id"], "ConnectorID": base_conn + c["id"],
                    "Geometry": "", "Style": "", "Hidden": 0, "Instance_ID": dlink,
                }, C["t_diagramlinks"])

    # ----- bump usys_system id counters (best effort) --------------------
    if C["usys_system"]:
        last_obj = PKG_OBJ_OFFSET + len(m.packages) + 1
        updates = {
            "LastObjectID": last_obj,
            "LastDiagramID": base_diag + len(m.diagrams) + 1,
            "LastConnectorID": base_conn + len(m.connectors) + 1,
        }
        for col, val in updates.items():
            if col in C["usys_system"]:
                try:
                    cur.execute('UPDATE usys_system SET "%s"=?' % col, (val,))
                except sqlite3.OperationalError:
                    pass

    db.commit()
    db.close()
    print("Base       : %s" % base)
    print("Packages   : %d (ids %d..%d)" % (len(m.packages), base_pkg + 1, base_pkg + len(m.packages)))
    print("Elements   : %d" % len(m.elements))
    print("Connectors : %d" % len(m.connectors))
    print("Diagrams   : %d" % len(m.diagrams))
    print("Wrote      : %s (%d bytes)" % (out, os.path.getsize(out)))


if __name__ == "__main__":
    main()
