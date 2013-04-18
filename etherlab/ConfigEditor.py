import os
import re
from types import TupleType

import wx
import wx.grid
import wx.gizmos
import wx.lib.buttons

from plcopen.structures import IEC_KEYWORDS, TestIdentifier
from controls import CustomGrid, CustomTable, FolderTree
from editors.ConfTreeNodeEditor import ConfTreeNodeEditor, SCROLLBAR_UNIT
from util.BitmapLibrary import GetBitmap

[ETHERCAT_VENDOR, ETHERCAT_GROUP, ETHERCAT_DEVICE] = range(3)

def AppendMenu(parent, help, id, kind, text):
    if wx.VERSION >= (2, 6, 0):
        parent.Append(help=help, id=id, kind=kind, text=text)
    else:
        parent.Append(helpString=help, id=id, kind=kind, item=text)

def GetVariablesTableColnames(position=False):
    _ = lambda x : x
    colname = ["#"]
    if position:
        colname.append(_("Position"))
    return colname + [_("Name"), _("Index"), _("SubIndex"), _("Type"), _("Access")]

ACCESS_TYPES = {
    'ro': 'R',
    'wo': 'W',
    'rw': 'R/W'}

def GetAccessValue(access, pdo_mapping):
    value = "SDO: %s" % ACCESS_TYPES.get(access, "")
    if pdo_mapping != "":
        value += ", PDO: %s" % pdo_mapping
    return value

VARIABLES_FILTERS = [
    (_("All"), (0x0000, 0xffff)),
    (_("Communication Parameters"), (0x1000, 0x1fff)),
    (_("Manufacturer Specific"), (0x2000, 0x5fff)),
    (_("Standardized Device Profile"), (0x6000, 0x9fff))]

VARIABLE_INDEX_FILTER_FORMAT = _("Variable Index: #x%4.4X")

ETHERCAT_INDEX_MODEL = re.compile("#x([0-9a-fA-F]{0,4})$")
ETHERCAT_SUBINDEX_MODEL = re.compile("#x([0-9a-fA-F]{0,2})$")
LOCATION_MODEL = re.compile("(?:%[IQM](?:[XBWLD]?([0-9]+(?:\.[0-9]+)*)))$")

NAVIGATION_KEYS = [
    wx.WXK_END,
    wx.WXK_HOME,
    wx.WXK_LEFT,
    wx.WXK_UP,
    wx.WXK_RIGHT,
    wx.WXK_DOWN,
    wx.WXK_PAGEUP,
    wx.WXK_PAGEDOWN,
    wx.WXK_NUMPAD_HOME,
    wx.WXK_NUMPAD_LEFT,
    wx.WXK_NUMPAD_UP,
    wx.WXK_NUMPAD_RIGHT,
    wx.WXK_NUMPAD_DOWN,
    wx.WXK_NUMPAD_PAGEUP,
    wx.WXK_NUMPAD_PAGEDOWN,
    wx.WXK_NUMPAD_END]

