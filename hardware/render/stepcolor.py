"""Load a STEP file into (vertices, faces, rgb) chunks, keeping XCAF colours."""
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorType
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.Quantity import Quantity_Color
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
from OCP.IFSelect import IFSelect_RetDone
import numpy as np

def _col(ct, shape, default):
    c = Quantity_Color()
    for t in (XCAFDoc_ColorType.XCAFDoc_ColorSurf, XCAFDoc_ColorType.XCAFDoc_ColorGen):
        ok = ct.GetColor_s(shape, t, c) if isinstance(shape, TDF_Label) else ct.GetColor(shape, t, c)
        if ok:
            return (c.Red(), c.Green(), c.Blue())
    return default

def load(path, default=(0.6, 0.6, 0.6), tol=0.02):
    doc = TDocStd_Document(TCollection_ExtendedString("doc"))
    r = STEPCAFControl_Reader(); r.SetColorMode(True)
    assert r.ReadFile(path) == IFSelect_RetDone, path
    r.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    labels = TDF_LabelSequence(); st.GetFreeShapes(labels)
    out = []
    def walk(lab, loc, inherited):
        shape = st.GetShape_s(lab)
        c = _col(ct, lab, None) or inherited
        if st.IsAssembly_s(lab) or st.IsCompound_s(lab) and st.IsReference_s(lab) is False and False:
            pass
        comps = TDF_LabelSequence()
        if st.IsAssembly_s(lab):
            st.GetComponents_s(lab, comps)
            for i in range(1, comps.Length() + 1):
                cl = comps.Value(i)
                ref = TDF_Label()
                st.GetReferredShape_s(cl, ref)
                cc = _col(ct, cl, None) or c
                walk(ref, loc.Multiplied(st.GetLocation_s(cl)), cc)
            return
        shape = shape.Located(loc.Multiplied(shape.Location()))
        BRepMesh_IncrementalMesh(shape, tol, False, 0.3, True)
        ex = TopExp_Explorer(shape, TopAbs_FACE)
        while ex.More():
            f = TopoDS.Face_s(ex.Current())
            fc = _col(ct, f, None)
            if fc is None:
                # colour on sub-shape label?
                sl = TDF_Label()
                if st.FindSubShape(lab, f, sl): fc = _col(ct, sl, None)
            fc = fc or c or default
            L = TopLoc_Location()
            tri = BRep_Tool.Triangulation_s(f, L)
            if tri is not None:
                tr = L.Transformation()
                v = np.array([[p.X(), p.Y(), p.Z()] for p in (tri.Node(i).Transformed(tr) for i in range(1, tri.NbNodes() + 1))])
                idx = []
                rev = f.Orientation() == 1  # TopAbs_REVERSED
                for i in range(1, tri.NbTriangles() + 1):
                    a, b, cc = tri.Triangle(i).Get()
                    idx.append((a - 1, cc - 1, b - 1) if rev else (a - 1, b - 1, cc - 1))
                out.append((v, np.array(idx), fc))
            ex.Next()
    for i in range(1, labels.Length() + 1):
        walk(labels.Value(i), TopLoc_Location(), None)
    return out
