# opcua/client.py

from __future__ import absolute_import

import os

from editors.ConfTreeNodeEditor import ConfTreeNodeEditor
from .opcua_client_maker import OPCUAClientPanel, OPCUAClientModel

import util.paths as paths

# Paths to open62541 assume that 
# - open62541 directory is aside beremiz directory
# - open62541 was just built (not installed)

Open62541Path = paths.ThirdPartyPath("open62541")
Open62541LibraryPath = os.path.join(Open62541Path,"build","bin") 
Open62541IncludePaths = [os.path.join(Open62541Path, *dirs) for dirs in [
    ("plugins","include"),
    ("build","src_generated"),
    ("include",),
    ("arch",)]]

class OPCUAClientEditor(ConfTreeNodeEditor):
    CONFNODEEDITOR_TABS = [
        (_("OPC-UA Client"), "CreateOPCUAClient_UI")]

    def Log(self, msg):
        self.Controler.GetCTRoot().logger.write(msg)

    def UriGetter(self):
        return self.Controler.GetServerURI() 

    def CreateOPCUAClient_UI(self, parent):
        return OPCUAClientPanel(parent, self.Controler.GetModelData(), self.Log, self.UriGetter)

class OPCUAClient(object):
    XSD = """<?xml version="1.0" encoding="ISO-8859-1" ?>
    <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <xsd:element name="OPCUAClient">
        <xsd:complexType>
          <xsd:attribute name="Server_URI" type="xsd:string" use="optional" default="opc.tcp://localhost:4840"/>
        </xsd:complexType>
      </xsd:element>
    </xsd:schema>
    """

    EditorType = OPCUAClientEditor

    def __init__(self):
        self.modeldata = OPCUAClientModel()

        filepath = self.GetFileName()
        if os.path.isfile(filepath):
            self.modeldata.LoadCSV(filepath)

    def GetModelData(self):
        return self.modeldata
    
    def GetServerURI(self):
        return self.GetParamsAttributes("OPCUAClient.Server_URI")["value"]

    def GetFileName(self):
        return os.path.join(self.CTNPath(), 'selected.csv')

    def OnCTNSave(self, from_project_path=None):
        self.modeldata.SaveCSV(self.GetFileName())
        return True

    def CTNGenerate_C(self, buildpath, locations):
        current_location = self.GetCurrentLocation()
        locstr = "_".join(map(str, current_location))
        c_path = os.path.join(buildpath, "opcua_client__%s.c" % locstr)

        c_code = self.modeldata.GenerateC(c_path, locstr, 
            self.GetParamsAttributes("OPCUAClient.Server_URI")["value"])

        with open(c_path, 'wb') as c_file:
            c_file.write(c_code)

        LDFLAGS = [' "' + os.path.join(Open62541LibraryPath, "libopen62541.a") + '"']

        CFLAGS = ' '.join(['-I"' + path + '"' for path in Open62541IncludePaths])

        return [(c_path, CFLAGS)], LDFLAGS, True