class NodeVariablesSizer(wx.FlexGridSizer):
    
    def __init__(self, parent, controler, position_column=False):
        wx.FlexGridSizer.__init__(self, cols=1, hgap=0, rows=2, vgap=5)
        self.AddGrowableCol(0)
        self.AddGrowableRow(1)
        
        self.Controler = controler
        self.PositionColumn = position_column
        
        self.VariablesFilter = wx.ComboBox(parent, style=wx.TE_PROCESS_ENTER)
        self.VariablesFilter.Bind(wx.EVT_COMBOBOX, self.OnVariablesFilterChanged)
        self.VariablesFilter.Bind(wx.EVT_TEXT_ENTER, self.OnVariablesFilterChanged)
        self.VariablesFilter.Bind(wx.EVT_CHAR, self.OnVariablesFilterKeyDown)
        self.AddWindow(self.VariablesFilter, flag=wx.GROW)
        
        self.VariablesGrid = wx.gizmos.TreeListCtrl(parent, 
                style=wx.TR_DEFAULT_STYLE |
                      wx.TR_ROW_LINES |
                      wx.TR_COLUMN_LINES |
                      wx.TR_HIDE_ROOT |
                      wx.TR_FULL_ROW_HIGHLIGHT)
        self.VariablesGrid.GetMainWindow().Bind(wx.EVT_LEFT_DOWN,
            self.OnVariablesGridLeftClick)
        self.AddWindow(self.VariablesGrid, flag=wx.GROW)
        
        self.Filters = []
        for desc, value in VARIABLES_FILTERS:
            self.VariablesFilter.Append(desc)
            self.Filters.append(value)
        
        self.VariablesFilter.SetSelection(0)
        self.CurrentFilter = self.Filters[0]
        self.VariablesFilterFirstCharacter = True
        
        if position_column:
            for colname, colsize, colalign in zip(GetVariablesTableColnames(position_column),
                                                  [40, 80, 350, 80, 100, 80, 150],
                                                  [wx.ALIGN_RIGHT, wx.ALIGN_RIGHT, wx.ALIGN_LEFT, 
                                                   wx.ALIGN_RIGHT, wx.ALIGN_RIGHT, wx.ALIGN_LEFT, 
                                                   wx.ALIGN_LEFT]):
                self.VariablesGrid.AddColumn(_(colname), colsize, colalign)
            self.VariablesGrid.SetMainColumn(2)
        else:
            for colname, colsize, colalign in zip(GetVariablesTableColnames(),
                                                  [40, 350, 80, 100, 80, 150],
                                                  [wx.ALIGN_RIGHT, wx.ALIGN_LEFT, wx.ALIGN_RIGHT, 
                                                   wx.ALIGN_RIGHT, wx.ALIGN_LEFT, wx.ALIGN_LEFT]):
                self.VariablesGrid.AddColumn(_(colname), colsize, colalign)
            self.VariablesGrid.SetMainColumn(1)
    
    def RefreshView(self):
        entries = self.Controler.GetSlaveVariables(self.CurrentFilter)
        self.RefreshVariablesGrid(entries)
    
    def RefreshVariablesGrid(self, entries):
        root = self.VariablesGrid.GetRootItem()
        if not root.IsOk():
            root = self.VariablesGrid.AddRoot(_("Slave entries"))
        self.GenerateVariablesGridBranch(root, entries, GetVariablesTableColnames(self.PositionColumn))
        self.VariablesGrid.Expand(root)
        
    def GenerateVariablesGridBranch(self, root, entries, colnames, idx=0):
        item, root_cookie = self.VariablesGrid.GetFirstChild(root)
        
        no_more_items = not item.IsOk()
        for entry in entries:
            idx += 1
            if no_more_items:
                item = self.VariablesGrid.AppendItem(root, "")
            for col, colname in enumerate(colnames):
                if col == 0:
                    self.VariablesGrid.SetItemText(item, str(idx), 0)
                else:
                    value = entry.get(colname, "")
                    if colname == "Access":
                        value = GetAccessValue(value, entry.get("PDOMapping", ""))
                    self.VariablesGrid.SetItemText(item, value, col)
            if entry["PDOMapping"] == "":
                self.VariablesGrid.SetItemBackgroundColour(item, wx.LIGHT_GREY)
            else:
                self.VariablesGrid.SetItemBackgroundColour(item, wx.WHITE)
            self.VariablesGrid.SetItemPyData(item, entry)
            idx = self.GenerateVariablesGridBranch(item, entry["children"], colnames, idx)
            if not no_more_items:
                item, root_cookie = self.VariablesGrid.GetNextChild(root, root_cookie)
                no_more_items = not item.IsOk()
        
        if not no_more_items:
            to_delete = []
            while item.IsOk():
                to_delete.append(item)
                item, root_cookie = self.VariablesGrid.GetNextChild(root, root_cookie)
            for item in to_delete:
                self.VariablesGrid.Delete(item)
        
        return idx
    
    def OnVariablesFilterChanged(self, event):
        filter = self.VariablesFilter.GetSelection()
        if filter != -1:
            self.CurrentFilter = self.Filters[filter]
            self.RefreshView()
        else:
            try:
                value = self.VariablesFilter.GetValue()
                if value == "":
                    self.CurrentFilter = self.Filters[0]
                    self.VariablesFilter.SetSelection(0)
                else:
                    result = ETHERCAT_INDEX_MODEL.match(value)
                    if result is not None:
                        value = result.group(1)
                    index = int(value, 16)
                    self.CurrentFilter = (index, index)
                    self.VariablesFilter.SetValue(VARIABLE_INDEX_FILTER_FORMAT % index)
                self.RefreshView()
            except:
                if self.CurrentFilter in self.Filters:
                    self.VariablesFilter.SetSelection(self.Filters.index(self.CurrentFilter))
                else:
                    self.VariablesFilter.SetValue(VARIABLE_INDEX_FILTER_FORMAT % self.CurrentFilter[0])
        self.VariablesFilterFirstCharacter = True
        event.Skip()
    
    def OnVariablesFilterKeyDown(self, event):
        if self.VariablesFilterFirstCharacter:
            keycode = event.GetKeyCode()
            if keycode not in [wx.WXK_RETURN, 
                               wx.WXK_NUMPAD_ENTER]:
                self.VariablesFilterFirstCharacter = False
                if keycode not in NAVIGATION_KEYS:
                    self.VariablesFilter.SetValue("")
            if keycode not in [wx.WXK_DELETE, 
                               wx.WXK_NUMPAD_DELETE, 
                               wx.WXK_BACK]:
                event.Skip()
        else:
            event.Skip()
    
    def OnVariablesGridLeftClick(self, event):
        item, flags, col = self.VariablesGrid.HitTest(event.GetPosition())
        if item.IsOk():
            entry = self.VariablesGrid.GetItemPyData(item)
            data_type = entry.get("Type", "")
            data_size = self.Controler.GetSizeOfType(data_type)
            
            if col == -1 and data_size is not None:
                pdo_mapping = entry.get("PDOMapping", "")
                access = entry.get("Access", "")
                entry_index = self.Controler.ExtractHexDecValue(entry.get("Index", "0"))
                entry_subindex = self.Controler.ExtractHexDecValue(entry.get("SubIndex", "0"))
                location = self.Controler.GetCurrentLocation()
                if self.PositionColumn:
                    slave_pos = self.Controler.ExtractHexDecValue(entry.get("Position", "0"))
                    location += (slave_pos,)
                    node_name = self.Controler.GetSlaveName(slave_pos)
                else:
                    node_name = self.Controler.CTNName()
                
                if pdo_mapping != "":
                    var_name = "%s_%4.4x_%2.2x" % (node_name, entry_index, entry_subindex)
                    if pdo_mapping == "T":
                        dir = "%I"
                    else:
                        dir = "%Q"
                    location = "%s%s" % (dir, data_size) + \
                               ".".join(map(lambda x:str(x), location + (entry_index, entry_subindex)))
                    
                    data = wx.TextDataObject(str((location, "location", data_type, var_name, "", access)))
                    dragSource = wx.DropSource(self.VariablesGrid)
                    dragSource.SetData(data)
                    dragSource.DoDragDrop()
                    return
                
                elif self.PositionColumn:
                    location = self.Controler.GetCurrentLocation() +\
                               (slave_pos, entry_index, entry_subindex)
                    data = wx.TextDataObject(str((location, "variable", access)))
                    dragSource = wx.DropSource(self.VariablesGrid)
                    dragSource.SetData(data)
                    dragSource.DoDragDrop()
                    return
        
        event.Skip()

class NodeEditor(ConfTreeNodeEditor):
    
    CONFNODEEDITOR_TABS = [
        (_("Ethercat node"), "_create_EthercatNodeEditor")]
    
    def _create_EthercatNodeEditor(self, prnt):
        self.EthercatNodeEditor = wx.Panel(prnt, style=wx.TAB_TRAVERSAL)
        
        main_sizer = wx.FlexGridSizer(cols=1, hgap=0, rows=2, vgap=5)
        main_sizer.AddGrowableCol(0)
        main_sizer.AddGrowableRow(1)
        
        variables_label = wx.StaticText(self.EthercatNodeEditor,
              label=_('Variable entries:'))
        main_sizer.AddWindow(variables_label, border=10, flag=wx.TOP|wx.LEFT|wx.RIGHT)
        
        self.NodeVariables = NodeVariablesSizer(self.EthercatNodeEditor, self.Controler)
        main_sizer.AddSizer(self.NodeVariables, border=10, 
            flag=wx.GROW|wx.BOTTOM|wx.LEFT|wx.RIGHT)
                
        self.EthercatNodeEditor.SetSizer(main_sizer)

        return self.EthercatNodeEditor
    
    def __init__(self, parent, controler, window):
        ConfTreeNodeEditor.__init__(self, parent, controler, window)
        
    def GetBufferState(self):
        return False, False
        
    def RefreshView(self):
        ConfTreeNodeEditor.RefreshView(self)
    
        self.NodeVariables.RefreshView()

CIA402NodeEditor = NodeEditor

def GetProcessVariablesTableColnames():
    _ = lambda x : x
    return ["#", _("Name"), 
            _("Read from (nodeid, index, subindex)"), 
            _("Write to (nodeid, index, subindex)"),
            _("Description")]

class ProcessVariablesTable(CustomTable):
    
    def GetValue(self, row, col):
        if row < self.GetNumberRows():
            if col == 0:
                return row + 1
            colname = self.GetColLabelValue(col, False)
            if colname.startswith("Read from"):
                value = self.data[row].get("ReadFrom", "")
                if value == "":
                    return value
                return "%d, #x%0.4X, #x%0.2X" % value
            elif colname.startswith("Write to"):
                value = self.data[row].get("WriteTo", "")
                if value == "":
                    return value
                return "%d, #x%0.4X, #x%0.2X" % value
            return self.data[row].get(colname, "")
    
    def SetValue(self, row, col, value):
        if col < len(self.colnames):
            colname = self.GetColLabelValue(col, False)
            if colname.startswith("Read from"):
                self.data[row]["ReadFrom"] = value
            elif colname.startswith("Write to"):
                self.data[row]["WriteTo"] = value
            else:
                self.data[row][colname] = value
    
    def _updateColAttrs(self, grid):
        """
        wx.grid.Grid -> update the column attributes to add the
        appropriate renderer given the column name.

        Otherwise default to the default renderer.
        """
        for row in range(self.GetNumberRows()):
            for col in range(self.GetNumberCols()):
                editor = None
                renderer = None
                colname = self.GetColLabelValue(col, False)
                if colname in ["Name", "Description"]:
                    editor = wx.grid.GridCellTextEditor()
                    renderer = wx.grid.GridCellStringRenderer()
                    grid.SetReadOnly(row, col, False)
                else:
                    grid.SetReadOnly(row, col, True)
                
                grid.SetCellEditor(row, col, editor)
                grid.SetCellRenderer(row, col, renderer)
                
            self.ResizeRow(grid, row)

class ProcessVariableDropTarget(wx.TextDropTarget):
    
    def __init__(self, parent):
        wx.TextDropTarget.__init__(self)
        self.ParentWindow = parent
    
    def OnDropText(self, x, y, data):
        self.ParentWindow.Select()
        x, y = self.ParentWindow.ProcessVariablesGrid.CalcUnscrolledPosition(x, y)
        col = self.ParentWindow.ProcessVariablesGrid.XToCol(x)
        row = self.ParentWindow.ProcessVariablesGrid.YToRow(y - self.ParentWindow.ProcessVariablesGrid.GetColLabelSize())
        message = None
        try:
            values = eval(data)
        except:
            message = _("Invalid value \"%s\" for process variable")%data
            values = None
        if not isinstance(values, TupleType):
            message = _("Invalid value \"%s\" for process variable")%data
            values = None
        if values is not None and col != wx.NOT_FOUND and row != wx.NOT_FOUND and 2 <= col <= 3:
            location = None
            if values[1] == "location":
                result = LOCATION_MODEL.match(values[0])
                if result is not None:
                    location = map(int, result.group(1).split('.'))
                master_location = self.ParentWindow.GetMasterLocation()
                if (master_location == tuple(location[:len(master_location)]) and 
                    len(location) - len(master_location) == 3):
                    values = tuple(location[len(master_location):])
                    var_type = self.ParentWindow.Controler.GetSlaveVariableDataType(*values)
                    if col == 2:
                        other_values = self.ParentWindow.ProcessVariablesTable.GetValueByName(row, "WriteTo")
                    else:
                        other_values = self.ParentWindow.ProcessVariablesTable.GetValueByName(row, "ReadFrom")
                    if other_values != "":
                        other_type = self.ParentWindow.Controler.GetSlaveVariableDataType(*other_values)
                    else:
                        other_type = None
                    if other_type is None or var_type == other_type:
                        if col == 2:
                            self.ParentWindow.ProcessVariablesTable.SetValueByName(row, "ReadFrom", values)
                        else:
                            self.ParentWindow.ProcessVariablesTable.SetValueByName(row, "WriteTo", values)
                        self.ParentWindow.SaveProcessVariables()
                        self.ParentWindow.RefreshProcessVariables()
                    else:
                        message = _("'Read from' and 'Write to' variables types are not compatible")
                else:
                    message = _("Invalid value \"%s\" for process variable")%data
                    
        if message is not None:
            wx.CallAfter(self.ShowMessage, message)
    
    def ShowMessage(self, message):
        message = wx.MessageDialog(self.ParentWindow, message, _("Error"), wx.OK|wx.ICON_ERROR)
        message.ShowModal()
        message.Destroy()

def GetStartupCommandsTableColnames():
    _ = lambda x : x
    return [_("Position"), _("Index"), _("Subindex"), _("Value"), _("Description")]

class StartupCommandDropTarget(wx.TextDropTarget):
    
    def __init__(self, parent):
        wx.TextDropTarget.__init__(self)
        self.ParentWindow = parent
    
    def OnDropText(self, x, y, data):
        self.ParentWindow.Select()
        message = None
        try:
            values = eval(data)
        except:
            message = _("Invalid value \"%s\" for startup command")%data
            values = None
        if not isinstance(values, TupleType):
            message = _("Invalid value \"%s\" for startup command")%data
            values = None
        if values is not None:
            location = None
            if values[1] == "location":
                result = LOCATION_MODEL.match(values[0])
                if result is not None and len(values) > 5:
                    location = map(int, result.group(1).split('.'))
                    access = values[5]
            elif values[1] == "variable":
                location = values[0]
                access = values[2]
            if location is not None:
                master_location = self.ParentWindow.GetMasterLocation()
                if (master_location == tuple(location[:len(master_location)]) and 
                    len(location) - len(master_location) == 3):
                    if access in ["wo", "rw"]:
                        self.ParentWindow.AddStartupCommand(*location[len(master_location):])
                    else:
                        message = _("Entry can't be write through SDO")
                else:
                    message = _("Invalid value \"%s\" for startup command")%data
                    
        if message is not None:
            wx.CallAfter(self.ShowMessage, message)
    
    def ShowMessage(self, message):
        message = wx.MessageDialog(self.ParentWindow, message, _("Error"), wx.OK|wx.ICON_ERROR)
        message.ShowModal()
        message.Destroy()

class StartupCommandsTable(CustomTable):

    """
    A custom wx.grid.Grid Table using user supplied data
    """
    def __init__(self, parent, data, colnames):
        # The base class must be initialized *first*
        CustomTable.__init__(self, parent, data, colnames)
        self.old_value = None

    def GetValue(self, row, col):
        if row < self.GetNumberRows():
            colname = self.GetColLabelValue(col, False)
            value = self.data[row].get(colname, "")
            if colname == "Index":
                return "#x%0.4X" % value
            elif colname == "Subindex":
                return "#x%0.2X" % value
            return value
    
    def SetValue(self, row, col, value):
        if col < len(self.colnames):
            colname = self.GetColLabelValue(col, False)
            if colname in ["Index", "Subindex"]:
                if colname == "Index":
                    result = ETHERCAT_INDEX_MODEL.match(value)
                else:
                    result = ETHERCAT_SUBINDEX_MODEL.match(value)
                if result is None:
                    return
                value = int(result.group(1), 16)
            elif colname == "Value":
                value = int(value)
            elif colname == "Position":
                self.old_value = self.data[row][colname]
                value = int(value)
            self.data[row][colname] = value
    
    def GetOldValue(self):
        return self.old_value
    
    def _updateColAttrs(self, grid):
        """
        wx.grid.Grid -> update the column attributes to add the
        appropriate renderer given the column name.

        Otherwise default to the default renderer.
        """
        for row in range(self.GetNumberRows()):
            for col in range(self.GetNumberCols()):
                editor = None
                renderer = None
                colname = self.GetColLabelValue(col, False)
                if colname in ["Position", "Value"]:
                    editor = wx.grid.GridCellNumberEditor()
                    renderer = wx.grid.GridCellNumberRenderer()
                else:
                    editor = wx.grid.GridCellTextEditor()
                    renderer = wx.grid.GridCellStringRenderer()
                
                grid.SetCellEditor(row, col, editor)
                grid.SetCellRenderer(row, col, renderer)
                grid.SetReadOnly(row, col, False)
                
            self.ResizeRow(grid, row)
    
    def GetCommandIndex(self, position, command_idx):
        for row, command in enumerate(self.data):
            if command["Position"] == position and command["command_idx"] == command_idx:
                return row
        return None

class MasterNodesVariablesSizer(NodeVariablesSizer):
    
    def __init__(self, parent, controler):
        NodeVariablesSizer.__init__(self, parent, controler, True)
        
        self.CurrentNodesFilter = {}
    
    def SetCurrentNodesFilter(self, nodes_filter):
        self.CurrentNodesFilter = nodes_filter
        
    def RefreshView(self):
        if self.CurrentNodesFilter is not None:
            args = self.CurrentNodesFilter.copy()
            args["limits"] = self.CurrentFilter
            entries = self.Controler.GetNodesVariables(**args)
            self.RefreshVariablesGrid(entries)

NODE_POSITION_FILTER_FORMAT = _("Node Position: %d")

class MasterEditor(ConfTreeNodeEditor):
    
    CONFNODEEDITOR_TABS = [
        (_("Network"), "_create_EthercatMasterEditor")]
    
    def _create_EthercatMasterEditor(self, prnt):
        self.EthercatMasterEditor = wx.ScrolledWindow(prnt, 
            style=wx.TAB_TRAVERSAL|wx.HSCROLL|wx.VSCROLL)
        self.EthercatMasterEditor.Bind(wx.EVT_SIZE, self.OnResize)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.NodesFilter = wx.ComboBox(self.EthercatMasterEditor,
            style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_COMBOBOX, self.OnNodesFilterChanged, self.NodesFilter)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnNodesFilterChanged, self.NodesFilter)
        self.NodesFilter.Bind(wx.EVT_CHAR, self.OnNodesFilterKeyDown)
        
        process_variables_header = wx.BoxSizer(wx.HORIZONTAL)
        
        process_variables_label = wx.StaticText(self.EthercatMasterEditor,
              label=_("Process variables mapped between nodes:"))
        process_variables_header.AddWindow(process_variables_label, 1,
              flag=wx.ALIGN_CENTER_VERTICAL)
        
        for name, bitmap, help in [
                ("AddVariableButton", "add_element", _("Add process variable")),
                ("DeleteVariableButton", "remove_element", _("Remove process variable")),
                ("UpVariableButton", "up", _("Move process variable up")),
                ("DownVariableButton", "down", _("Move process variable down"))]:
            button = wx.lib.buttons.GenBitmapButton(self.EthercatMasterEditor, bitmap=GetBitmap(bitmap), 
                  size=wx.Size(28, 28), style=wx.NO_BORDER)
            button.SetToolTipString(help)
            setattr(self, name, button)
            process_variables_header.AddWindow(button, border=5, flag=wx.LEFT)
        
        self.ProcessVariablesGrid = CustomGrid(self.EthercatMasterEditor, style=wx.VSCROLL)
        self.ProcessVariablesGrid.SetMinSize(wx.Size(0, 150))
        self.ProcessVariablesGrid.SetDropTarget(ProcessVariableDropTarget(self))
        self.ProcessVariablesGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, 
              self.OnProcessVariablesGridCellChange)
        self.ProcessVariablesGrid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, 
              self.OnProcessVariablesGridCellLeftClick)
        self.ProcessVariablesGrid.Bind(wx.EVT_KEY_DOWN, self.OnProcessVariablesGridKeyDown)
        
        startup_commands_header = wx.BoxSizer(wx.HORIZONTAL)
        
        startup_commands_label = wx.StaticText(self.EthercatMasterEditor,
              label=_("Startup service variables assignments:"))
        startup_commands_header.AddWindow(startup_commands_label, 1,
              flag=wx.ALIGN_CENTER_VERTICAL)
        
        for name, bitmap, help in [
                ("AddCommandButton", "add_element", _("Add startup service variable")),
                ("DeleteCommandButton", "remove_element", _("Remove startup service variable"))]:
            button = wx.lib.buttons.GenBitmapButton(self.EthercatMasterEditor, bitmap=GetBitmap(bitmap), 
                  size=wx.Size(28, 28), style=wx.NO_BORDER)
            button.SetToolTipString(help)
            setattr(self, name, button)
            startup_commands_header.AddWindow(button, border=5, flag=wx.LEFT)
        
        self.StartupCommandsGrid = CustomGrid(self.EthercatMasterEditor, style=wx.VSCROLL)
        self.StartupCommandsGrid.SetDropTarget(StartupCommandDropTarget(self))
        self.StartupCommandsGrid.SetMinSize(wx.Size(0, 150))
        self.StartupCommandsGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, 
              self.OnStartupCommandsGridCellChange)
        self.StartupCommandsGrid.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN, 
              self.OnStartupCommandsGridEditorShow)
        
        second_staticbox = wx.StaticBox(self.EthercatMasterEditor, label=_("Nodes variables filter:"))
        second_staticbox_sizer = wx.StaticBoxSizer(second_staticbox, wx.VERTICAL)
        
        self.NodesVariables = MasterNodesVariablesSizer(self.EthercatMasterEditor, self.Controler)
        second_staticbox_sizer.AddSizer(self.NodesVariables, 1, border=5, flag=wx.GROW|wx.ALL)
        
        main_staticbox = wx.StaticBox(self.EthercatMasterEditor, label=_("Node filter:"))
        staticbox_sizer = wx.StaticBoxSizer(main_staticbox, wx.VERTICAL)
        main_sizer.AddSizer(staticbox_sizer, 0, border=10, flag=wx.GROW|wx.ALL)
        main_staticbox_sizer = wx.FlexGridSizer(cols=1, hgap=0, rows=6, vgap=0)
        main_staticbox_sizer.AddGrowableCol(0)
        main_staticbox_sizer.AddGrowableRow(2)
        main_staticbox_sizer.AddGrowableRow(4)
        main_staticbox_sizer.AddGrowableRow(5)
        staticbox_sizer.AddSizer(main_staticbox_sizer, 1, flag=wx.GROW)
        main_staticbox_sizer.AddWindow(self.NodesFilter, border=5, flag=wx.GROW|wx.ALL)
        main_staticbox_sizer.AddSizer(process_variables_header, border=5, 
              flag=wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM)
        main_staticbox_sizer.AddWindow(self.ProcessVariablesGrid, 1, 
              border=5, flag=wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM)
        main_staticbox_sizer.AddSizer(startup_commands_header, 
              border=5, flag=wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM)
        main_staticbox_sizer.AddWindow(self.StartupCommandsGrid, 1, 
              border=5, flag=wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM)
        main_staticbox_sizer.AddSizer(second_staticbox_sizer, 1, 
            border=5, flag=wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM)
        
        self.EthercatMasterEditor.SetSizer(main_sizer)
        
        return self.EthercatMasterEditor

    def __init__(self, parent, controler, window):
        ConfTreeNodeEditor.__init__(self, parent, controler, window)
        
        self.ProcessVariables = []
        self.CellShown = None
        self.NodesFilterFirstCharacter = True
        
        self.ProcessVariablesDefaultValue = {"Name": "", "ReadFrom": "", "WriteTo": "", "Description": ""}
        self.ProcessVariablesTable = ProcessVariablesTable(self, [], GetProcessVariablesTableColnames())
        self.ProcessVariablesColSizes = [40, 100, 150, 150, 200]
        self.ProcessVariablesColAlignements = [wx.ALIGN_CENTER, wx.ALIGN_LEFT, wx.ALIGN_LEFT, wx.ALIGN_LEFT, wx.ALIGN_LEFT]
        
        self.ProcessVariablesGrid.SetTable(self.ProcessVariablesTable)
        self.ProcessVariablesGrid.SetButtons({"Add": self.AddVariableButton,
                                              "Delete": self.DeleteVariableButton,
                                              "Up": self.UpVariableButton,
                                              "Down": self.DownVariableButton})
        
        def _AddVariablesElement(new_row):
            self.ProcessVariablesTable.InsertRow(new_row, self.ProcessVariablesDefaultValue.copy())
            self.SaveProcessVariables()
            self.ProcessVariablesTable.ResetView(self.ProcessVariablesGrid)
            return new_row
        setattr(self.ProcessVariablesGrid, "_AddRow", _AddVariablesElement)
        
        def _DeleteVariablesElement(row):
            self.ProcessVariablesTable.RemoveRow(row)
            self.SaveProcessVariables()
            self.ProcessVariablesTable.ResetView(self.ProcessVariablesGrid)
        setattr(self.ProcessVariablesGrid, "_DeleteRow", _DeleteVariablesElement)
            
        def _MoveVariablesElement(row, move):
            new_row = self.ProcessVariablesTable.MoveRow(row, move)
            if new_row != row:
                self.SaveProcessVariables()
                self.ProcessVariablesTable.ResetView(self.ProcessVariablesGrid)
            return new_row
        setattr(self.ProcessVariablesGrid, "_MoveRow", _MoveVariablesElement)
        
        _refresh_buttons = getattr(self.ProcessVariablesGrid, "RefreshButtons")
        def _RefreshButtons():
            if self.NodesFilter.GetSelection() == 0:
                _refresh_buttons()
            else:
                self.AddVariableButton.Enable(False)
                self.DeleteVariableButton.Enable(False)
                self.UpVariableButton.Enable(False)
                self.DownVariableButton.Enable(False)
        setattr(self.ProcessVariablesGrid, "RefreshButtons", _RefreshButtons)
        
        self.ProcessVariablesGrid.SetRowLabelSize(0)
        for col in range(self.ProcessVariablesTable.GetNumberCols()):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(self.ProcessVariablesColAlignements[col], wx.ALIGN_CENTRE)
            self.ProcessVariablesGrid.SetColAttr(col, attr)
            self.ProcessVariablesGrid.SetColMinimalWidth(col, self.ProcessVariablesColSizes[col])
            self.ProcessVariablesGrid.AutoSizeColumn(col, False)
        self.ProcessVariablesGrid.RefreshButtons()
    
        self.StartupCommandsDefaultValue = {"Position": 0, "Index": 0, "Subindex": 0, "Value": 0, "Description": ""}
        self.StartupCommandsTable = StartupCommandsTable(self, [], GetStartupCommandsTableColnames())
        self.StartupCommandsColSizes = [100, 100, 50, 100, 200]
        self.StartupCommandsColAlignements = [wx.ALIGN_CENTER, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT, wx.ALIGN_LEFT]
        
        self.StartupCommandsGrid.SetTable(self.StartupCommandsTable)
        self.StartupCommandsGrid.SetButtons({"Add": self.AddCommandButton,
                                             "Delete": self.DeleteCommandButton})
        
        def _AddCommandsElement(new_row):
            command = self.StartupCommandsDefaultValue.copy()
            command_idx = self.Controler.AppendStartupCommand(command)
            self.RefreshStartupCommands()
            self.RefreshBuffer()
            return self.StartupCommandsTable.GetCommandIndex(command["Position"], command_idx)
        setattr(self.StartupCommandsGrid, "_AddRow", _AddCommandsElement)
        
        def _DeleteCommandsElement(row):
            command = self.StartupCommandsTable.GetRow(row)
            self.Controler.RemoveStartupCommand(command["Position"], command["command_idx"])
            self.RefreshStartupCommands()
            self.RefreshBuffer()
        setattr(self.StartupCommandsGrid, "_DeleteRow", _DeleteCommandsElement)
        
        self.StartupCommandsGrid.SetRowLabelSize(0)
        for col in range(self.StartupCommandsTable.GetNumberCols()):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(self.StartupCommandsColAlignements[col], wx.ALIGN_CENTRE)
            self.StartupCommandsGrid.SetColAttr(col, attr)
            self.StartupCommandsGrid.SetColMinimalWidth(col, self.StartupCommandsColSizes[col])
            self.StartupCommandsGrid.AutoSizeColumn(col, False)
        self.StartupCommandsGrid.RefreshButtons()
    
    def RefreshBuffer(self):
        self.ParentWindow.RefreshTitle()
        self.ParentWindow.RefreshFileMenu()
        self.ParentWindow.RefreshEditMenu()
        self.ParentWindow.RefreshPageTitles()
    
    def GetBufferState(self):
        return self.Controler.GetBufferState()
    
    def Undo(self):
        self.Controler.LoadPrevious()
        self.RefreshView()
            
    def Redo(self):
        self.Controler.LoadNext()
        self.RefreshView()
    
    def RefreshView(self):
        ConfTreeNodeEditor.RefreshView(self)
        
        self.RefreshNodesFilter()
        self.RefreshProcessVariables()
        self.RefreshStartupCommands()
        self.NodesVariables.RefreshView()
    
    def RefreshNodesFilter(self):
        value = self.NodesFilter.GetValue()
        self.NodesFilter.Clear()
        self.NodesFilter.Append(_("All"))
        self.NodesFilterValues = [{}]
        for vendor_id, vendor_name in self.Controler.GetLibraryVendors():
            self.NodesFilter.Append(_("%s's nodes") % vendor_name)
            self.NodesFilterValues.append({"vendor": vendor_id})
        self.NodesFilter.Append(_("CIA402 nodes"))
        self.NodesFilterValues.append({"slave_profile": 402})
        if value in self.NodesFilter.GetStrings():
            self.NodesFilter.SetStringSelection(value)
        else:
            try:
                int(value)
                self.NodesFilter.SetValue(value)
            except:
                self.NodesFilter.SetSelection(0)
        self.RefreshCurrentNodesFilter()
    
    def RefreshCurrentNodesFilter(self):
        filter = self.NodesFilter.GetSelection()
        if filter != -1:
            self.CurrentNodesFilter = self.NodesFilterValues[filter]
        else:
            try:
                value = self.NodesFilter.GetValue()
                if value == "":
                    self.CurrentNodesFilter = self.NodesFilterValues[0]
                    self.NodesFilter.SetSelection(0)
                else:
                    position = int(self.NodesFilter.GetValue())
                    self.CurrentNodesFilter = {"slave_pos": position}
                    self.NodesFilter.SetValue(NODE_POSITION_FILTER_FORMAT % position)
            except:
                if self.CurrentNodesFilter in self.NodesFilterValues:
                    self.NodesFilter.SetSelection(self.NodesFilterValues.index(self.CurrentNodesFilter))
                else:
                    self.NodesFilter.SetValue(NODE_POSITION_FILTER_FORMAT % self.CurrentNodesFilter["slave_pos"])
        self.NodesFilterFirstCharacter = True
        self.NodesVariables.SetCurrentNodesFilter(self.CurrentNodesFilter)
    
    def RefreshProcessVariables(self):
        if self.CurrentNodesFilter is not None:
            self.ProcessVariables = self.Controler.GetProcessVariables()
            slaves = self.Controler.GetSlaves(**self.CurrentNodesFilter)
            data = []
            for variable in self.ProcessVariables:
                if (variable["ReadFrom"] == "" or variable["ReadFrom"][0] in slaves or
                    variable["WriteTo"] == "" or variable["WriteTo"][0] in slaves):
                    data.append(variable)
            self.ProcessVariablesTable.SetData(data)
            self.ProcessVariablesTable.ResetView(self.ProcessVariablesGrid)
            self.ProcessVariablesGrid.RefreshButtons()
    
    def SaveProcessVariables(self):
        if self.CurrentNodesFilter is not None:
            if len(self.CurrentNodesFilter) > 0:
                self.Controler.SetProcessVariables(self.ProcessVariables)
            else:
                self.Controler.SetProcessVariables(self.ProcessVariablesTable.GetData())
            self.RefreshBuffer()
    
    def RefreshStartupCommands(self, position=None, command_idx=None):
        if self.CurrentNodesFilter is not None:
            self.StartupCommandsTable.SetData(
                self.Controler.GetStartupCommands(**self.CurrentNodesFilter))
            self.StartupCommandsTable.ResetView(self.StartupCommandsGrid)
            if position is not None and command_idx is not None:
                wx.CallAfter(self.SelectStartupCommand, position, command_idx)
    
    def SelectStartupCommand(self, position, command_idx):
        self.StartupCommandsGrid.SetSelectedRow(
            self.StartupCommandsTable.GetCommandIndex(position, command_idx))
    
    def GetMasterLocation(self):
        return self.Controler.GetCurrentLocation()
    
    def AddStartupCommand(self, position, index, subindex):
        command = self.StartupCommandsDefaultValue.copy()
        command["Position"] = position
        command["Index"] = index
        command["Subindex"] = subindex
        command_idx = self.Controler.AppendStartupCommand(command)
        self.RefreshStartupCommands()
        self.RefreshBuffer()
        self.StartupCommandsGrid.SetSelectedRow(
            self.StartupCommandsTable.GetCommandIndex(position, command_idx))
    
    def OnNodesFilterChanged(self, event):
        self.RefreshCurrentNodesFilter()
        if self.CurrentNodesFilter is not None:
            self.RefreshProcessVariables()
            self.RefreshStartupCommands()
            self.NodesVariables.RefreshView()
        event.Skip()
    
    def OnNodesFilterKeyDown(self, event):
        if self.NodesFilterFirstCharacter:
            keycode = event.GetKeyCode()
            if keycode not in [wx.WXK_RETURN, 
                               wx.WXK_NUMPAD_ENTER]:
                self.NodesFilterFirstCharacter = False
                if keycode not in NAVIGATION_KEYS:
                    self.NodesFilter.SetValue("")
            if keycode not in [wx.WXK_DELETE, 
                               wx.WXK_NUMPAD_DELETE, 
                               wx.WXK_BACK]:
                event.Skip()
        else:
            event.Skip()
    
    def OnProcessVariablesGridCellChange(self, event):
        row, col = event.GetRow(), event.GetCol()
        colname = self.ProcessVariablesTable.GetColLabelValue(col, False)
        value = self.ProcessVariablesTable.GetValue(row, col)
        message = None
        if colname == "Name":
            if not TestIdentifier(value):
                message = _("\"%s\" is not a valid identifier!") % value
            elif value.upper() in IEC_KEYWORDS:
                message = _("\"%s\" is a keyword. It can't be used!") % value
            elif value.upper() in [var["Name"].upper() for idx, var in enumerate(self.ProcessVariablesTable.GetData()) if idx != row]:
                message = _("An variable named \"%s\" already exists!") % value
        if message is None:
            self.SaveProcessVariables()
            wx.CallAfter(self.ProcessVariablesTable.ResetView, self.ProcessVariablesGrid)
            event.Skip()
        else:
            dialog = wx.MessageDialog(self, message, _("Error"), wx.OK|wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()
            event.Veto()
    
    def OnProcessVariablesGridCellLeftClick(self, event):
        row = event.GetRow()
        if event.GetCol() == 0:
            var_name = self.ProcessVariablesTable.GetValueByName(row, "Name")
            var_type = self.Controler.GetSlaveVariableDataType(
                *self.ProcessVariablesTable.GetValueByName(row, "ReadFrom"))
            data_size = self.Controler.GetSizeOfType(var_type)
            number = self.ProcessVariablesTable.GetValueByName(row, "Number")
            location = "%%M%s" % data_size + \
                       ".".join(map(lambda x:str(x), self.Controler.GetCurrentLocation() + (number,)))
            
            data = wx.TextDataObject(str((location, "location", var_type, var_name, "")))
            dragSource = wx.DropSource(self.ProcessVariablesGrid)
            dragSource.SetData(data)
            dragSource.DoDragDrop()
        event.Skip()
    
    def OnProcessVariablesGridKeyDown(self, event):
        keycode = event.GetKeyCode()
        col = self.ProcessVariablesGrid.GetGridCursorCol()
        row = self.ProcessVariablesGrid.GetGridCursorRow()
        colname = self.ProcessVariablesTable.GetColLabelValue(col, False)
        if (keycode in (wx.WXK_DELETE, wx.WXK_NUMPAD_DELETE) and 
            (colname.startswith("Read from") or colname.startswith("Write to"))):
            self.ProcessVariablesTable.SetValue(row, col, "")
            self.SaveProcessVariables()
            wx.CallAfter(self.ProcessVariablesTable.ResetView, self.ProcessVariablesGrid)
        else:
            event.Skip()
    
    def OnStartupCommandsGridEditorShow(self, event):
        self.CellShown = event.GetRow(), event.GetCol()
        event.Skip()
    
    def OnStartupCommandsGridCellChange(self, event):
        row, col = event.GetRow(), event.GetCol()
        if self.CellShown == (row, col):
            self.CellShown = None
            colname = self.StartupCommandsTable.GetColLabelValue(col, False)
            value = self.StartupCommandsTable.GetValue(row, col)
            message = None
            if colname == "Position":
                if value not in self.Controler.GetSlaves():
                    message = _("No slave defined at position %d!") % value
                old_value = self.StartupCommandsTable.GetOldValue()
                command = self.StartupCommandsTable.GetRow(row)
                if message is None and old_value != command["Position"]:
                    self.Controler.RemoveStartupCommand(
                        self.StartupCommandsTable.GetOldValue(),
                        command["command_idx"], False)
                    command_idx = self.Controler.AppendStartupCommand(command)
                    wx.CallAfter(self.RefreshStartupCommands, command["Position"], command_idx)
            else:
                command = self.StartupCommandsTable.GetRow(row)
                self.Controler.SetStartupCommandInfos(command)
                if colname in ["Index", "SubIndex"]: 
                    wx.CallAfter(self.RefreshStartupCommands, command["Position"], command["command_idx"])
            if message is None:
                self.RefreshBuffer()
                event.Skip()
            else:
                dialog = wx.MessageDialog(self, message, _("Error"), wx.OK|wx.ICON_ERROR)
                dialog.ShowModal()
                dialog.Destroy()
                event.Veto()
        else:
            event.Veto()
    
    def OnResize(self, event):
        self.EthercatMasterEditor.GetBestSize()
        xstart, ystart = self.EthercatMasterEditor.GetViewStart()
        window_size = self.EthercatMasterEditor.GetClientSize()
        maxx, maxy = self.EthercatMasterEditor.GetMinSize()
        posx = max(0, min(xstart, (maxx - window_size[0]) / SCROLLBAR_UNIT))
        posy = max(0, min(ystart, (maxy - window_size[1]) / SCROLLBAR_UNIT))
        self.EthercatMasterEditor.Scroll(posx, posy)
        self.EthercatMasterEditor.SetScrollbars(SCROLLBAR_UNIT, SCROLLBAR_UNIT, 
                maxx / SCROLLBAR_UNIT, maxy / SCROLLBAR_UNIT, posx, posy)
        event.Skip()
    
def GetModulesTableColnames():
    _ = lambda x : x
    return [_("Name"), _("PDO alignment (bits)")]

class LibraryEditorSizer(wx.FlexGridSizer):
    
    def __init__(self, parent, module_library, buttons):
        wx.FlexGridSizer.__init__(self, cols=1, hgap=0, rows=4, vgap=5)
        
        self.ModuleLibrary = module_library
        self.ParentWindow = parent
        
        self.AddGrowableCol(0)
        self.AddGrowableRow(1)
        self.AddGrowableRow(3)
        
        ESI_files_label = wx.StaticText(parent, 
            label=_("ESI Files:"))
        self.AddWindow(ESI_files_label, border=10, 
            flag=wx.TOP|wx.LEFT|wx.RIGHT)
        
        folder_tree_sizer = wx.FlexGridSizer(cols=2, hgap=5, rows=1, vgap=0)
        folder_tree_sizer.AddGrowableCol(0)
        folder_tree_sizer.AddGrowableRow(0)
        self.AddSizer(folder_tree_sizer, border=10, 
            flag=wx.GROW|wx.LEFT|wx.RIGHT)
        
        self.ESIFiles = FolderTree(parent, self.GetPath(), editable=False)
        self.ESIFiles.SetFilter(".xml")
        folder_tree_sizer.AddWindow(self.ESIFiles, flag=wx.GROW)
        
        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        folder_tree_sizer.AddSizer(buttons_sizer, 
            flag=wx.ALIGN_CENTER_VERTICAL)
        
        for idx, (name, bitmap, help, callback) in enumerate(buttons):
            button = wx.lib.buttons.GenBitmapButton(parent, 
                  bitmap=GetBitmap(bitmap), 
                  size=wx.Size(28, 28), style=wx.NO_BORDER)
            button.SetToolTipString(help)
            setattr(self, name, button)
            if idx > 0:
                flag = wx.TOP
            else:
                flag = 0
            if callback is None:
                callback = getattr(self, "On" + name, None)
            if callback is not None:
                parent.Bind(wx.EVT_BUTTON, callback, button)
            buttons_sizer.AddWindow(button, border=10, flag=flag)
        
        modules_label = wx.StaticText(parent, 
            label=_("Modules library:"))
        self.AddSizer(modules_label, border=10, 
            flag=wx.LEFT|wx.RIGHT)
        
        self.ModulesGrid = wx.gizmos.TreeListCtrl(parent,
              style=wx.TR_DEFAULT_STYLE |
                    wx.TR_ROW_LINES |
                    wx.TR_COLUMN_LINES |
                    wx.TR_HIDE_ROOT |
                    wx.TR_FULL_ROW_HIGHLIGHT)
        self.ModulesGrid.GetMainWindow().Bind(wx.EVT_LEFT_DCLICK,
            self.OnModulesGridLeftDClick)
        self.AddWindow(self.ModulesGrid, border=10, 
            flag=wx.GROW|wx.BOTTOM|wx.LEFT|wx.RIGHT)
        
        for colname, colsize, colalign in zip(GetModulesTableColnames(),
                                              [400, 150],
                                              [wx.ALIGN_LEFT, wx.ALIGN_RIGHT]):
            self.ModulesGrid.AddColumn(_(colname), colsize, colalign)
        self.ModulesGrid.SetMainColumn(0)
    
    def GetPath(self):
        return self.ModuleLibrary.GetPath()
    
    def SetControlMinSize(self, size):
        self.ESIFiles.SetMinSize(size)
        self.ModulesGrid.SetMinSize(size)
        
    def GetSelectedFilePath(self):
        return self.ESIFiles.GetPath()
    
    def RefreshView(self):
        self.ESIFiles.RefreshTree()
        self.RefreshModulesGrid()
    
    def RefreshModulesGrid(self):
        root = self.ModulesGrid.GetRootItem()
        if not root.IsOk():
            root = self.ModulesGrid.AddRoot("Modules")
        self.GenerateModulesGridBranch(root, 
            self.ModuleLibrary.GetModulesLibrary(), 
            GetVariablesTableColnames())
        self.ModulesGrid.Expand(root)
            
    def GenerateModulesGridBranch(self, root, modules, colnames):
        item, root_cookie = self.ModulesGrid.GetFirstChild(root)
        
        no_more_items = not item.IsOk()
        for module in modules:
            if no_more_items:
                item = self.ModulesGrid.AppendItem(root, "")
            self.ModulesGrid.SetItemText(item, module["name"], 0)
            if module["infos"] is not None:
                self.ModulesGrid.SetItemText(item, str(module["infos"]["alignment"]), 1)
            else:
                self.ModulesGrid.SetItemBackgroundColour(item, wx.LIGHT_GREY)
            self.ModulesGrid.SetItemPyData(item, module["infos"])
            self.GenerateModulesGridBranch(item, module["children"], colnames)
            if not no_more_items:
                item, root_cookie = self.ModulesGrid.GetNextChild(root, root_cookie)
                no_more_items = not item.IsOk()
        
        if not no_more_items:
            to_delete = []
            while item.IsOk():
                to_delete.append(item)
                item, root_cookie = self.ModulesGrid.GetNextChild(root, root_cookie)
            for item in to_delete:
                self.ModulesGrid.Delete(item)
    
    def OnImportButton(self, event):
        dialog = wx.FileDialog(self.ParentWindow,
             _("Choose an XML file"), 
             os.getcwd(), "",  
             _("XML files (*.xml)|*.xml|All files|*.*"), wx.OPEN)
        
        if dialog.ShowModal() == wx.ID_OK:
            filepath = dialog.GetPath()
            if self.ModuleLibrary.ImportModuleLibrary(filepath):
                wx.CallAfter(self.RefreshView)
            else:
                message = wx.MessageDialog(self, 
                    _("No such XML file: %s\n") % filepath, 
                    _("Error"), wx.OK|wx.ICON_ERROR)
                message.ShowModal()
                message.Destroy()
        dialog.Destroy()
        
        event.Skip()
    
    def OnDeleteButton(self, event):
        filepath = self.GetSelectedFilePath()
        if os.path.isfile(filepath):
            folder, filename = os.path.split(filepath)
            
            dialog = wx.MessageDialog(self.ParentWindow, 
                  _("Do you really want to delete the file '%s'?") % filename, 
                  _("Delete File"), wx.YES_NO|wx.ICON_QUESTION)
            remove = dialog.ShowModal() == wx.ID_YES
            dialog.Destroy()
            
            if remove:
                os.remove(filepath)
                self.ModuleLibrary.LoadModules()
                wx.CallAfter(self.RefreshView)
        event.Skip()
    
    def OnModulesGridLeftDClick(self, event):
        item, flags, col = self.ModulesGrid.HitTest(event.GetPosition())
        if item.IsOk():
            entry_infos = self.ModulesGrid.GetItemPyData(item)
            if entry_infos is not None and col == 1:
                dialog = wx.TextEntryDialog(self.ParentWindow, 
                    _("Set PDO alignment (bits):"),
                    _("%s PDO alignment") % self.ModulesGrid.GetItemText(item), 
                    str(entry_infos["alignment"]))
                
                if dialog.ShowModal() == wx.ID_OK:
                    try:
                        self.ModuleLibrary.SetAlignment(
                            entry_infos["vendor"],
                            entry_infos["product_code"],
                            entry_infos["revision_number"],
                            int(dialog.GetValue()))
                        wx.CallAfter(self.RefreshModulesGrid)
                    except ValueError:
                        message = wx.MessageDialog(self, 
                            _("Module PDO alignment must be an integer!"), 
                            _("Error"), wx.OK|wx.ICON_ERROR)
                        message.ShowModal()
                        message.Destroy()
                    
                dialog.Destroy()
        
        event.Skip()

class DatabaseManagementDialog(wx.Dialog):
    
    def __init__(self, parent, database):
        wx.Dialog.__init__(self, parent,
              size=wx.Size(700, 500), title=_('ESI Files Database management'),
              style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        main_sizer = wx.FlexGridSizer(cols=1, hgap=0, rows=2, vgap=10)
        main_sizer.AddGrowableCol(0)
        main_sizer.AddGrowableRow(0)
        
        self.DatabaseSizer = LibraryEditorSizer(self, database,
            [("ImportButton", "ImportESI", _("Import file to ESI files database"), None),
             ("DeleteButton", "remove_element", _("Remove file from database"), None)])
        self.DatabaseSizer.SetControlMinSize(wx.Size(0, 0))
        main_sizer.AddSizer(self.DatabaseSizer, border=10,
            flag=wx.GROW|wx.TOP|wx.LEFT|wx.RIGHT)
        
        button_sizer = self.CreateButtonSizer(wx.OK|wx.CANCEL|wx.CENTRE)
        button_sizer.GetAffirmativeButton().SetLabel(_("Add file to project"))
        button_sizer.GetCancelButton().SetLabel(_("Close"))
        main_sizer.AddSizer(button_sizer, border=10, 
              flag=wx.ALIGN_RIGHT|wx.BOTTOM|wx.LEFT|wx.RIGHT)
        
        self.SetSizer(main_sizer)
        
        self.DatabaseSizer.RefreshView()
        
    def GetValue(self):
        return self.DatabaseSizer.GetSelectedFilePath()

class LibraryEditor(ConfTreeNodeEditor):
    
    CONFNODEEDITOR_TABS = [
        (_("Modules Library"), "_create_ModuleLibraryEditor")]
    
    def _create_ModuleLibraryEditor(self, prnt):
        self.ModuleLibraryEditor = wx.ScrolledWindow(prnt,
            style=wx.TAB_TRAVERSAL|wx.HSCROLL|wx.VSCROLL)
        self.ModuleLibraryEditor.Bind(wx.EVT_SIZE, self.OnResize)
        
        self.ModuleLibrarySizer = LibraryEditorSizer(self.ModuleLibraryEditor,
            self.Controler.GetModulesLibraryInstance(),
            [("ImportButton", "ImportESI", _("Import ESI file"), None),
             ("AddButton", "ImportDatabase", _("Add file from ESI files database"), self.OnAddButton),
             ("DeleteButton", "remove_element", _("Remove file from library"), None)])
        self.ModuleLibrarySizer.SetControlMinSize(wx.Size(0, 200))
        self.ModuleLibraryEditor.SetSizer(self.ModuleLibrarySizer)
        
        return self.ModuleLibraryEditor

    def __init__(self, parent, controler, window):
        ConfTreeNodeEditor.__init__(self, parent, controler, window)
    
        self.RefreshView()
    
    def RefreshView(self):
        ConfTreeNodeEditor.RefreshView(self)
        self.ModuleLibrarySizer.RefreshView()

    def OnAddButton(self, event):
        dialog = DatabaseManagementDialog(self, 
            self.Controler.GetModulesDatabaseInstance())
        
        if dialog.ShowModal() == wx.ID_OK:
            module_library = self.Controler.GetModulesLibraryInstance()
            module_library.ImportModuleLibrary(dialog.GetValue())
            
        dialog.Destroy()
        
        wx.CallAfter(self.ModuleLibrarySizer.RefreshView)
        
        event.Skip()

    def OnResize(self, event):
        self.ModuleLibraryEditor.GetBestSize()
        xstart, ystart = self.ModuleLibraryEditor.GetViewStart()
        window_size = self.ModuleLibraryEditor.GetClientSize()
        maxx, maxy = self.ModuleLibraryEditor.GetMinSize()
        posx = max(0, min(xstart, (maxx - window_size[0]) / SCROLLBAR_UNIT))
        posy = max(0, min(ystart, (maxy - window_size[1]) / SCROLLBAR_UNIT))
        self.ModuleLibraryEditor.Scroll(posx, posy)
        self.ModuleLibraryEditor.SetScrollbars(SCROLLBAR_UNIT, SCROLLBAR_UNIT, 
                maxx / SCROLLBAR_UNIT, maxy / SCROLLBAR_UNIT, posx, posy)
        event.Skip()
        

